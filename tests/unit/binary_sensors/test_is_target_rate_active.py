from datetime import datetime, timedelta
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.binary_sensors import is_target_rate_active

@pytest.mark.asyncio
async def test_when_called_before_rates_then_not_active_returned():
  # Arrange
  rates = [
    {
      "valid_from": datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
      "valid_from": datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
      "valid_from": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    }
  ]

  current_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Act
  result = is_target_rate_active(
    current_date,
    rates
  )

  # Assert
  assert result is not None
  assert result["is_active"] == False
  assert result["current_duration_in_hours"] == 0
  assert result["next_time"] == rates[0]["valid_from"]
  assert result["next_duration_in_hours"] == 1

@pytest.mark.asyncio
async def test_when_called_during_rates_then_active_returned():
  # Arrange
  rates = [
    {
      "valid_from": datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
      "valid_from": datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
      "valid_from": datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
      "valid_from": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
      "valid_from": datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
      "valid_from": datetime.strptime("2022-02-09T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    }
  ]

  tests = [
    {
      "current_date": datetime.strptime("2022-02-09T10:15:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_current_duration_in_hours": 1.5,
      "expected_next_duration_in_hours": 1
    },
    {
      "current_date": datetime.strptime("2022-02-09T12:35:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": datetime.strptime("2022-02-09T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_current_duration_in_hours": 1,
      "expected_next_duration_in_hours": 0.5
    },
    {
      "current_date": datetime.strptime("2022-02-09T14:05:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": None,
      "expected_current_duration_in_hours": 0.5,
      "expected_next_duration_in_hours": 0
    }
  ]
  
  for test in tests:
    result = is_target_rate_active(
      test["current_date"],
      rates
    )

    # Assert
    assert result is not None
    assert result["is_active"] == True
    assert result["current_duration_in_hours"] == test["expected_current_duration_in_hours"]
    assert result["next_time"] == test["expected_next_time"]
    assert result["next_duration_in_hours"] == test["expected_next_duration_in_hours"]

@pytest.mark.asyncio
async def test_when_called_after_rates_then_not_active_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2]

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )

  current_date = period_to + timedelta(minutes=15)

  # Act
  result = is_target_rate_active(
    current_date,
    rates
  )

  # Assert
  assert result is not None
  assert result["is_active"] == False
  assert result["next_time"] is None

@pytest.mark.asyncio
async def test_when_offset_set_then_active_at_correct_current_time():
  # Arrange
  offset = "-01:00:00"

  rates = [
    {
      "valid_from": datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
      "valid_from": datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
      "valid_from": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    }
  ]

  # Check where we're before the offset
  current_date = rates[0]["valid_from"] - timedelta(hours=1, minutes=1)

  result = is_target_rate_active(
    current_date,
    rates,
    offset
  )

  assert result is not None
  assert result["is_active"] == False
  assert result["next_time"] == datetime.strptime("2022-02-09T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Check where's within our rates and our offset
  for minutes_to_add in range(60):
    current_date = rates[0]["valid_from"] - timedelta(hours=1) + timedelta(minutes=minutes_to_add)

    result = is_target_rate_active(
      current_date,
      rates,
      offset
    )

    assert result is not None
    assert result["is_active"] == True
    assert result["next_time"] is not None

  # Check when within rate but after offset
  current_date = rates[0]["valid_from"] - timedelta(hours=1) + timedelta(minutes=61)

  result = is_target_rate_active(
    current_date,
    rates,
    offset
  )

  assert result is not None
  assert result["is_active"] == False
  assert result["next_time"] == datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
async def test_when_current_date_is_equal_to_last_end_date_then_not_active():
  # Arrange
  period_from = datetime.strptime("2022-10-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-10-09T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1]
  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )

  current_date = datetime.strptime("2022-10-09T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

  result = is_target_rate_active(
    current_date,
    rates,
    None
  )

  assert result is not None
  assert result["is_active"] == False
  assert result["next_time"] is None