from datetime import (datetime)
import pytest

from custom_components.octopus_energy.utils.consumption import get_current_consumption_delta

@pytest.mark.asyncio
async def test_when_previous_updated_is_none_then_none_returned():
  # Arrange
  current_datetime = datetime.strptime("2023-08-04T10:10:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_updated = None
  previous_total_consumption = 33.6
  current_total_consumption = 35.9

  # Act
  consumption_delta = get_current_consumption_delta(current_datetime, current_total_consumption, previous_updated, previous_total_consumption)

  # Assert
  assert consumption_delta is None

@pytest.mark.asyncio
async def test_when_previous_updated_is_different_date_then_total_returned():
  # Arrange
  current_datetime = datetime.strptime("2023-08-04T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_updated = datetime.strptime("2023-08-03T23:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_total_consumption = 33.6
  current_total_consumption = 35.9

  # Act
  consumption_delta = get_current_consumption_delta(current_datetime, current_total_consumption, previous_updated, previous_total_consumption)

  # Assert
  assert consumption_delta == current_total_consumption

@pytest.mark.asyncio
async def test_when_previous_total_consumption_is_none_then_none_returned():
  # Arrange
  current_datetime = datetime.strptime("2023-08-04T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_updated = datetime.strptime("2023-08-03T23:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_total_consumption = None
  current_total_consumption = 35.9

  # Act
  consumption_delta = get_current_consumption_delta(current_datetime, current_total_consumption, previous_updated, previous_total_consumption)

  # Assert
  assert consumption_delta is None

@pytest.mark.asyncio
async def test_when_previous_updated_is_same_date_then_delta_returned():
  # Arrange
  current_datetime = datetime.strptime("2023-08-04T23:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_updated = datetime.strptime("2023-08-04T23:59:58+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_total_consumption = 33.6
  current_total_consumption = 35.9

  # Act
  consumption_delta = get_current_consumption_delta(current_datetime, current_total_consumption, previous_updated, previous_total_consumption)

  # Assert
  assert consumption_delta == (current_total_consumption - previous_total_consumption)