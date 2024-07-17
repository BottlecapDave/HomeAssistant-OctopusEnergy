from datetime import datetime, timedelta
from custom_components.octopus_energy.const import CONFIG_TARGET_HOURS_MODE_MAXIMUM, CONFIG_TARGET_HOURS_MODE_MINIMUM
import pytest

from unit import (create_rate_data, agile_rates)
from custom_components.octopus_energy.api_client import rates_to_thirty_minute_increments
from custom_components.octopus_energy.target_rates import calculate_continuous_times, get_applicable_rates

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target,find_last_rates",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T20:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
])
async def test_when_continuous_times_present_then_next_continuous_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target, find_last_rates):
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

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    is_rolling_target
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    target_hours,
    False,
    find_last_rates
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["start"] == expected_first_valid_from
  assert result[0]["end"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.001

  assert result[1]["start"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["end"] == expected_first_valid_from + timedelta(hours=1)
  assert result[1]["value_inc_vat"] == 0.001

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target,find_last_rates",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, False),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, False),
  
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True, True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False, True),
])
async def test_when_continuous_times_present_and_highest_price_required_then_next_continuous_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target, find_last_rates):
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

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    is_rolling_target
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    target_hours,
    True,
    find_last_rates
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["start"] == expected_first_valid_from
  assert result[0]["end"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.002

  assert result[1]["start"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["end"] == expected_first_valid_from + timedelta(hours=1)
  assert result[1]["value_inc_vat"] == 0.003

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target",[
  (datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-01T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-01T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2023-01-01T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2023-01-01T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, None, True),

  (datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-01T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-01T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2023-01-01T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", datetime.strptime("2023-01-01T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2023-01-01T18:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "05:00", "19:00", None, True),

  (datetime.strptime("2023-01-01T20:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", datetime.strptime("2023-01-01T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-02T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", datetime.strptime("2023-01-01T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2023-01-02T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", datetime.strptime("2023-01-02T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2023-01-02T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), "20:00", "06:00", None, True),
])
async def test_readme_examples(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target):
  # Arrange
  tariff_code = "test-tariff"
  rates = rates_to_thirty_minute_increments(
    {
      "results": [
        {
          "value_exc_vat": 6,
          "value_inc_vat": 6,
          "valid_from": "2023-01-01T00:00:00Z",
          "valid_to": "2023-01-01T00:30:00Z"
        },
        {
          "value_exc_vat": 12,
          "value_inc_vat": 12,
          "valid_from": "2023-01-01T00:30:00Z",
          "valid_to": "2023-01-01T05:00:00Z"
        },
        {
          "value_exc_vat": 7,
          "value_inc_vat": 7,
          "valid_from": "2023-01-01T05:00:00Z",
          "valid_to": "2023-01-01T05:30:00Z"
        },
        {
          "value_exc_vat": 20,
          "value_inc_vat": 20,
          "valid_from": "2023-01-01T05:30:00Z",
          "valid_to": "2023-01-01T18:00:00Z"
        },
        {
          "value_exc_vat": 34,
          "value_inc_vat": 34,
          "valid_from": "2023-01-01T18:00:00Z",
          "valid_to": "2023-01-01T23:30:00Z"
        },
        {
          "value_exc_vat": 5,
          "value_inc_vat": 5,
          "valid_from": "2023-01-01T23:30:00Z",
          "valid_to": "2023-01-02T00:30:00Z"
        },
        {
          "value_exc_vat": 12,
          "value_inc_vat": 12,
          "valid_from": "2023-01-02T00:30:00Z",
          "valid_to": "2023-01-02T05:00:00Z"
        },
        {
          "value_exc_vat": 7,
          "value_inc_vat": 7,
          "valid_from": "2023-01-02T05:00:00Z",
          "valid_to": "2023-01-02T05:30:00Z"
        },
        {
          "value_exc_vat": 20,
          "value_inc_vat": 20,
          "valid_from": "2023-01-02T05:30:00Z",
          "valid_to": "2023-01-02T18:00:00Z"
        },
        {
          "value_exc_vat": 34,
          "value_inc_vat": 34,
          "valid_from": "2023-01-02T18:00:00Z",
          "valid_to": "2023-01-02T23:30:00Z"
        },
        {
          "value_exc_vat": 6,
          "value_inc_vat": 6,
          "valid_from": "2023-01-02T23:30:00Z",
          "valid_to": "2023-01-03T00:00:00Z"
        },
      ]
    },
    datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    tariff_code
  )
  
  # Restrict our time block
  target_hours = 1

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    is_rolling_target
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    target_hours,
  )

  # Assert
  assert result is not None

  if (expected_first_valid_from is None):
    assert len(result) == 0
  else:
    assert len(result) == 2
    assert result[0]["start"] == expected_first_valid_from
    assert result[0]["end"] == expected_first_valid_from + timedelta(minutes=30)
    assert result[1]["start"] == expected_first_valid_from + timedelta(minutes=30)
    assert result[1]["end"] == expected_first_valid_from + timedelta(minutes=60)

@pytest.mark.asyncio
async def test_when_applicable_rates_is_none_then_no_continuous_times_returned():
  # Arrange
  target_hours = 1

  # Act
  result = calculate_continuous_times(
    None,
    target_hours
  )

  # Assert
  assert result is not None
  assert len(result) == 0

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

  assert rates is not None
  assert len(rates) == 48
  
  # Restrict our time block
  target_hours = 4

  applicable_rates = get_applicable_rates(
    current_date,
    None,
    None,
    rates,
    False
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    target_hours
  )

  # Assert
  assert result is not None
  assert len(result) == 8

  start_time = datetime.strptime("2022-10-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(8):
    end_time = start_time + timedelta(minutes=30)
    assert result[index]["start"] == start_time
    assert result[index]["end"] == end_time
    assert result[index]["value_inc_vat"] == round(rates[1]["value_inc_vat"] / 100, 6)

    assert result[index]["tariff_code"] == tariff_code

    start_time = end_time

  # Make sure our end time doesn't go outside of our Octopus Go cheap period
  assert start_time == datetime.strptime("2022-10-09T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
async def test_when_last_rate_is_currently_active_and_target_is_rolling_then_rates_are_not_reevaluated():
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"

  expected_first_valid_from = datetime.strptime("2022-10-22T12:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 0.5

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    agile_rates,
    True
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    target_hours,
    False,
    True
  )

  # Assert
  assert result is not None
  assert len(result) == 1
  assert result[0]["start"] == expected_first_valid_from
  assert result[0]["end"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.18081

@pytest.mark.asyncio
async def test_when_available_rates_are_too_low_then_no_times_are_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  
  # Restrict our time block
  target_hours = 3

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    agile_rates,
    False
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    target_hours
  )

  # Assert
  assert result is not None
  assert len(result) == 0

@pytest.mark.asyncio
@pytest.mark.parametrize("target_hours,expected_first_valid_from,expected_rates",[
  (0.5, datetime.strptime("2022-10-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [0.191]),
  (1, datetime.strptime("2022-10-22T09:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [0.2, 0.191]),
])
async def test_when_min_rate_is_provided_then_result_does_not_include_any_rate_below_min_rate(target_hours: float, expected_first_valid_from: datetime, expected_rates: list):
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  min_rate = 0.19

  rates = create_rate_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.1, 20]
  )

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    True
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    target_hours,
    False,
    False,
    min_rate
  )

  # Assert
  assert result is not None
  assert len(result) == len(expected_rates)

  expected_from = expected_first_valid_from
  for index in range(0, len(expected_rates)):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value_inc_vat"] == expected_rates[index]

@pytest.mark.asyncio
@pytest.mark.parametrize("target_hours,expected_first_valid_from,expected_rates",[
  (0.5, datetime.strptime("2022-10-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [0.191]),
  (1, datetime.strptime("2022-10-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [0.191, 0.189]),
])
async def test_when_max_rate_is_provided_then_result_does_not_include_any_rate_above_max_rate(target_hours: float, expected_first_valid_from: datetime, expected_rates: list):
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  max_rate = 0.199

  rates = create_rate_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.1, 20]
  )

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    True
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    target_hours,
    True,
    False,
    None,
    max_rate
  )

  # Assert
  assert result is not None
  assert len(result) == len(expected_rates)

  expected_from = expected_first_valid_from
  for index in range(0, len(expected_rates)):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value_inc_vat"] == expected_rates[index]

@pytest.mark.asyncio
@pytest.mark.parametrize("weighting,possible_rates,expected_first_valid_from,expected_rates",[
  ([1, 2, 1], [19.1, 18.9, 19.1, 15.1, 20], datetime.strptime("2022-10-22T11:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [0.191, 0.151, 0.20]),
  ([1, 2, 2], [19.1, 18.9, 19.1, 15.1, 20], datetime.strptime("2022-10-22T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [0.189, 0.191, 0.151]),
  ([1, 0, 0], [19.1, 18.9, 19.1, 15.1, 20], datetime.strptime("2022-10-22T11:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [0.151, 0.20, 0.191]),

  # Examples defined in https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/807
  (None, [14, 14, 10, 7, 15, 21], datetime.strptime("2022-10-22T09:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [0.14, 0.1, 0.07]),
  ([1, 1, 2], [14, 14, 10, 7, 15, 21], datetime.strptime("2022-10-22T09:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [0.14, 0.1, 0.07]),
  ([5, 1, 1], [14, 14, 10, 7, 15, 21], datetime.strptime("2022-10-22T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), [0.07, 0.15, 0.21]),
])
async def test_when_weighting_specified_then_result_is_adjusted(weighting: list, possible_rates: list, expected_first_valid_from: datetime, expected_rates: list):
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"

  rates = create_rate_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    possible_rates
  )

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    True
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    1.5,
    False,
    False,
    None,
    weighting=weighting
  )

  # Assert
  assert result is not None
  assert len(result) == len(expected_rates)

  expected_from = expected_first_valid_from
  for index in range(0, len(expected_rates)):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value_inc_vat"] == expected_rates[index]

@pytest.mark.asyncio
@pytest.mark.parametrize("weighting",[
  (None),
  ([]),
])
async def test_when_target_hours_zero_then_result_is_adjusted(weighting):
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"

  rates = create_rate_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    [19.1, 18.9, 19.1, 15.1, 20]
  )

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    True
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    0,
    False,
    False,
    None,
    weighting=weighting
  )

  # Assert
  assert result is not None
  assert len(result) == 0

def test_when_hour_mode_is_maximum_and_not_enough_hours_available_then_reduced_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  possible_rates = [19.1, 18.9, 21.1, 15.1, 20]
  expected_rates = [0.191, 0.189]

  rates = create_rate_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    possible_rates
  )

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    True
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    1.5,
    False,
    False,
    max_rate=0.199,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MAXIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 2

  expected_from = datetime.strptime("2022-10-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(0, 2):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value_inc_vat"] == expected_rates[index]

def test_when_hour_mode_is_maximum_and_more_than_enough_hours_available_then_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  possible_rates = [19.1, 18.9, 19.1, 15.1, 20]
  expected_rates = [0.189, 0.191, 0.151]

  rates = create_rate_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    possible_rates
  )

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    True
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    1.5,
    False,
    False,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MAXIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 3

  expected_from = datetime.strptime("2022-10-22T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(0, 3):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value_inc_vat"] == expected_rates[index]

def test_when_hour_mode_is_minimum_and_not_enough_hours_available_then_no_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  possible_rates = [19.1, 18.9, 21.1, 15.1, 20]
  expected_rates = [0.191, 0.189]

  rates = create_rate_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    possible_rates
  )

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    True
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    1.5,
    False,
    False,
    max_rate=0.199,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MINIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 0

def test_when_hour_mode_is_minimum_and_more_than_enough_hours_available_then_target_rates_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "09:00"
  target_end_time = "22:00"
  possible_rates = [19.1, 18.9, 19.1, 15.1, 20]
  expected_rates = [0.191, 0.189, 0.191, 0.151]

  rates = create_rate_data(
    datetime.strptime("2022-10-22T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    possible_rates
  )

  applicable_rates = get_applicable_rates(
    current_date,
    target_start_time,
    target_end_time,
    rates,
    True
  )

  # Act
  result = calculate_continuous_times(
    applicable_rates,
    1.5,
    False,
    False,
    max_rate=0.199,
    hours_mode=CONFIG_TARGET_HOURS_MODE_MINIMUM
  )

  # Assert
  assert result is not None
  assert len(result) == 4

  expected_from = datetime.strptime("2022-10-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(0, 3):
    assert result[index]["start"] == expected_from
    expected_from = expected_from + timedelta(minutes=30)
    assert result[index]["end"] == expected_from
    assert result[index]["value_inc_vat"] == expected_rates[index]