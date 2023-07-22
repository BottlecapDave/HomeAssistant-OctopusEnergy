from datetime import (datetime, timedelta)
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.utils.rate_information import get_previous_rate_information

@pytest.mark.asyncio
async def test_when_target_has_no_rates_and_gmt_then_no_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-01T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = create_rate_data(period_from, period_to, [10, 10, 20, 30, 30])

  # Act
  rate_information = get_previous_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_has_no_rates_and_bst_then_no_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-02T00:00:01+01:00", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = create_rate_data(period_from, period_to, [10, 10, 20, 30, 30])

  # Act
  rate_information = get_previous_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_is_at_start_of_rates_and_bst_then_no_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-02-28T00:00:01+01:00", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = create_rate_data(period_from, period_to, [10, 10, 20, 30, 30])

  # Act
  rate_information = get_previous_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_previous_rate_is_identical_to_current_rate_then_no_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-01T00:32:01+01:00", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = create_rate_data(period_from, period_to, [10])

  # Act
  rate_information = get_previous_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_has_rates_and_gmt_then_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-02-28T01:12:00Z", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = create_rate_data(period_from, period_to, [10, 10, 20, 30, 30])
  expected_current_rate = 10
  for rate in rate_data:
    if now >= rate["valid_from"] and now <= rate["valid_to"]:
      assert expected_current_rate == rate["value_inc_vat"]

  # Act
  rate_information = get_previous_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None
  
  assert "previous_rate" in rate_information
  assert rate_information["previous_rate"]["value_inc_vat"] == 30
  assert rate_information["previous_rate"]["valid_from"] == datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["previous_rate"]["valid_to"] == datetime.strptime("2022-02-28T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert "rates" in rate_information
  assert len(rate_information["rates"]) == 2

  assert rate_information["rates"][0]["value_inc_vat"] == 30
  assert rate_information["rates"][0]["valid_from"] == datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["rates"][0]["valid_to"] == datetime.strptime("2022-02-28T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert rate_information["rates"][1]["value_inc_vat"] == 30
  assert rate_information["rates"][1]["valid_from"] == datetime.strptime("2022-02-28T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["rates"][1]["valid_to"] == datetime.strptime("2022-02-28T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
async def test_when_target_has_rates_and_bst_then_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-02T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-02-28T01:12:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = create_rate_data(period_from, period_to, [10, 10, 20, 30, 30])
  expected_current_rate = 20
  for rate in rate_data:
    if now >= rate["valid_from"] and now <= rate["valid_to"]:
      assert expected_current_rate == rate["value_inc_vat"]

  # Act
  rate_information = get_previous_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None
  
  assert "previous_rate" in rate_information
  assert rate_information["previous_rate"]["value_inc_vat"] == 10
  assert rate_information["previous_rate"]["valid_from"] == datetime.strptime("2022-02-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["previous_rate"]["valid_to"] == datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert "rates" in rate_information
  assert len(rate_information["rates"]) == 2

  assert rate_information["rates"][0]["value_inc_vat"] == 10
  assert rate_information["rates"][0]["valid_from"] == datetime.strptime("2022-02-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["rates"][0]["valid_to"] == datetime.strptime("2022-02-27T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert rate_information["rates"][1]["value_inc_vat"] == 10
  assert rate_information["rates"][1]["valid_from"] == datetime.strptime("2022-02-27T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["rates"][1]["valid_to"] == datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")