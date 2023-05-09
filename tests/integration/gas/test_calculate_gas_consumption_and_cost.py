from datetime import datetime, timedelta
import pytest

from integration import (get_test_context)
from custom_components.octopus_energy.gas import async_calculate_gas_consumption_and_cost
from custom_components.octopus_energy.coordinators.previous_consumption_and_rates import async_fetch_consumption_and_rates
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
@pytest.mark.parametrize("consumption_units",[
  ("m³"), 
  ("kWh")
])
async def test_when_calculate_gas_cost_using_real_data_then_calculation_returned(consumption_units):
  # Arrange
  context = get_test_context()
  client = OctopusEnergyApiClient(context["api_key"])

  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"
  latest_date = None
  
  # Retrieve real consumption data so we can make sure our calculation works with the result
  current_utc_timestamp = datetime.strptime(f'2022-03-02T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  sensor_identifier = context["gas_mprn"]
  sensor_serial_number = context["gas_serial_number"]
  is_electricity = False
  consumption_and_rates_result = await async_fetch_consumption_and_rates(
    None,
    current_utc_timestamp,
    client,
    period_from,
    period_to,
    sensor_identifier,
    sensor_serial_number,
    is_electricity,
    tariff_code,
    True
  )

  assert consumption_and_rates_result is not None
  assert "consumption" in consumption_and_rates_result
  assert "rates" in consumption_and_rates_result

  # Make sure we have standing charges available

  standard_charge_result = await client.async_get_gas_standing_charge(tariff_code, period_from, period_to)
  assert standard_charge_result is not None

  # Act
  result = await async_calculate_gas_consumption_and_cost(
    consumption_and_rates_result["consumption"],
    consumption_and_rates_result["rates"],
    consumption_and_rates_result["standing_charge"],
    latest_date,
    tariff_code,
    consumption_units,
    40
  )

  # Assert
  assert result is not None
  assert result["last_calculated_timestamp"] == consumption_and_rates_result["consumption"][-1]["interval_end"]
  assert result["standing_charge"] == standard_charge_result["value_inc_vat"]
  
  if consumption_units == "m³":
    assert result["total_cost_without_standing_charge"] == 2.88
    assert result["total_cost"] == 3.14
    assert round(result["total_consumption_kwh"], 2) == 63.86
    assert round(result["total_consumption_m3"], 2) == 5.62
  else:
    assert result["total_cost_without_standing_charge"] == 0.25
    assert result["total_cost"] == 0.52
    assert round(result["total_consumption_kwh"], 2) == 5.62
    assert round(result["total_consumption_m3"], 2) == 0.5

  assert len(result["charges"]) == 48

  # Make sure our data is returned in 30 minute increments
  expected_valid_from = period_from
  for item in result["charges"]:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "from" in item
    assert item["from"] == expected_valid_from
    assert "to" in item
    assert item["to"] == expected_valid_to

    expected_valid_from = expected_valid_to

    assert "rate" in item
    assert "cost" in item
    assert "consumption_m3" in item
    assert "consumption_kwh" in item

  