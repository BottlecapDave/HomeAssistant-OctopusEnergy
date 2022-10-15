from datetime import datetime, timedelta
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.utils import rates_to_thirty_minute_increments
from custom_components.octopus_energy.target_sensor_utils import calculate_continuous_times

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
])
async def test_when_continuous_times_present_then_next_continuous_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target):
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2, 0.3, 0.2, 0.2, 0.1]

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )
  
  # Restrict our time block
  target_hours = 1

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    None,
    is_rolling_target
  )

  # Assert
  assert result != None
  assert len(result) == 2
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.1

  assert result[1]["valid_from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["valid_to"] == expected_first_valid_from + timedelta(hours=1)
  assert result[1]["value_inc_vat"] == 0.1

@pytest.mark.asyncio
async def test_when_current_time_has_not_enough_time_left_then_no_continuous_times_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2, 0.3, 0.2, 0.2, 0.1]

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )
  
  # Restrict our time block
  current_date = datetime.strptime("2022-02-09T17:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "10:00"
  target_end_time = "18:00"
  target_hours = 1

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates
  )

  # Assert
  assert result != None
  assert len(result) == 0

@pytest.mark.asyncio
async def test_when_offset_set_then_next_continuous_times_returned_have_offset_applied():
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2, 0.3, 0.2, 0.2, 0.1]
  current_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "11:00"
  target_end_time = "18:00"
  offset = "-01:00:00"

  expected_first_valid_from = datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 1

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    offset
  )

  # Assert
  assert result != None
  assert len(result) == 2
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.1

  assert result[1]["valid_from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["valid_to"] == expected_first_valid_from + timedelta(hours=1)
  assert result[1]["value_inc_vat"] == 0.1

# Added for https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/68
@pytest.mark.asyncio
@pytest.mark.parametrize("current_date",[
  (datetime.strptime("2022-10-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T01:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T03:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T07:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T07:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T08:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T08:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T09:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T13:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T15:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T16:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T17:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T18:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T19:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T21:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T22:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-10-09T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z")),
])
async def test_when_go_rates_supplied_once_a_day_set_and_cheapest_period_past_then_no_period_returned(current_date):
  # Arrange
  tariff_code = "test-tariff"
  rates = rates_to_thirty_minute_increments(
    {
      "results": [
        {
          "value_exc_vat": 38.217,
          "value_inc_vat": 40.12785,
          "valid_from": "2022-10-08T04:30:00Z",
          "valid_to": "2022-10-09T00:30:00Z"
        },
        {
          "value_exc_vat": 7.142,
          "value_inc_vat": 7.4991,
          "valid_from": "2022-10-09T00:30:00Z",
          "valid_to": "2022-10-09T04:30:00Z"
        },
        {
          "value_exc_vat": 38.217,
          "value_inc_vat": 40.12785,
          "valid_from": "2022-10-09T04:30:00Z",
          "valid_to": "2022-10-10T00:30:00Z"
        }
      ]
    },
    datetime.strptime("2022-10-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    tariff_code
  )

  assert rates != None
  assert len(rates) == 48
  
  # Restrict our time block
  target_hours = 4

  # Act
  result = calculate_continuous_times(
    current_date,
    None,
    None,
    target_hours,
    rates,
    None,
    False
  )

  # Assert
  assert result != None
  assert len(result) == 8

  start_time = datetime.strptime("2022-10-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(8):
    end_time = start_time + timedelta(minutes=30)
    assert result[index]["valid_from"] == start_time
    assert result[index]["valid_to"] == end_time
    assert result[index]["value_inc_vat"] == rates[1]["value_inc_vat"]
    assert result[index]["value_exc_vat"] == rates[1]["value_exc_vat"]

    assert result[index]["tariff_code"] == tariff_code

    start_time = end_time

  # Make sure our end time doesn't go outside of our Octopus Go cheap period
  assert start_time == datetime.strptime("2022-10-09T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")