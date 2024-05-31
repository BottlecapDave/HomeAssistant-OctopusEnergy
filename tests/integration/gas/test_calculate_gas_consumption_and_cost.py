from datetime import datetime, timedelta
import pytest

from integration import (get_test_context)
from custom_components.octopus_energy.gas import calculate_gas_consumption_and_cost
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
  client = OctopusEnergyApiClient(context.api_key)

  account_info = await client.async_get_account(context.account_id)
  assert account_info is not None

  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_product_code = "SUPER-GREEN-24M-21-07-30"
  expected_tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-L"
  latest_date = None

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  # Retrieve real consumption data so we can make sure our calculation works with the result
  current_utc_timestamp = datetime.strptime(f'2022-03-02T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  sensor_identifier = context.gas_mprn
  sensor_serial_number = context.gas_serial_number
  is_electricity = False
  consumption_and_rates_result = await async_fetch_consumption_and_rates(
    None,
    current_utc_timestamp,
    account_info,
    client,
    period_from,
    period_to,
    sensor_identifier,
    sensor_serial_number,
    is_electricity,
    True,
    fire_event
  )

  assert consumption_and_rates_result is not None

  # Make sure we have standing charges available

  standard_charge_result = await client.async_get_gas_standing_charge(expected_product_code, expected_tariff_code, period_from, period_to)
  assert standard_charge_result is not None

  # Act
  result = calculate_gas_consumption_and_cost(
    consumption_and_rates_result.consumption,
    consumption_and_rates_result.rates,
    consumption_and_rates_result.standing_charge,
    latest_date,
    consumption_units,
    40
  )

  # Assert
  assert result is not None
  assert result["last_evaluated"] == consumption_and_rates_result.consumption[-1]["end"]
  assert result["standing_charge"] == round(standard_charge_result["value_inc_vat"] / 100, 2)
  
  if consumption_units == "m³":
    assert result["total_cost_without_standing_charge"] == 2.86
    assert result["total_cost"] == 3.12
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

    assert "start" in item
    assert item["start"] == expected_valid_from
    assert "end" in item
    assert item["end"] == expected_valid_to

    expected_valid_from = expected_valid_to

    assert "rate" in item
    assert "cost" in item
    assert "consumption_m3" in item
    assert "consumption_kwh" in item

  