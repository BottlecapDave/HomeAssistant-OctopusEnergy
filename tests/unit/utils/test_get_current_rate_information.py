from datetime import (datetime, timedelta)
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.utils.rate_information import get_current_rate_information
from custom_components.octopus_energy.api_client import rates_to_thirty_minute_increments

@pytest.mark.asyncio
async def test_when_target_has_no_rates_and_gmt_then_no_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-01T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_price = 10
  expected_max_price = 30

  rate_data = create_rate_data(period_from, period_to, [expected_min_price, 20, 20, expected_max_price])

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_has_no_rates_and_bst_then_no_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-02T00:00:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_price = 10
  expected_max_price = 30

  rate_data = create_rate_data(period_from, period_to, [expected_min_price, 20, 20, expected_max_price])

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_has_rates_and_gmt_then_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-02-28T00:32:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_price = 10
  expected_max_price = 30
  expected_rate = 20

  rate_data = create_rate_data(period_from, period_to, [expected_min_price, expected_rate, expected_rate, expected_max_price])

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None

  assert "all_rates" in rate_information
  expected_period_from = period_from
  
  total_rate_value = 0
  min_target = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  max_target = min_target + timedelta(days=1)
  
  for index in range(len(rate_data)):
    assert rate_information["all_rates"][index]["start"] == expected_period_from
    assert rate_information["all_rates"][index]["end"] == expected_period_from + timedelta(minutes=30)

    assert rate_information["all_rates"][index]["value_inc_vat"] == round((expected_min_price if index % 4 == 0 else expected_max_price if index % 4 == 3 else expected_rate) / 100, 6)
    assert rate_information["all_rates"][index]["is_capped"] == False
    expected_period_from = expected_period_from + timedelta(minutes=30)

    if rate_data[index]["start"] >= min_target and rate_data[index]["end"] <= max_target:
      total_rate_value = total_rate_value + rate_data[index]["value_inc_vat"]

  assert "current_rate" in rate_information
  assert rate_information["current_rate"]["start"] == datetime.strptime("2022-02-28T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["current_rate"]["end"] == rate_information["current_rate"]["start"] + timedelta(minutes=60)
  assert rate_information["current_rate"]["tariff_code"] == rate_data[0]["tariff_code"]

  assert rate_information["current_rate"]["value_inc_vat"] == round(expected_rate / 100, 6)
  
  assert "min_rate_today" in rate_information
  assert rate_information["min_rate_today"] == round(expected_min_price / 100, 6)
  
  assert "max_rate_today" in rate_information
  assert rate_information["max_rate_today"] == round(expected_max_price / 100, 6)
  
  assert "average_rate_today" in rate_information
  assert rate_information["average_rate_today"] == round((total_rate_value / 48) / 100, 6)

@pytest.mark.asyncio
async def test_when_target_has_rates_and_bst_then_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-02T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-02-28T00:32:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_price = 10
  expected_max_price = 30
  expected_rate = 20

  rate_data = create_rate_data(period_from, period_to, [expected_min_price, expected_rate, expected_rate, expected_max_price])

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None

  assert "all_rates" in rate_information
  expected_period_from = period_from
  
  total_rate_value = 0
  min_target = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  max_target = min_target + timedelta(days=1)
  
  for index in range(len(rate_data)):
    assert rate_information["all_rates"][index]["start"] == expected_period_from
    assert rate_information["all_rates"][index]["end"] == expected_period_from + timedelta(minutes=30)

    assert rate_information["all_rates"][index]["value_inc_vat"] == round((expected_min_price if index % 4 == 0 else expected_max_price if index % 4 == 3 else expected_rate) / 100, 6)
    assert rate_information["all_rates"][index]["is_capped"] == False
    expected_period_from = expected_period_from + timedelta(minutes=30)

    if rate_information["all_rates"][index]["start"] >= min_target and rate_information["all_rates"][index]["end"] <= max_target:
      total_rate_value = total_rate_value + rate_data[index]["value_inc_vat"]

  assert "current_rate" in rate_information
  assert rate_information["current_rate"]["start"] == datetime.strptime("2022-02-28T00:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["current_rate"]["end"] == rate_information["current_rate"]["start"] + timedelta(minutes=60)
  assert rate_information["current_rate"]["tariff_code"] == rate_data[0]["tariff_code"]

  assert rate_information["current_rate"]["value_inc_vat"] == round(expected_rate / 100, 6)
  
  assert "min_rate_today" in rate_information
  assert rate_information["min_rate_today"] == round(expected_min_price / 100, 6)
  
  assert "max_rate_today" in rate_information
  assert rate_information["max_rate_today"] == round(expected_max_price / 100, 6)
  
  assert "average_rate_today" in rate_information
  assert rate_information["average_rate_today"] == round((total_rate_value / 48)  / 100, 6)

@pytest.mark.asyncio
async def test_when_all_rates_identical_costs_then_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-02T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-02-28T00:32:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_rate = 20

  rate_data = create_rate_data(period_from, period_to, [expected_rate])

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None

  assert "all_rates" in rate_information
  expected_period_from = period_from
  
  total_rate_value = 0
  min_target = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  max_target = min_target + timedelta(days=1)
  
  for index in range(len(rate_data)):
    assert rate_information["all_rates"][index]["start"] == expected_period_from
    assert rate_information["all_rates"][index]["end"] == expected_period_from + timedelta(minutes=30)

    assert rate_information["all_rates"][index]["value_inc_vat"] == round(expected_rate / 100, 6)
    assert rate_information["all_rates"][index]["is_capped"] == False
    expected_period_from = expected_period_from + timedelta(minutes=30)

    if rate_information["all_rates"][index]["start"] >= min_target and rate_information["all_rates"][index]["end"] <= max_target:
      total_rate_value = total_rate_value + rate_data[index]["value_inc_vat"]

  assert "current_rate" in rate_information
  assert rate_information["current_rate"]["start"] == period_from
  assert rate_information["current_rate"]["end"] == period_to
  assert rate_information["current_rate"]["tariff_code"] == rate_data[0]["tariff_code"]

  assert rate_information["current_rate"]["value_inc_vat"] == round(expected_rate / 100, 6)
  
  assert "min_rate_today" in rate_information
  assert rate_information["min_rate_today"] == round(expected_rate / 100, 6)
  
  assert "max_rate_today" in rate_information
  assert rate_information["max_rate_today"] == round(expected_rate / 100, 6)
  
  assert "average_rate_today" in rate_information
  assert rate_information["average_rate_today"] == round((total_rate_value / 48) / 100, 6)

# Covering https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/441
@pytest.mark.asyncio
@pytest.mark.parametrize("now",[
  (datetime.strptime("2023-10-06T10:50:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2023-10-06T09:50:00Z", "%Y-%m-%dT%H:%M:%S%z")),
])
async def test_when_agile_rates_then_rate_information_is_returned(now: datetime):
  # Arrange
  rate_data = rates_to_thirty_minute_increments(
    {
      "results": [
        {
          "value_inc_vat": 2.0,
          "valid_from": "2023-10-06T11:30:00Z",
          "valid_to": "2023-10-06T12:00:00Z"
        },
        {
          "value_inc_vat": 3.02,
          "valid_from": "2023-10-06T11:00:00Z",
          "valid_to": "2023-10-06T11:30:00Z"
        },
        {
          "value_inc_vat": 3.43,
          "valid_from": "2023-10-06T10:30:00Z",
          "valid_to": "2023-10-06T11:00:00Z"
        },
        {
          "value_inc_vat": 4.18,
          "valid_from": "2023-10-06T10:00:00Z",
          "valid_to": "2023-10-06T10:30:00Z"
        },
        {
          "value_inc_vat": 6.19,
          "valid_from": "2023-10-06T09:30:00Z",
          "valid_to": "2023-10-06T10:00:00Z"
        },
        {
          "value_inc_vat": 6.74,
          "valid_from": "2023-10-06T09:00:00Z",
          "valid_to": "2023-10-06T09:30:00Z"
        },
        {
          "value_inc_vat": 7.6,
          "valid_from": "2023-10-06T08:30:00Z",
          "valid_to": "2023-10-06T09:00:00Z"
        },
      ]
    },
    datetime.strptime("2023-10-06T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-10-06T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    "test"
  )
  expected_current_rate = 6.19

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None
  
  assert "current_rate" in rate_information
  assert rate_information["current_rate"]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["current_rate"]["start"] == datetime.strptime("2023-10-06T09:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["current_rate"]["end"] == datetime.strptime("2023-10-06T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["current_rate"]["tariff_code"] == rate_data[0]["tariff_code"]

  assert "applicable_rates" in rate_information
  assert len(rate_information["applicable_rates"]) == 1

  assert rate_information["applicable_rates"][0]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["applicable_rates"][0]["start"] == datetime.strptime("2023-10-06T09:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["applicable_rates"][0]["end"] == datetime.strptime("2023-10-06T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
