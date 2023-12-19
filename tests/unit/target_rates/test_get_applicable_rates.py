from datetime import datetime, timedelta
import pytest

from unit import (create_rate_data, agile_rates)
from custom_components.octopus_energy.api_client import rates_to_thirty_minute_increments
from custom_components.octopus_energy.target_rates import get_applicable_rates

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target,expected_number_of_rates",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, 16),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, 12),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, 16),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, 16),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, 16),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, 16),
  
  # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, 36),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, 12),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, 36),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, 36),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, 36),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, 36),
  
  # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, 28),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, 24),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, 28),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, 28),
  
  # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, 48),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, 24),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, 48),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, 48),
])
async def test_when_continuous_times_present_then_next_continuous_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target, expected_number_of_rates):
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2, 0.3, 0.2, 0.2, 0.1]

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )

  # Act
  result = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    is_rolling_target
  )

  assert result is not None

  assert len(result) == expected_number_of_rates
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

@pytest.mark.asyncio
async def test_when_start_time_is_after_end_time_then_rates_are_overnight():
  # Arrange
  current_date = datetime.strptime("2022-10-21T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "20:00"
  target_end_time = "09:00"

  expected_first_valid_from = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

  # Act
  result = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    agile_rates,
    False
  )

  # Assert
  assert result is not None
  assert len(result) == 26

  expected_first_valid_from = current_date.replace(hour=20, minute=0)
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

@pytest.mark.asyncio
async def test_when_start_time_and_end_time_is_same_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2022-10-21T17:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"

  expected_first_valid_from = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

  # Act
  result = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    agile_rates,
    False
  )

  # Assert
  assert result is not None
  expected_first_valid_from = current_date.replace(hour=16, minute=0)
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]


@pytest.mark.asyncio
async def test_when_start_time_is_after_end_time_and_rolling_target_then_rates_are_overnight():
  # Arrange
  current_date = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "22:00"
  target_end_time = "01:00"

  expected_first_valid_from = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

  tariff_code = "test-tariff"
  rates = rates_to_thirty_minute_increments(
    {
      "results": [
        {
          "value_exc_vat": 15.1,
          "value_inc_vat": 15.1,
          "valid_from": "2022-10-21T00:00:00Z",
          "valid_to": "2022-10-21T22:00:00Z"
        },
        {
          "value_exc_vat": 16.1,
          "value_inc_vat": 16.1,
          "valid_from": "2022-10-21T22:00:00Z",
          "valid_to": "2022-10-22T02:00:00Z"
        },
        {
          "value_exc_vat": 15.1,
          "value_inc_vat": 15.1,
          "valid_from": "2022-10-22T02:00:00Z",
          "valid_to": "2022-10-22T05:00:00Z"
        },
      ]
    },
    datetime.strptime("2022-10-21T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-24T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    tariff_code
  )

  # Act
  result = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    True
  )

  # Assert
  assert result is not None
  assert len(result) == 3
  expected_first_valid_from = current_date.replace(hour=23, minute=30)
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

@pytest.mark.asyncio
async def test_when_start_time_and_end_time_is_same_and_rolling_target_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"

  expected_first_valid_from = datetime.strptime("2022-10-22T02:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

  tariff_code = "test-tariff"
  rates = rates_to_thirty_minute_increments(
    {
      "results": [
        {
          "value_exc_vat": 15.1,
          "value_inc_vat": 15.1,
          "valid_from": "2022-10-21T00:00:00Z",
          "valid_to": "2022-10-21T22:00:00Z"
        },
        {
          "value_exc_vat": 16.1,
          "value_inc_vat": 16.1,
          "valid_from": "2022-10-21T22:00:00Z",
          "valid_to": "2022-10-22T02:00:00Z"
        },
        {
          "value_exc_vat": 15.1,
          "value_inc_vat": 15.1,
          "valid_from": "2022-10-22T02:00:00Z",
          "valid_to": "2022-10-22T05:00:00Z"
        },
        {
          "value_exc_vat": 16.1,
          "value_inc_vat": 16.1,
          "valid_from": "2022-10-22T05:00:00Z",
          "valid_to": "2022-10-23T00:00:00Z"
        },
      ]
    },
    datetime.strptime("2022-10-21T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-24T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    tariff_code
  )

  # Act
  result = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    True
  )

  # Assert
  assert result is not None
  assert len(result) == 33
  
  expected_first_valid_from = current_date.replace(hour=23, minute=30)
  for item in result:
    assert item["start"] == expected_first_valid_from
    assert item["end"] == expected_first_valid_from + timedelta(minutes=30)
    expected_first_valid_from = item["end"]

@pytest.mark.asyncio
async def test_when_available_rates_are_too_low_then_no_times_are_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"

  # Act
  result = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    agile_rates,
    False
  )

  # Assert
  assert result is None