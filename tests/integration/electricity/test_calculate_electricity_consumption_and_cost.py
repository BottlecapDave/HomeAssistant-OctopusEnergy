from datetime import datetime, timedelta
import pytest

from integration import (get_test_context)
from custom_components.octopus_energy.electricity import calculate_electricity_consumption_and_cost
from custom_components.octopus_energy.coordinators.previous_consumption_and_rates import async_fetch_consumption_and_rates
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_calculate_electricity_cost_uses_real_data_then_calculation_returned():
  # Arrange
  context = get_test_context()
  client = OctopusEnergyApiClient(context["api_key"])

  current = datetime.strptime("2022-02-28T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  tariff_code = "E-1R-SUPER-GREEN-24M-21-07-30-A"
  latest_date = None
  is_smart_meter = True

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  # Retrieve real consumption data so we can make sure our calculation works with the result
  current_utc_timestamp = datetime.strptime(f'2022-03-02T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  sensor_identifier = context["electricity_mpan"]
  sensor_serial_number = context["electricity_serial_number"]
  is_electricity = True
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
    is_smart_meter,
    fire_event
  )

  assert consumption_and_rates_result is not None
  assert "consumption" in consumption_and_rates_result
  assert "rates" in consumption_and_rates_result
  assert "standing_charge" in consumption_and_rates_result

  # Make sure we have rates and standing charges available
  rates = await client.async_get_electricity_rates(tariff_code, False, period_from, period_to)
  assert rates is not None
  assert len(rates) > 0

  standard_charge_result = await client.async_get_electricity_standing_charge(tariff_code, period_from, period_to)
  assert standard_charge_result is not None

  # Act
  result = calculate_electricity_consumption_and_cost(
    current,
    consumption_and_rates_result["consumption"],
    consumption_and_rates_result["rates"],
    consumption_and_rates_result["standing_charge"],
    latest_date,
    tariff_code
  )

  # Assert
  assert result is not None
  assert result["standing_charge"] == round(standard_charge_result["value_inc_vat"] / 100, 2)
  assert result["total_cost_without_standing_charge"] == 1.63
  assert result["total_cost"] == 1.87
  assert result["last_evaluated"] == consumption_and_rates_result["consumption"][-1]["interval_end"]

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
    assert "consumption" in item

  assert round(result["total_consumption"], 2) == 8.11