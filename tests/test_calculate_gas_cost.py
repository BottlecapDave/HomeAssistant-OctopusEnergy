from datetime import datetime, timedelta
import pytest

from tests import get_test_context
from custom_components.octopus_energy.sensor_utils import async_calculate_gas_cost
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_gas_consumption_is_none_then_no_calculation_is_returned():
  # Arrange
  context = get_test_context()

  client = OctopusEnergyApiClient(context["api_key"])
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True
  tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"

  # Act
  consumption_cost = await async_calculate_gas_cost(
    client,
    None,
    latest_date,
    period_from,
    period_to,
    {
      "tariff_code": tariff_code,
      "is_smets1_meter": is_smets1_meter
    }
  )

  # Assert
  assert consumption_cost == None

@pytest.mark.asyncio
async def test_when_gas_consumption_is_empty_then_no_calculation_is_returned():
  # Arrange
  context = get_test_context()

  client = OctopusEnergyApiClient(context["api_key"])
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True
  tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"

  # Act
  consumption_cost = await async_calculate_gas_cost(
    client,
    [],
    latest_date,
    period_from,
    period_to,
    {
      "tariff_code": tariff_code,
      "is_smets1_meter": is_smets1_meter
    }
  )

  # Assert
  assert consumption_cost == None

@pytest.mark.asyncio
async def test_when_gas_consumption_is_before_latest_date_then_no_calculation_is_returned():
  # Arrange
  context = get_test_context()

  client = OctopusEnergyApiClient(context["api_key"])
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-12T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True
  tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"

  consumption_data = await client.async_get_gas_consumption(context["gas_mprn"], context["gas_serial_number"], period_from, period_to)
  assert consumption_data != None
  assert len(consumption_data) > 0

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
  assert consumption_cost == None

@pytest.mark.asyncio
async def test_when_gas_consumption_available_then_calculation_returned():
  # Arrange
  context = get_test_context()

  client = OctopusEnergyApiClient(context["api_key"])
  period_from = datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  is_smets1_meter = True
  tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"
  
  consumption_data = await client.async_get_gas_consumption(context["gas_mprn"], context["gas_serial_number"], period_from, period_to)
  assert consumption_data != None
  assert len(consumption_data) > 0

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
  assert consumption_cost["standing_charge"] == standard_charge_result["value_inc_vat"]
  assert consumption_cost["total_without_standing_charge"] == 3.02
  assert consumption_cost["total"] == 3.28
  assert len(consumption_cost["charges"]) == 48

  # Make sure our data is returned in 30 minute increments
  expected_valid_to = period_to
  for item in consumption_cost["charges"]:
      expected_valid_from = expected_valid_to - timedelta(minutes=30)

      assert "from" in item
      assert item["from"] == expected_valid_from
      assert "to" in item
      assert item["to"] == expected_valid_to

      expected_valid_to = expected_valid_from