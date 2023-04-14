from datetime import datetime, timedelta
import pytest

from integration import (get_test_context)
from custom_components.octopus_energy.gas import calculate_gas_consumption
from custom_components.octopus_energy.coordinators.previous_consumption import async_get_consumption_data
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
@pytest.mark.parametrize("consumption_units",[
  ("m³"), 
  ("kWh")
])
async def test_when_calculate_gas_consumption_uses_real_data_then_calculation_returned(consumption_units):
  # Arrange
  context = get_test_context()
  client = OctopusEnergyApiClient(context["api_key"])

  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = None

  # Retrieve real consumption data so we can make sure our calculation works with the result
  current_utc_timestamp = datetime.strptime(f'2022-03-02T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
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
    consumption_units,
    40
  )

  # Assert
  assert consumption is not None
  assert consumption["last_calculated_timestamp"] == consumption_data[-1]["interval_end"]

  if consumption_units == "m³":
    assert consumption["total_kwh"] == 63.86
    assert consumption["total_m3"] == 5.62
  else:
    assert consumption["total_kwh"] == 5.62
    assert consumption["total_m3"] == 0.498

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