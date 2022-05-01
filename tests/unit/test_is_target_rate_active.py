from datetime import datetime, timedelta
from time import time
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.target_sensor_utils import is_target_rate_active

@pytest.mark.asyncio
async def test_when_called_before_rates_then_not_active_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2]

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )

  current_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Act
  result = is_target_rate_active(
    current_date,
    rates
  )

  # Assert
  assert result != None
  assert result["is_active"] == False
  assert result["next_time"] == period_from

@pytest.mark.asyncio
async def test_when_called_during_rates_then_active_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2]

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )

  current_date = period_from + timedelta(minutes=15)
  expected_next_time = (period_from + timedelta(minutes=30))
  
  while current_date < period_to:
    result = is_target_rate_active(
      current_date,
      rates
    )

    # Assert
    assert result != None
    assert result["is_active"] == True
    assert result["next_time"] == expected_next_time

    current_date = current_date + timedelta(minutes=30)
    if expected_next_time != None:
      expected_next_time = expected_next_time + timedelta(minutes=30)
      if (expected_next_time >= period_to):
        expected_next_time = None

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
