from datetime import datetime, timedelta
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.target_sensor_utils import calculate_intermittent_times

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
])
async def test_when_intermittent_times_present_then_next_intermittent_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target):
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
    None,
    is_rolling_target
  )

  # Assert
  assert result != None
  assert len(result) == 2
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.1

  assert result[1]["valid_from"] == expected_first_valid_from + timedelta(hours=1, minutes=30)
  assert result[1]["valid_to"] == expected_first_valid_from + timedelta(hours=2)
  assert result[1]["value_inc_vat"] == 0.1

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,target_start_time,target_end_time,expected_first_valid_from,is_rolling_target",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-10T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", "18:00", datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # # No start set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-10T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, "18:00", datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # # No end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "10:00", None, datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  # # No start or end set
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), True),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
  (datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), None, None, datetime.strptime("2022-02-09T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), False),
])
async def test_when_intermittent_times_present_and_highest_prices_are_true_then_next_intermittent_times_returned(current_date, target_start_time, target_end_time, expected_first_valid_from, is_rolling_target):
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
    None,
    is_rolling_target,
    True
  )

  # Assert
  assert result != None
  assert len(result) == 2
  assert result[0]["valid_from"] == expected_first_valid_from
  assert result[0]["valid_to"] == expected_first_valid_from + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.3

  assert result[1]["valid_from"] == expected_first_valid_from + timedelta(hours=1, minutes=30)
  assert result[1]["valid_to"] == expected_first_valid_from + timedelta(hours=2)
  assert result[1]["value_inc_vat"] == 0.3

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
  assert result != None
  assert len(result) == 0

@pytest.mark.asyncio
async def test_when_offset_set_then_next_continuous_times_returned_have_offset_applied():
  # Arrange
  period_from = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2, 0.3]
  current_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_start_time = "11:00"
  target_end_time = "18:00"
  offset = "-01:00:00"
  
  # Restrict our time block
  target_hours = 1

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )

  # Act
  result = calculate_intermittent_times(
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
  assert result[0]["valid_from"] == datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[0]["valid_to"] == datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z") + timedelta(minutes=30)
  assert result[0]["value_inc_vat"] == 0.1

  assert result[1]["valid_from"] == datetime.strptime("2022-02-09T13:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert result[1]["valid_to"] == datetime.strptime("2022-02-09T13:30:00Z", "%Y-%m-%dT%H:%M:%S%z") + timedelta(minutes=30)
  assert result[1]["value_inc_vat"] == 0.1