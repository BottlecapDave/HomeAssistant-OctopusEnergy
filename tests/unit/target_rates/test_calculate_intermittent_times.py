from datetime import datetime, timedelta
import pytest

from unit import (create_rate_data, agile_rates)
from custom_components.octopus_energy.api_client import rates_to_thirty_minute_increments
from custom_components.octopus_energy.target_rates import calculate_intermittent_times

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target,find_last_rates",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),

  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),

  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),

  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T21:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
])
async def test_when_intermittent_times_present_then_next_intermittent_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target, find_last_rates):
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
  result = calculate_intermittent_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    is_rolling_target,
    False,
    find_last_rates
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["start"] == expected_first_valid_from
  assert result[0]["end"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.001

  assert result[1]["start"] == expected_first_valid_from + timedelta(hours=1, minutes=30)
  assert result[1]["end"] == expected_first_valid_from + timedelta(hours=2)
  assert result[1]["value_inc_vat"] == 0.001

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target,find_last_rates",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
])
async def test_when_intermittent_times_present_and_highest_prices_are_true_then_next_intermittent_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target, find_last_rates):
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
  result = calculate_intermittent_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    is_rolling_target,
    True,
    find_last_rates
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["start"] == expected_first_valid_from
  assert result[0]["end"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.003

  assert result[1]["start"] == expected_first_valid_from + timedelta(hours=1, minutes=30)
  assert result[1]["end"] == expected_first_valid_from + timedelta(hours=2)
  assert result[1]["value_inc_vat"] == 0.003

@pytest.mark.asyncio
async def test_when_current_time_has_not_enough_time_left_then_no_intermittent_times_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2, 0.3]

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
  result = calculate_intermittent_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates
  )

  # Assert
  assert result is not None
  assert len(result) == 0

@pytest.mark.asyncio
async def test_when_start_time_is_after_end_time_then_rates_are_overnight():
  # Arrange
  current_date = datetime.strptime("2022-10-21T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "20:00"
  target_end_time = "09:00"
  
  # Restrict our time block
  target_hours = 1

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
          "value_exc_vat": 14.1,
          "value_inc_vat": 14.1,
          "valid_from": "2022-10-22T02:00:00Z",
          "valid_to": "2022-10-22T02:30:00Z"
        },
        {
          "value_exc_vat": 15.1,
          "value_inc_vat": 15.1,
          "valid_from": "2022-10-22T02:30:00Z",
          "valid_to": "2022-10-22T09:00:00Z"
        },
      ]
    },
    datetime.strptime("2022-10-21T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-24T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    tariff_code
  )

  # Act
  result = calculate_intermittent_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    False
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["start"] == datetime.strptime("2022-10-21T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["end"] == datetime.strptime("2022-10-21T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["value_inc_vat"] == 0.151

  assert result[1]["start"] == datetime.strptime("2022-10-22T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["end"] == datetime.strptime("2022-10-22T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["value_inc_vat"] == 0.141

@pytest.mark.asyncio
async def test_when_start_time_and_end_time_is_same_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2022-10-21T17:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  
  # Restrict our time block
  target_hours = 1

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
          "value_exc_vat": 14.1,
          "value_inc_vat": 14.1,
          "valid_from": "2022-10-21T22:00:00Z",
          "valid_to": "2022-10-21T22:30:00Z"
        },
        {
          "value_exc_vat": 16.1,
          "value_inc_vat": 16.1,
          "valid_from": "2022-10-21T22:30:00Z",
          "valid_to": "2022-10-22T02:00:00Z"
        },
        {
          "value_exc_vat": 14.1,
          "value_inc_vat": 14.1,
          "valid_from": "2022-10-22T02:00:00Z",
          "valid_to": "2022-10-22T02:30:00Z"
        },
        {
          "value_exc_vat": 15.1,
          "value_inc_vat": 15.1,
          "valid_from": "2022-10-22T02:30:00Z",
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
  result = calculate_intermittent_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    False
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["start"] == datetime.strptime("2022-10-21T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["end"] == datetime.strptime("2022-10-21T22:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["value_inc_vat"] == 0.141

  assert result[1]["start"] == datetime.strptime("2022-10-22T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["end"] == datetime.strptime("2022-10-22T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["value_inc_vat"] == 0.141

@pytest.mark.asyncio
async def test_when_start_time_is_after_end_time_and_rolling_target_then_rates_are_overnight():
  # Arrange
  current_date = datetime.strptime("2022-10-21T21:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "20:00"
  target_end_time = "09:00"
  
  # Restrict our time block
  target_hours = 1

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
          "value_exc_vat": 14.1,
          "value_inc_vat": 14.1,
          "valid_from": "2022-10-22T02:00:00Z",
          "valid_to": "2022-10-22T02:30:00Z"
        },
        {
          "value_exc_vat": 15.1,
          "value_inc_vat": 15.1,
          "valid_from": "2022-10-22T02:30:00Z",
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
  result = calculate_intermittent_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    True
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["start"] == datetime.strptime("2022-10-21T21:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["end"] == datetime.strptime("2022-10-21T22:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["value_inc_vat"] == 0.151

  assert result[1]["start"] == datetime.strptime("2022-10-22T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["end"] == datetime.strptime("2022-10-22T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["value_inc_vat"] == 0.141

@pytest.mark.asyncio
async def test_when_start_time_and_end_time_is_same_and_rolling_target_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2022-10-21T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  
  # Restrict our time block
  target_hours = 1

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
          "value_exc_vat": 14.1,
          "value_inc_vat": 14.1,
          "valid_from": "2022-10-21T22:00:00Z",
          "valid_to": "2022-10-21T22:30:00Z"
        },
        {
          "value_exc_vat": 16.1,
          "value_inc_vat": 16.1,
          "valid_from": "2022-10-21T22:30:00Z",
          "valid_to": "2022-10-22T02:00:00Z"
        },
        {
          "value_exc_vat": 14.1,
          "value_inc_vat": 14.1,
          "valid_from": "2022-10-22T02:00:00Z",
          "valid_to": "2022-10-22T02:30:00Z"
        },
        {
          "value_exc_vat": 15.1,
          "value_inc_vat": 15.1,
          "valid_from": "2022-10-22T02:30:00Z",
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
  result = calculate_intermittent_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    True
  )

  # Assert
  assert result is not None
  assert len(result) == 2

  assert result[0]["start"] == datetime.strptime("2022-10-22T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["end"] == datetime.strptime("2022-10-22T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["value_inc_vat"] == 0.141

  assert result[1]["start"] == datetime.strptime("2022-10-22T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["end"] == datetime.strptime("2022-10-22T03:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["value_inc_vat"] == 0.151

@pytest.mark.asyncio
async def test_when_using_agile_times_then_lowest_rates_are_picked():
  # Arrange
  current_date = datetime.strptime("2022-10-21T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  
  # Restrict our time block
  target_hours = 3

  # Act
  result = calculate_intermittent_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    agile_rates,
    False
  )

  # Assert
  assert result is not None
  assert len(result) == 6

  assert result[0]["start"] == datetime.strptime("2022-10-21T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["end"] == datetime.strptime("2022-10-22T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["value_inc_vat"] == 0.14123

  assert result[1]["start"] == datetime.strptime("2022-10-22T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["end"] == datetime.strptime("2022-10-22T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["value_inc_vat"] == 0.14123

  assert result[2]["start"] == datetime.strptime("2022-10-22T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[2]["end"] == datetime.strptime("2022-10-22T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[2]["value_inc_vat"] == 0.179025

  assert result[3]["start"] == datetime.strptime("2022-10-22T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[3]["end"] == datetime.strptime("2022-10-22T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[3]["value_inc_vat"] == 0.17136

  assert result[4]["start"] == datetime.strptime("2022-10-22T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[4]["end"] == datetime.strptime("2022-10-22T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[4]["value_inc_vat"] == 0.17136

  assert result[5]["start"] == datetime.strptime("2022-10-22T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[5]["end"] == datetime.strptime("2022-10-22T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[5]["value_inc_vat"] == 0.18081

@pytest.mark.asyncio
async def test_when_available_rates_are_too_low_then_no_times_are_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  
  # Restrict our time block
  target_hours = 3

  # Act
  result = calculate_intermittent_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    agile_rates,
    False
  )

  # Assert
  assert result is not None
  assert len(result) == 0