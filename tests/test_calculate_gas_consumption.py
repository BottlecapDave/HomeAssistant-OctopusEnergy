from datetime import datetime, timedelta
import pytest

from tests import (get_test_context, create_consumption_data)
from custom_components.octopus_energy.sensor_utils import calculate_gas_consumption
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_gas_consumption_is_none_then_no_calculation_is_returned():
  # Arrange
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True

  # Act
  consumption = calculate_gas_consumption(
    None,
    latest_date,
    is_smets1_meter
  )

  # Assert
  assert consumption == None

@pytest.mark.asyncio
async def test_when_gas_consumption_is_empty_then_no_calculation_is_returned():
  # Arrange
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True

  # Act
  consumption = calculate_gas_consumption(
    [],
    latest_date,
    is_smets1_meter
  )

  # Assert
  assert consumption == None

@pytest.mark.asyncio
async def test_when_gas_consumption_is_before_latest_date_then_no_calculation_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-12T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True

  consumption_data = create_consumption_data(period_from, period_to)

  # Act
  consumption = calculate_gas_consumption(
    consumption_data,
    latest_date,
    is_smets1_meter
  )

  # Assert
  assert consumption == None

@pytest.mark.asyncio
@pytest.mark.parametrize("is_smets1_meter",[(True), (False)])
async def test_when_gas_consumption_available_then_calculation_returned(is_smets1_meter):
  # Arrange
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True

  consumption_data = create_consumption_data(period_from, period_to)

  # Act
  consumption = calculate_gas_consumption(
    consumption_data,
    latest_date,
    is_smets1_meter
  )

  # Assert
  assert consumption != None
  
  # Check that for SMETS1 meters, we convert the data from kwh to m3
  if is_smets1_meter:
    assert consumption["total"] == 4.224
  else:
    assert consumption["total"] == 48

  assert len(consumption["consumptions"]) == len(consumption_data)

  # Make sure our data is returned in 30 minute increments
  expected_valid_from = period_from
  for item in consumption["consumptions"]:
      expected_valid_to = expected_valid_from + timedelta(minutes=30)

      assert "from" in item
      assert item["from"] == expected_valid_from
      assert "to" in item
      assert item["to"] == expected_valid_to

      expected_valid_from = expected_valid_to