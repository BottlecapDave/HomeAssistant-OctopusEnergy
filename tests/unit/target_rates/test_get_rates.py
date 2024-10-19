from datetime import datetime, timedelta
import pytest

from custom_components.octopus_energy.target_rates import get_rates
from tests.unit import create_rate_data

@pytest.mark.asyncio
async def test_when_rates_is_none_then_none_returned():
  # Arrange
  current_datetime = datetime.strptime("2024-10-19T10:15:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  all_rates = None
  target_hours = 2

  # Act
  actual_rates = get_rates(current_datetime, all_rates, target_hours)

  # Assert
  assert actual_rates is None

@pytest.mark.asyncio
async def test_when_not_enough_rates_available_then_none_returned():
  # Arrange
  current_datetime = datetime.strptime("2024-10-19T10:15:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  all_rates = create_rate_data(
    datetime.strptime("2024-10-19T10:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-10-19T11:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [1]
  )
  target_hours = 2

  # Act
  actual_rates = get_rates(current_datetime, all_rates, target_hours)

  # Assert
  assert actual_rates is None

@pytest.mark.asyncio
async def test_when_rates_available_then_target_rates_returned():
  # Arrange
  current_datetime = datetime.strptime("2024-10-19T10:15:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  all_rates = create_rate_data(
    datetime.strptime("2024-10-19T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-10-20T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [1, 2, 3]
  )
  target_hours = 2

  # Act
  actual_rates = get_rates(current_datetime, all_rates, target_hours)

  # Assert
  assert actual_rates is not None
  assert len(actual_rates) == 4
  expected_start_date = datetime.strptime("2024-10-19T10:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  for rate in actual_rates:
    assert rate["start"] == expected_start_date

    expected_start_date += timedelta(minutes=30)
    assert rate["end"] == expected_start_date