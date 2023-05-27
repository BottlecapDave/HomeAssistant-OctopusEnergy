from datetime import datetime, timedelta
import pytest

from unit import (create_rate_data, agile_rates)
from custom_components.octopus_energy.api_client import rates_to_thirty_minute_increments
from custom_components.octopus_energy.target_rates import calculate_continuous_times

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

  # Act
  result = calculate_continuous_times(
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
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.1

  assert result[1]["valid_from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["valid_to"] == expected_first_valid_from + timedelta(hours=1)
  assert result[1]["value_inc_vat"] == 0.1

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

  # Act
  result = calculate_continuous_times(
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
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.2

  assert result[1]["valid_from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["valid_to"] == expected_first_valid_from + timedelta(hours=1)
  assert result[1]["value_inc_vat"] == 0.3

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

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    rates,
    is_rolling_target
  )

  # Assert
  assert result is not None

  if (expected_first_valid_from is None):
    assert len(result) == 0
  else:
    assert len(result) == 2
    assert result[0]["valid_from"] == expected_first_valid_from
    assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
    assert result[1]["valid_from"] == expected_first_valid_from + timedelta(minutes=30)
    assert result[1]["valid_to"] == expected_first_valid_from + timedelta(minutes=60)

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
  assert result is not None
  assert len(result) == 8

  start_time = datetime.strptime("2022-10-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  for index in range(8):
    end_time = start_time + timedelta(minutes=30)
    assert result[index]["valid_from"] == start_time
    assert result[index]["valid_to"] == end_time
    assert result[index]["value_inc_vat"] == rates[1]["value_inc_vat"]

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

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    agile_rates
  )

  # Assert
  assert result is not None
  assert len(result) == 1
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 18.081

@pytest.mark.asyncio
async def test_when_start_time_is_after_end_time_then_rates_are_overnight():
  # Arrange
  current_date = datetime.strptime("2022-10-21T09:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "20:00"
  target_end_time = "09:00"

  expected_first_valid_from = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 1

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    agile_rates,
    False
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 14.123

  assert result[1]["valid_from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["valid_to"] == expected_first_valid_from + timedelta(minutes=60)
  assert result[1]["value_inc_vat"] == 14.123

@pytest.mark.asyncio
async def test_when_start_time_and_end_time_is_same_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2022-10-21T17:10:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"

  expected_first_valid_from = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
  # Restrict our time block
  target_hours = 1

  # Act
  result = calculate_continuous_times(
    current_date,
    target_start_time,
    target_end_time,
    target_hours,
    agile_rates,
    False
  )

  # Assert
  assert result is not None
  assert len(result) == 2
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 14.123

  assert result[1]["valid_from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["valid_to"] == expected_first_valid_from + timedelta(minutes=60)
  assert result[1]["value_inc_vat"] == 14.123


@pytest.mark.asyncio
async def test_when_start_time_is_after_end_time_and_rolling_target_then_rates_are_overnight():
  # Arrange
  current_date = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "22:00"
  target_end_time = "01:00"

  expected_first_valid_from = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
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
  result = calculate_continuous_times(
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
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 16.1

  assert result[1]["valid_from"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[1]["valid_to"] == expected_first_valid_from + timedelta(minutes=60)
  assert result[1]["value_inc_vat"] == 16.1

@pytest.mark.asyncio
async def test_when_start_time_and_end_time_is_same_and_rolling_target_then_rates_are_shifted():
  # Arrange
  current_date = datetime.strptime("2022-10-21T23:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"

  expected_first_valid_from = datetime.strptime("2022-10-22T02:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  
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
  result = calculate_continuous_times(
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
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 15.1

@pytest.mark.asyncio
async def test_when_available_rates_are_too_low_then_no_times_are_returned():
  # Arrange
  current_date = datetime.strptime("2022-10-22T22:40:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "16:00"
  target_end_time = "16:00"
  
  # Restrict our time block
  target_hours = 3

  # Act
  result = calculate_continuous_times(
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