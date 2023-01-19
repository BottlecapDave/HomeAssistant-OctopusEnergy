from datetime import datetime, timedelta
from time import time
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.target_sensor_utils import is_target_rate_active
from custom_components.octopus_energy.utils import rates_to_thirty_minute_increments

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
  assert result != None
  assert result["is_active"] == False
  assert result["next_time"] == rates[0]["valid_from"]
  assert result["current_duration_in_minutes"] == 0

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
      "expected_duration_in_minutes": 90
    },
    {
      "current_date": datetime.strptime("2022-02-09T12:35:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": datetime.strptime("2022-02-09T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_duration_in_minutes": 60
    },
    {
      "current_date": datetime.strptime("2022-02-09T14:05:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": None,
      "expected_duration_in_minutes": 30
    }
  ]
  
  for test in tests:
    result = is_target_rate_active(
      test["current_date"],
      rates
    )

    # Assert
    assert result != None
    assert result["is_active"] == True
    assert result["next_time"] == test["expected_next_time"]
    assert result["current_duration_in_minutes"] == test["expected_duration_in_minutes"]

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
  assert result != None
  assert result["is_active"] == False
  assert result["next_time"] == None

@pytest.mark.asyncio
async def test_when_offset_set_and_current_date_in_non_offset_rate_then_not_active():
  # Arrange
  period_from = datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2]
  offset = "-01:00:00"

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )

  rates = rates[0:2]

  # Attempt where the current date should be within a rate
  current_date = period_from + timedelta(minutes=15)

  result = is_target_rate_active(
    current_date,
    rates,
    offset
  )

  assert result != None
  assert result["is_active"] == False
  assert result["next_time"] == None

@pytest.mark.asyncio
async def test_when_offset_set_and_current_date_in_offset_rate_then_active():
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

  # Attempt where the current date should be within a rate
  current_date = rates[0]["valid_from"] + timedelta(minutes=15)

  result = is_target_rate_active(
    current_date,
    rates,
    offset
  )

  assert result != None
  assert result["is_active"] == False
  assert result["next_time"] == datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Attempt where the current date should be within a rate with the offset applied
  current_date = rates[0]["valid_from"] - timedelta(minutes=45)

  result = is_target_rate_active(
    current_date,
    rates,
    offset
  )

  assert result != None
  assert result["is_active"] == True
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

  assert result != None
  assert result["is_active"] == False
  assert result["next_time"] == None