from datetime import datetime, timedelta
import pytest

from unit import (create_consumption_data)
from custom_components.octopus_energy.sensor_utils import async_get_consumption_data, calculate_electricity_consumption
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_electricity_consumption_is_none_then_no_calculation_is_returned():
  # Arrange
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Act
  consumption_cost = calculate_electricity_consumption(
    None,
    latest_date
  )

  # Assert
  assert consumption_cost == None

@pytest.mark.asyncio
async def test_when_electricity_consumption_is_empty_then_no_calculation_is_returned():
  # Arrange
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Act
  consumption_cost = calculate_electricity_consumption(
    [],
    latest_date,
  )

  # Assert
  assert consumption_cost == None

@pytest.mark.asyncio
async def test_when_electricity_consumption_is_before_latest_date_then_no_calculation_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-12T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  consumption_data = create_consumption_data(period_from, period_to)
  assert consumption_data != None
  assert len(consumption_data) > 0

  # Act
  consumption_cost = calculate_electricity_consumption(
    consumption_data,
    latest_date
  )

  # Assert
  assert consumption_cost == None

@pytest.mark.asyncio
@pytest.mark.parametrize("latest_date",[(datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")), (None)])
async def test_when_electricity_consumption_available_then_calculation_returned(latest_date):
  # Arrange
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  consumption_data = create_consumption_data(period_from, period_to)
  assert consumption_data != None
  assert len(consumption_data) > 0
  assert consumption_data[-1]["interval_end"] == period_to
  assert consumption_data[0]["interval_start"] == period_from

  # Act
  consumption_cost = calculate_electricity_consumption(
    consumption_data,
    latest_date
  )

  # Assert
  assert consumption_cost != None
  assert consumption_cost["total"] == 48
  assert consumption_cost["last_calculated_timestamp"] == consumption_data[-1]["interval_end"]

  assert len(consumption_cost["consumptions"]) == 48

  # Make sure our data is returned in 30 minute increments
  expected_valid_from = period_from
  for item in consumption_cost["consumptions"]:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "from" in item
    assert item["from"] == expected_valid_from
    assert "to" in item
    assert item["to"] == expected_valid_to

    expected_valid_from = expected_valid_to

@pytest.mark.asyncio
async def test_when_electricity_consumption_starts_with_latest_date_then_calculation_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = None
  
  consumption_data = create_consumption_data(period_from, period_to, True)
  assert consumption_data != None
  assert len(consumption_data) > 0
  assert consumption_data[0]["interval_end"] == period_to
  assert consumption_data[-1]["interval_start"] == period_from

  # Act
  consumption = calculate_electricity_consumption(
    consumption_data,
    latest_date
  )

  # Assert
  assert consumption != None
  assert consumption["total"] == 48
  assert consumption["last_calculated_timestamp"] == consumption_data[0]["interval_end"]

  assert len(consumption["consumptions"]) == 48

  # Make sure our data is returned in 30 minute increments
  expected_valid_from = period_from
  for item in consumption["consumptions"]:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "from" in item
    assert item["from"] == expected_valid_from
    assert "to" in item
    assert item["to"] == expected_valid_to

    expected_valid_from = expected_valid_to