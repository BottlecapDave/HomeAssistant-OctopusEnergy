from datetime import datetime
import pytest

from custom_components.octopus_energy.octoplus import OctoplusSessionConsumptionDate, get_filtered_consumptions
from tests.integration import create_consumption_data

@pytest.mark.asyncio
async def test_when_target_consumption_dates_not_present_then_empty_list_returned():
  # Arrange
  consumptions: list = create_consumption_data(
    datetime.strptime("2024-09-18T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-09-18T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  target_consumption_dates: list[OctoplusSessionConsumptionDate] = [
    OctoplusSessionConsumptionDate(
      datetime.strptime("2024-09-18T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2024-09-18T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )
  ]

  # Act
  result = get_filtered_consumptions(
    consumptions,
    target_consumption_dates,
  )

  # Assert
  assert result is not None
  assert len(result) == 0

@pytest.mark.asyncio
async def test_when_target_consumption_dates_empty_then_empty_list_returned():
  # Arrange
  consumptions: list = create_consumption_data(
    datetime.strptime("2024-09-18T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-09-18T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  target_consumption_dates: list[OctoplusSessionConsumptionDate] = []

  # Act
  result = get_filtered_consumptions(
    consumptions,
    target_consumption_dates,
  )

  # Assert
  assert result is not None
  assert len(result) == 0

@pytest.mark.asyncio
async def test_when_target_consumption_dates_present_then_filtered_list_returned():
  # Arrange
  consumptions: list = create_consumption_data(
    datetime.strptime("2024-09-18T16:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-09-18T19:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  target_consumption_dates: list[OctoplusSessionConsumptionDate] = [
    OctoplusSessionConsumptionDate(
      datetime.strptime("2024-09-18T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2024-09-18T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )
  ]

  # Act
  result = get_filtered_consumptions(
    consumptions,
    target_consumption_dates,
  )

  # Assert
  assert result is not None
  assert len(result) == 2

  assert result[0] == consumptions[2]
  assert result[1] == consumptions[3]