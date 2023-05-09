from datetime import datetime, timedelta
import pytest

from integration import (get_test_context)
from custom_components.octopus_energy.electricity import calculate_electricity_consumption
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.coordinators.previous_consumption_and_rates import async_fetch_consumption_and_rates

@pytest.mark.asyncio
async def test_when_calculate_electricity_consumption_uses_real_data_then_calculation_returned():
  # Arrange
  context = get_test_context()
  client = OctopusEnergyApiClient(context["api_key"])

  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = None
  tariff_code = "E-1R-SUPER-GREEN-24M-21-07-30-A"
  is_smart_meter = True
  
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
    is_smart_meter
  )

  assert consumption_and_rates_result is not None
  assert "consumption" in consumption_and_rates_result
  assert "rates" in consumption_and_rates_result

  # Act
  consumption = calculate_electricity_consumption(
    consumption_and_rates_result["consumption"],
    latest_date
  )

  # Assert
  assert consumption is not None
  assert round(consumption["total"], 2) == 8.11
  assert consumption["last_calculated_timestamp"] == consumption_and_rates_result["consumption"][-1]["interval_end"]

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