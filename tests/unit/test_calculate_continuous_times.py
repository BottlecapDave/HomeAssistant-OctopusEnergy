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
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
])
async def test_when_continuous_times_present_and_highest_price_required_then_next_continuous_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target):
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2, 0.3]

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
    is_rolling_target,
    True
  )

  # Assert
  assert result != None
  assert len(result) == 2
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.2

  assert result[1]["valid_from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["valid_to"] == expected_first_valid_from + timedelta(hours=1)
  assert result[1]["value_inc_vat"] == 0.3

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

@pytest.mark.asyncio
async def test_when_last_rate_is_currently_active_and_target_is_rolling_then_rates_are_not_reevaluated():
  # Arrange
  period_from = datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  offset = None

  expected_first_valid_from = datetime.strptime("2022-10-22T12:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 0.5

  rates = rates_to_thirty_minute_increments(
    {
      "results": [
        {
          "value_exc_vat": 15.33,
          "value_inc_vat": 16.0965,
          "valid_from": "2022-10-22T22:30:00Z",
          "valid_to": "2022-10-22T23:00:00Z"
        },
        {
          "value_exc_vat": 14.28,
          "value_inc_vat": 14.994,
          "valid_from": "2022-10-22T22:00:00Z",
          "valid_to": "2022-10-22T22:30:00Z"
        },
        {
          "value_exc_vat": 22.03,
          "value_inc_vat": 23.1315,
          "valid_from": "2022-10-22T21:30:00Z",
          "valid_to": "2022-10-22T22:00:00Z"
        },
        {
          "value_exc_vat": 24.42,
          "value_inc_vat": 25.641,
          "valid_from": "2022-10-22T21:00:00Z",
          "valid_to": "2022-10-22T21:30:00Z"
        },
        {
          "value_exc_vat": 23.1,
          "value_inc_vat": 24.255,
          "valid_from": "2022-10-22T20:30:00Z",
          "valid_to": "2022-10-22T21:00:00Z"
        },
        {
          "value_exc_vat": 27.89,
          "value_inc_vat": 29.2845,
          "valid_from": "2022-10-22T20:00:00Z",
          "valid_to": "2022-10-22T20:30:00Z"
        },
        {
          "value_exc_vat": 24.36,
          "value_inc_vat": 25.578,
          "valid_from": "2022-10-22T19:30:00Z",
          "valid_to": "2022-10-22T20:00:00Z"
        },
        {
          "value_exc_vat": 31.58,
          "value_inc_vat": 33.159,
          "valid_from": "2022-10-22T19:00:00Z",
          "valid_to": "2022-10-22T19:30:00Z"
        },
        {
          "value_exc_vat": 29.23,
          "value_inc_vat": 30.6915,
          "valid_from": "2022-10-22T18:30:00Z",
          "valid_to": "2022-10-22T19:00:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-22T18:00:00Z",
          "valid_to": "2022-10-22T18:30:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-22T17:30:00Z",
          "valid_to": "2022-10-22T18:00:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-22T17:00:00Z",
          "valid_to": "2022-10-22T17:30:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-22T16:30:00Z",
          "valid_to": "2022-10-22T17:00:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-22T16:00:00Z",
          "valid_to": "2022-10-22T16:30:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-22T15:30:00Z",
          "valid_to": "2022-10-22T16:00:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-22T15:00:00Z",
          "valid_to": "2022-10-22T15:30:00Z"
        },
        {
          "value_exc_vat": 21.0,
          "value_inc_vat": 22.05,
          "valid_from": "2022-10-22T14:30:00Z",
          "valid_to": "2022-10-22T15:00:00Z"
        },
        {
          "value_exc_vat": 20.37,
          "value_inc_vat": 21.3885,
          "valid_from": "2022-10-22T14:00:00Z",
          "valid_to": "2022-10-22T14:30:00Z"
        },
        {
          "value_exc_vat": 18.02,
          "value_inc_vat": 18.921,
          "valid_from": "2022-10-22T13:30:00Z",
          "valid_to": "2022-10-22T14:00:00Z"
        },
        {
          "value_exc_vat": 18.27,
          "value_inc_vat": 19.1835,
          "valid_from": "2022-10-22T13:00:00Z",
          "valid_to": "2022-10-22T13:30:00Z"
        },
        {
          "value_exc_vat": 17.22,
          "value_inc_vat": 18.081,
          "valid_from": "2022-10-22T12:30:00Z",
          "valid_to": "2022-10-22T13:00:00Z"
        },
        {
          "value_exc_vat": 17.64,
          "value_inc_vat": 18.522,
          "valid_from": "2022-10-22T12:00:00Z",
          "valid_to": "2022-10-22T12:30:00Z"
        },
        {
          "value_exc_vat": 19.03,
          "value_inc_vat": 19.9815,
          "valid_from": "2022-10-22T11:30:00Z",
          "valid_to": "2022-10-22T12:00:00Z"
        },
        {
          "value_exc_vat": 20.33,
          "value_inc_vat": 21.3465,
          "valid_from": "2022-10-22T11:00:00Z",
          "valid_to": "2022-10-22T11:30:00Z"
        },
        {
          "value_exc_vat": 19.74,
          "value_inc_vat": 20.727,
          "valid_from": "2022-10-22T10:30:00Z",
          "valid_to": "2022-10-22T11:00:00Z"
        },
        {
          "value_exc_vat": 19.74,
          "value_inc_vat": 20.727,
          "valid_from": "2022-10-22T10:00:00Z",
          "valid_to": "2022-10-22T10:30:00Z"
        },
        {
          "value_exc_vat": 20.16,
          "value_inc_vat": 21.168,
          "valid_from": "2022-10-22T09:30:00Z",
          "valid_to": "2022-10-22T10:00:00Z"
        },
        {
          "value_exc_vat": 21.21,
          "value_inc_vat": 22.2705,
          "valid_from": "2022-10-22T09:00:00Z",
          "valid_to": "2022-10-22T09:30:00Z"
        },
        {
          "value_exc_vat": 21.59,
          "value_inc_vat": 22.6695,
          "valid_from": "2022-10-22T08:30:00Z",
          "valid_to": "2022-10-22T09:00:00Z"
        },
        {
          "value_exc_vat": 23.4,
          "value_inc_vat": 24.57,
          "valid_from": "2022-10-22T08:00:00Z",
          "valid_to": "2022-10-22T08:30:00Z"
        },
        {
          "value_exc_vat": 28.56,
          "value_inc_vat": 29.988,
          "valid_from": "2022-10-22T07:30:00Z",
          "valid_to": "2022-10-22T08:00:00Z"
        },
        {
          "value_exc_vat": 23.18,
          "value_inc_vat": 24.339,
          "valid_from": "2022-10-22T07:00:00Z",
          "valid_to": "2022-10-22T07:30:00Z"
        },
        {
          "value_exc_vat": 20.75,
          "value_inc_vat": 21.7875,
          "valid_from": "2022-10-22T06:30:00Z",
          "valid_to": "2022-10-22T07:00:00Z"
        },
        {
          "value_exc_vat": 16.32,
          "value_inc_vat": 17.136,
          "valid_from": "2022-10-22T06:00:00Z",
          "valid_to": "2022-10-22T06:30:00Z"
        },
        {
          "value_exc_vat": 16.32,
          "value_inc_vat": 17.136,
          "valid_from": "2022-10-22T05:30:00Z",
          "valid_to": "2022-10-22T06:00:00Z"
        },
        {
          "value_exc_vat": 18.9,
          "value_inc_vat": 19.845,
          "valid_from": "2022-10-22T05:00:00Z",
          "valid_to": "2022-10-22T05:30:00Z"
        },
        {
          "value_exc_vat": 17.05,
          "value_inc_vat": 17.9025,
          "valid_from": "2022-10-22T04:30:00Z",
          "valid_to": "2022-10-22T05:00:00Z"
        },
        {
          "value_exc_vat": 18.9,
          "value_inc_vat": 19.845,
          "valid_from": "2022-10-22T04:00:00Z",
          "valid_to": "2022-10-22T04:30:00Z"
        },
        {
          "value_exc_vat": 17.62,
          "value_inc_vat": 18.501,
          "valid_from": "2022-10-22T03:30:00Z",
          "valid_to": "2022-10-22T04:00:00Z"
        },
        {
          "value_exc_vat": 17.81,
          "value_inc_vat": 18.7005,
          "valid_from": "2022-10-22T03:00:00Z",
          "valid_to": "2022-10-22T03:30:00Z"
        },
        {
          "value_exc_vat": 17.47,
          "value_inc_vat": 18.3435,
          "valid_from": "2022-10-22T02:30:00Z",
          "valid_to": "2022-10-22T03:00:00Z"
        },
        {
          "value_exc_vat": 17.47,
          "value_inc_vat": 18.3435,
          "valid_from": "2022-10-22T02:00:00Z",
          "valid_to": "2022-10-22T02:30:00Z"
        },
        {
          "value_exc_vat": 18.42,
          "value_inc_vat": 19.341,
          "valid_from": "2022-10-22T01:30:00Z",
          "valid_to": "2022-10-22T02:00:00Z"
        },
        {
          "value_exc_vat": 18.69,
          "value_inc_vat": 19.6245,
          "valid_from": "2022-10-22T01:00:00Z",
          "valid_to": "2022-10-22T01:30:00Z"
        },
        {
          "value_exc_vat": 20.22,
          "value_inc_vat": 21.231,
          "valid_from": "2022-10-22T00:30:00Z",
          "valid_to": "2022-10-22T01:00:00Z"
        },
        {
          "value_exc_vat": 18.38,
          "value_inc_vat": 19.299,
          "valid_from": "2022-10-22T00:00:00Z",
          "valid_to": "2022-10-22T00:30:00Z"
        },
        {
          "value_exc_vat": 19.95,
          "value_inc_vat": 20.9475,
          "valid_from": "2022-10-21T23:30:00Z",
          "valid_to": "2022-10-22T00:00:00Z"
        },
        {
          "value_exc_vat": 20.58,
          "value_inc_vat": 21.609,
          "valid_from": "2022-10-21T23:00:00Z",
          "valid_to": "2022-10-21T23:30:00Z"
        },
        {
          "value_exc_vat": 18.9,
          "value_inc_vat": 19.845,
          "valid_from": "2022-10-21T22:30:00Z",
          "valid_to": "2022-10-21T23:00:00Z"
        },
        {
          "value_exc_vat": 18.75,
          "value_inc_vat": 19.6875,
          "valid_from": "2022-10-21T22:00:00Z",
          "valid_to": "2022-10-21T22:30:00Z"
        },
        {
          "value_exc_vat": 19.74,
          "value_inc_vat": 20.727,
          "valid_from": "2022-10-21T21:30:00Z",
          "valid_to": "2022-10-21T22:00:00Z"
        },
        {
          "value_exc_vat": 22.05,
          "value_inc_vat": 23.1525,
          "valid_from": "2022-10-21T21:00:00Z",
          "valid_to": "2022-10-21T21:30:00Z"
        },
        {
          "value_exc_vat": 19.74,
          "value_inc_vat": 20.727,
          "valid_from": "2022-10-21T20:30:00Z",
          "valid_to": "2022-10-21T21:00:00Z"
        },
        {
          "value_exc_vat": 22.39,
          "value_inc_vat": 23.5095,
          "valid_from": "2022-10-21T20:00:00Z",
          "valid_to": "2022-10-21T20:30:00Z"
        },
        {
          "value_exc_vat": 20.62,
          "value_inc_vat": 21.651,
          "valid_from": "2022-10-21T19:30:00Z",
          "valid_to": "2022-10-21T20:00:00Z"
        },
        {
          "value_exc_vat": 24.78,
          "value_inc_vat": 26.019,
          "valid_from": "2022-10-21T19:00:00Z",
          "valid_to": "2022-10-21T19:30:00Z"
        },
        {
          "value_exc_vat": 20.87,
          "value_inc_vat": 21.9135,
          "valid_from": "2022-10-21T18:30:00Z",
          "valid_to": "2022-10-21T19:00:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T18:00:00Z",
          "valid_to": "2022-10-21T18:30:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T17:30:00Z",
          "valid_to": "2022-10-21T18:00:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T17:00:00Z",
          "valid_to": "2022-10-21T17:30:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T16:30:00Z",
          "valid_to": "2022-10-21T17:00:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T16:00:00Z",
          "valid_to": "2022-10-21T16:30:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T15:30:00Z",
          "valid_to": "2022-10-21T16:00:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T15:00:00Z",
          "valid_to": "2022-10-21T15:30:00Z"
        },
        {
          "value_exc_vat": 21.0,
          "value_inc_vat": 22.05,
          "valid_from": "2022-10-21T14:30:00Z",
          "valid_to": "2022-10-21T15:00:00Z"
        },
        {
          "value_exc_vat": 19.74,
          "value_inc_vat": 20.727,
          "valid_from": "2022-10-21T14:00:00Z",
          "valid_to": "2022-10-21T14:30:00Z"
        },
        {
          "value_exc_vat": 20.2,
          "value_inc_vat": 21.21,
          "valid_from": "2022-10-21T13:30:00Z",
          "valid_to": "2022-10-21T14:00:00Z"
        },
        {
          "value_exc_vat": 20.2,
          "value_inc_vat": 21.21,
          "valid_from": "2022-10-21T13:00:00Z",
          "valid_to": "2022-10-21T13:30:00Z"
        },
        {
          "value_exc_vat": 20.35,
          "value_inc_vat": 21.3675,
          "valid_from": "2022-10-21T12:30:00Z",
          "valid_to": "2022-10-21T13:00:00Z"
        },
        {
          "value_exc_vat": 26.04,
          "value_inc_vat": 27.342,
          "valid_from": "2022-10-21T12:00:00Z",
          "valid_to": "2022-10-21T12:30:00Z"
        },
        {
          "value_exc_vat": 20.96,
          "value_inc_vat": 22.008,
          "valid_from": "2022-10-21T11:30:00Z",
          "valid_to": "2022-10-21T12:00:00Z"
        },
        {
          "value_exc_vat": 29.4,
          "value_inc_vat": 30.87,
          "valid_from": "2022-10-21T11:00:00Z",
          "valid_to": "2022-10-21T11:30:00Z"
        },
        {
          "value_exc_vat": 27.09,
          "value_inc_vat": 28.4445,
          "valid_from": "2022-10-21T10:30:00Z",
          "valid_to": "2022-10-21T11:00:00Z"
        },
        {
          "value_exc_vat": 25.2,
          "value_inc_vat": 26.46,
          "valid_from": "2022-10-21T10:00:00Z",
          "valid_to": "2022-10-21T10:30:00Z"
        },
        {
          "value_exc_vat": 25.62,
          "value_inc_vat": 26.901,
          "valid_from": "2022-10-21T09:30:00Z",
          "valid_to": "2022-10-21T10:00:00Z"
        },
        {
          "value_exc_vat": 31.5,
          "value_inc_vat": 33.075,
          "valid_from": "2022-10-21T09:00:00Z",
          "valid_to": "2022-10-21T09:30:00Z"
        },
        {
          "value_exc_vat": 30.58,
          "value_inc_vat": 32.109,
          "valid_from": "2022-10-21T08:30:00Z",
          "valid_to": "2022-10-21T09:00:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T08:00:00Z",
          "valid_to": "2022-10-21T08:30:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T07:30:00Z",
          "valid_to": "2022-10-21T08:00:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T07:00:00Z",
          "valid_to": "2022-10-21T07:30:00Z"
        },
        {
          "value_exc_vat": 31.882,
          "value_inc_vat": 33.4761,
          "valid_from": "2022-10-21T06:30:00Z",
          "valid_to": "2022-10-21T07:00:00Z"
        },
        {
          "value_exc_vat": 26.06,
          "value_inc_vat": 27.363,
          "valid_from": "2022-10-21T06:00:00Z",
          "valid_to": "2022-10-21T06:30:00Z"
        },
        {
          "value_exc_vat": 20.85,
          "value_inc_vat": 21.8925,
          "valid_from": "2022-10-21T05:30:00Z",
          "valid_to": "2022-10-21T06:00:00Z"
        },
        {
          "value_exc_vat": 21.38,
          "value_inc_vat": 22.449,
          "valid_from": "2022-10-21T05:00:00Z",
          "valid_to": "2022-10-21T05:30:00Z"
        },
        {
          "value_exc_vat": 25.56,
          "value_inc_vat": 26.838,
          "valid_from": "2022-10-21T04:30:00Z",
          "valid_to": "2022-10-21T05:00:00Z"
        },
        {
          "value_exc_vat": 20.2,
          "value_inc_vat": 21.21,
          "valid_from": "2022-10-21T04:00:00Z",
          "valid_to": "2022-10-21T04:30:00Z"
        },
        {
          "value_exc_vat": 20.2,
          "value_inc_vat": 21.21,
          "valid_from": "2022-10-21T03:30:00Z",
          "valid_to": "2022-10-21T04:00:00Z"
        },
        {
          "value_exc_vat": 20.62,
          "value_inc_vat": 21.651,
          "valid_from": "2022-10-21T03:00:00Z",
          "valid_to": "2022-10-21T03:30:00Z"
        },
        {
          "value_exc_vat": 20.41,
          "value_inc_vat": 21.4305,
          "valid_from": "2022-10-21T02:30:00Z",
          "valid_to": "2022-10-21T03:00:00Z"
        },
        {
          "value_exc_vat": 20.62,
          "value_inc_vat": 21.651,
          "valid_from": "2022-10-21T02:00:00Z",
          "valid_to": "2022-10-21T02:30:00Z"
        },
        {
          "value_exc_vat": 19.74,
          "value_inc_vat": 20.727,
          "valid_from": "2022-10-21T01:30:00Z",
          "valid_to": "2022-10-21T02:00:00Z"
        },
        {
          "value_exc_vat": 20.62,
          "value_inc_vat": 21.651,
          "valid_from": "2022-10-21T01:00:00Z",
          "valid_to": "2022-10-21T01:30:00Z"
        },
        {
          "value_exc_vat": 20.62,
          "value_inc_vat": 21.651,
          "valid_from": "2022-10-21T00:30:00Z",
          "valid_to": "2022-10-21T01:00:00Z"
        },
        {
          "value_exc_vat": 20.2,
          "value_inc_vat": 21.21,
          "valid_from": "2022-10-21T00:00:00Z",
          "valid_to": "2022-10-21T00:30:00Z"
        },
        {
          "value_exc_vat": 20.62,
          "value_inc_vat": 21.651,
          "valid_from": "2022-10-20T23:30:00Z",
          "valid_to": "2022-10-21T00:00:00Z"
        },
        {
          "value_exc_vat": 23.52,
          "value_inc_vat": 24.696,
          "valid_from": "2022-10-20T23:00:00Z",
          "valid_to": "2022-10-20T23:30:00Z"
        }
      ]
    },
    period_from,
    period_to,
    "E-1R-AGILE-18-02-21-G"
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
  assert len(result) == 1
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 18.081