from datetime import datetime, timedelta
import pytest

from integration import (get_test_context)
from custom_components.octopus_energy.sensor_utils import async_calculate_gas_cost, async_get_consumption_data
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
@pytest.mark.parametrize("is_smets1_meter",[
  (True),
  (False)
])
async def test_when_calculate_gas_cost_using_real_data_then_calculation_returned(is_smets1_meter):
  # Arrange
  context = get_test_context()
  client = OctopusEnergyApiClient(context["api_key"])

  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"
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

  # Make sure we have rates and standing charges available
  rates = await client.async_get_gas_rates(tariff_code, period_from, period_to)
  assert rates != None
  assert len(rates) > 0

  standard_charge_result = await client.async_get_gas_standing_charge(tariff_code, period_from, period_to)
  assert standard_charge_result != None

  # Act
  consumption_cost = await async_calculate_gas_cost(
    client,
    consumption_data,
    latest_date,
    period_from,
    period_to,
    {
      "tariff_code": tariff_code,
      "is_smets1_meter": is_smets1_meter
    }
  )

  # Assert
  assert consumption_cost != None
  assert consumption_cost["last_calculated_timestamp"] == consumption_data[-1]["interval_end"]
  assert consumption_cost["standing_charge"] == standard_charge_result["value_inc_vat"]
  
  # Check that for SMETS2 meters, we convert the data from m3 to kwh
  if is_smets1_meter:
    assert consumption_cost["total_without_standing_charge"] == 3.02
    assert consumption_cost["total"] == 3.28
  else:
    assert consumption_cost["total_without_standing_charge"] == 34.27
    assert consumption_cost["total"] == 34.53

  assert len(consumption_cost["charges"]) == 48

  # Make sure our data is returned in 30 minute increments
  expected_valid_from = period_from
  for item in consumption_cost["charges"]:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "from" in item
    assert item["from"] == expected_valid_from
    assert "to" in item
    assert item["to"] == expected_valid_to

    expected_valid_from = expected_valid_to