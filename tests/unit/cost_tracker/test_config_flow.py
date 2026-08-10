from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.octopus_energy import async_migrate_entry
from custom_components.octopus_energy.config_flow import OctopusEnergyConfigFlow
from custom_components.octopus_energy.const import (
  CONFIG_ACCOUNT_ID,
  CONFIG_COST_TRACKER_ENTITY_ACCUMULATIVE_VALUE,
  CONFIG_COST_TRACKER_MANUAL_RESET,
  CONFIG_COST_TRACKER_MONTH_DAY_RESET,
  CONFIG_COST_TRACKER_MPAN,
  CONFIG_COST_TRACKER_NAME,
  CONFIG_COST_TRACKER_TARGET_ENTITY_ID,
  CONFIG_COST_TRACKER_WEEKDAY_RESET,
  CONFIG_KIND,
  CONFIG_KIND_COST_TRACKER,
  CONFIG_VERSION,
  DATA_ACCOUNT,
  DOMAIN,
)


def create_user_input(target_entity_id: str) -> dict:
  return {
    CONFIG_COST_TRACKER_NAME: "test_tracker",
    CONFIG_COST_TRACKER_MPAN: "1234567890123",
    CONFIG_COST_TRACKER_TARGET_ENTITY_ID: target_entity_id,
    CONFIG_COST_TRACKER_ENTITY_ACCUMULATIVE_VALUE: True,
    CONFIG_COST_TRACKER_MANUAL_RESET: False,
    CONFIG_COST_TRACKER_WEEKDAY_RESET: "0",
    CONFIG_COST_TRACKER_MONTH_DAY_RESET: 1,
  }


@pytest.mark.asyncio
async def test_discovery_flow_keeps_discovered_target_as_canonical_identity():
  flow = OctopusEnergyConfigFlow()
  flow.hass = SimpleNamespace(data={
    DOMAIN: {
      "A-TEST": {
        DATA_ACCOUNT: SimpleNamespace(account={}),
      }
    }
  })
  flow._account_id = "A-TEST"
  flow._target_entity_id = "sensor.lounge_cooling_energy"
  flow._async_abort_entries_match = Mock()
  flow.async_set_unique_id = AsyncMock()
  flow._abort_if_unique_id_configured = Mock()
  flow.async_create_entry = Mock(return_value={"type": "create_entry"})
  user_input = create_user_input("sensor.kitchen_heating_energy")

  with patch(
    "custom_components.octopus_energy.config_flow.validate_cost_tracker_config",
    return_value={},
  ):
    await flow.async_step_cost_tracker(user_input)

  assert user_input[CONFIG_COST_TRACKER_TARGET_ENTITY_ID] == "sensor.lounge_cooling_energy"
  flow.async_set_unique_id.assert_awaited_once_with(
    "octopus_energy_ct_A-TEST_sensor.lounge_cooling_energy",
    raise_on_progress=False,
  )
  flow._async_abort_entries_match.assert_called_once_with({
    CONFIG_KIND: CONFIG_KIND_COST_TRACKER,
    CONFIG_ACCOUNT_ID: "A-TEST",
    CONFIG_COST_TRACKER_TARGET_ENTITY_ID: "sensor.lounge_cooling_energy",
  })


@pytest.mark.asyncio
async def test_migration_repairs_unique_id_from_canonical_target():
  config_entry = SimpleNamespace(
    version=CONFIG_VERSION - 1,
    data={
      CONFIG_KIND: CONFIG_KIND_COST_TRACKER,
      CONFIG_ACCOUNT_ID: "A-TEST",
      CONFIG_COST_TRACKER_TARGET_ENTITY_ID: "sensor.kitchen_heating_energy",
    },
    options={},
    title="Kitchen heating (cost tracker)",
    unique_id="octopus_energy_ct_A-TEST_sensor.lounge_cooling_energy",
    entry_id="entry-id",
  )
  config_entries = SimpleNamespace(
    async_entries=Mock(return_value=[]),
    async_update_entry=Mock(),
  )
  hass = SimpleNamespace(config_entries=config_entries)

  result = await async_migrate_entry(hass, config_entry)

  assert result is True
  config_entries.async_update_entry.assert_called_once_with(
    config_entry,
    title="Kitchen heating (cost tracker)",
    data=config_entry.data,
    options={},
    unique_id="octopus_energy_ct_A-TEST_sensor.kitchen_heating_energy",
    version=CONFIG_VERSION,
  )
