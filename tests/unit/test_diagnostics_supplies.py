from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.octopus_energy.const import (
  CONFIG_MAIN_SUPPLIES_TO_MONITOR,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
)
from custom_components.octopus_energy.diagnostics import async_get_diagnostics


def get_account_info():
  return {
    "id": "A-TEST",
    "property_ids": [],
    "electricity_meter_points": [
      {
        "mpan": "electricity-mpan",
        "meters": [{"serial_number": "electricity-serial", "device_id": ""}],
      }
    ],
    "gas_meter_points": [
      {
        "mprn": "gas-mprn",
        "meters": [{"serial_number": "gas-serial", "device_id": ""}],
      }
    ],
  }


@pytest.mark.asyncio
@pytest.mark.parametrize(
  "supplies_to_monitor,electricity_calls,gas_calls",
  [
    (CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY, 1, 0),
    (CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS, 0, 1),
  ],
)
@pytest.mark.parametrize("use_existing_account", [True, False])
async def test_diagnostics_only_retrieves_consumption_for_monitored_supplies(
  supplies_to_monitor,
  electricity_calls,
  gas_calls,
  use_existing_account,
):
  # Arrange
  account_info = get_account_info()
  client = MagicMock()
  client.async_get_account = AsyncMock(return_value=account_info)
  client.async_get_electricity_consumption = AsyncMock(return_value=[])
  client.async_get_gas_consumption = AsyncMock(return_value=[])
  client.async_get_intelligent_devices = AsyncMock(return_value=[])
  client.async_get_heat_pump_ids = AsyncMock(return_value=[])
  config = {CONFIG_MAIN_SUPPLIES_TO_MONITOR: supplies_to_monitor}

  # Act
  result = await async_get_diagnostics(
    client,
    "A-TEST",
    account_info if use_existing_account else None,
    None,
    lambda _: {},
    config,
  )

  # Assert
  assert client.async_get_electricity_consumption.await_count == electricity_calls
  assert client.async_get_gas_consumption.await_count == gas_calls
  assert len(result["account"]["electricity_meter_points"]) == electricity_calls
  assert len(result["account"]["gas_meter_points"]) == gas_calls
