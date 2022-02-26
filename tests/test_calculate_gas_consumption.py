from datetime import datetime, timedelta
import pytest

from tests import (create_consumption_data, get_test_context)
from custom_components.octopus_energy.sensor_utils import async_get_consumption_data, calculate_gas_consumption
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
@pytest.mark.parametrize("is_smets1_meter,latest_date",[
  (True, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (True, None),
  (False, datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (False, None)
])
async def test_when_gas_consumption_available_then_calculation_returned(is_smets1_meter,latest_date):
  # Arrange
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  consumption_data = create_consumption_data(period_from, period_to)
  assert consumption_data != None
  assert len(consumption_data) > 0
  assert consumption_data[-1]["interval_end"] == period_to
  assert consumption_data[0]["interval_start"] == period_from

  # Act
  consumption = calculate_gas_consumption(
    consumption_data,
    latest_date,
    is_smets1_meter
  )

  # Assert
  assert consumption != None
  assert consumption["last_calculated_timestamp"] == consumption_data[-1]["interval_end"]
  
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

@pytest.mark.asyncio
async def test_when_gas_consumption_starting_at_latest_date_then_calculation_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True
  latest_date = None

  consumption_data = create_consumption_data(period_from, period_to, True)
  assert consumption_data != None
  assert len(consumption_data) > 0
  assert consumption_data[0]["interval_end"] == period_to
  assert consumption_data[-1]["interval_start"] == period_from

  # Act
  consumption = calculate_gas_consumption(
    consumption_data,
    latest_date,
    is_smets1_meter
  )

  # Assert
  assert consumption != None
  assert consumption["last_calculated_timestamp"] == consumption_data[0]["interval_end"]
  
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

@pytest.mark.asyncio
@pytest.mark.parametrize("is_smets1_meter",[
  (True),
  (False)
])
async def test_when_calculate_gas_consumption_uses_real_data_then_calculation_returned(is_smets1_meter):
  # Arrange
  context = get_test_context()
  client = OctopusEnergyApiClient(context["api_key"])

  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = None

  # Retrieve real consumption data so we can make sure our calculation works with the result
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  sensor_identifier = context["gas_mprn"]
  sensor_serial_number = context["gas_serial_number"]
  is_electricity = False
  consumption_data = await async_get_consumption_data(
    client,
    [],
    current_utc_timestamp,
    period_from,
    period_to,
    sensor_identifier,
    sensor_serial_number,
    is_electricity
  )

  # Act
  consumption = calculate_gas_consumption(
    consumption_data,
    latest_date,
    is_smets1_meter
  )

  # Assert
  assert consumption != None
  assert consumption["last_calculated_timestamp"] == consumption_data[-1]["interval_end"]
  
  # Check that for SMETS1 meters, we convert the data from kwh to m3
  if is_smets1_meter:
    assert consumption["total"] == 5.892
  else:
    assert consumption["total"] == 66.951

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