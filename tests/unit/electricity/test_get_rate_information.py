from datetime import (datetime, timedelta)
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.electricity import get_rate_information

@pytest.mark.asyncio
async def test_when_target_has_no_rates_then_no_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target = datetime.strptime("2022-03-01T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_price = 10
  expected_max_price = 30

  rate_data = create_rate_data(period_from, period_to, [expected_min_price, 20, expected_max_price])

  # Act
  rate_information = get_rate_information(rate_data, target)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_has_rates_then_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target = datetime.strptime("2022-02-28T10:12:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_price = 10
  expected_max_price = 30

  rate_data = create_rate_data(period_from, period_to, [expected_min_price, 20, expected_max_price])

  # Act
  rate_information = get_rate_information(rate_data, target)

  # Assert
  assert rate_information is not None

  assert "rates" in rate_information
  expected_period_from = period_from
  
  total_rate_value = 0
  min_target = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  max_target = min_target + timedelta(days=1)
  
  for index in range(len(rate_data)):
    assert rate_information["rates"][index]["from"] == expected_period_from
    assert rate_information["rates"][index]["to"] == expected_period_from + timedelta(minutes=30)

    assert rate_information["rates"][index]["rate"] == (expected_min_price if index % 3 == 0 else expected_max_price if index % 3 == 2 else 20)
    assert rate_information["rates"][index]["is_capped"] == False
    expected_period_from = expected_period_from + timedelta(minutes=30)

    if rate_information["rates"][index]["from"] >= min_target and rate_information["rates"][index]["to"] <= max_target:
      total_rate_value = total_rate_value + rate_information["rates"][index]["rate"]

  assert "current_rate" in rate_information
  assert rate_information["current_rate"]["valid_from"] == datetime.strptime("2022-02-28T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["current_rate"]["valid_to"] == rate_information["current_rate"]["valid_from"] + timedelta(minutes=30)

  assert rate_information["current_rate"]["value_inc_vat"] == expected_max_price
  assert rate_information["current_rate"]["is_capped"] == False
  
  assert "min_rate_today" in rate_information
  assert rate_information["min_rate_today"] == expected_min_price
  
  assert "max_rate_today" in rate_information
  assert rate_information["max_rate_today"] == expected_max_price
  
  assert "average_rate_today" in rate_information
  assert rate_information["average_rate_today"] == total_rate_value / 48