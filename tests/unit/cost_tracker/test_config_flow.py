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


def create_flow() -> OctopusEnergyConfigFlow:
  flow = OctopusEnergyConfigFlow()
  flow.hass = SimpleNamespace(data={
    DOMAIN: {
      "A-TEST": {
        DATA_ACCOUNT: SimpleNamespace(account={"electricity_meter_points": []}),
      }
    }
  })
  return flow


def create_config_entry(target_entity_id: str) -> SimpleNamespace:
  return SimpleNamespace(
    data={
      **create_user_input(target_entity_id),
      CONFIG_KIND: CONFIG_KIND_COST_TRACKER,
      CONFIG_ACCOUNT_ID: "A-TEST",
    },
  )


def get_schema_fields(schema) -> set[str]:
  return {getattr(field, "schema", field) for field in schema.schema}


@pytest.mark.asyncio
async def test_discovery_flow_keeps_discovered_target_as_canonical_identity():
  flow = create_flow()
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
async def test_manual_cost_tracker_form_includes_target_entity():
  flow = create_flow()

  schema = await flow.__async_setup_cost_tracker_schema__("A-TEST")

  assert CONFIG_COST_TRACKER_TARGET_ENTITY_ID in get_schema_fields(schema)


@pytest.mark.asyncio
async def test_reconfigure_cost_tracker_form_hides_target_entity():
  flow = create_flow()
  flow._get_reconfigure_entry = Mock(
    return_value=create_config_entry("sensor.lounge_cooling_energy")
  )
  flow.async_show_form = Mock(return_value={"type": "form"})

  with patch(
    "custom_components.octopus_energy.config_flow.validate_cost_tracker_config",
    return_value={},
  ):
    await flow.async_step_reconfigure_cost_tracker(None)

  schema = flow.async_show_form.call_args.kwargs["data_schema"]
  assert CONFIG_COST_TRACKER_TARGET_ENTITY_ID not in get_schema_fields(schema)


@pytest.mark.asyncio
async def test_reconfigure_cost_tracker_preserves_existing_target_entity():
  flow = create_flow()
  config_entry = create_config_entry("sensor.lounge_cooling_energy")
  flow._get_reconfigure_entry = Mock(return_value=config_entry)
  flow.async_update_reload_and_abort = Mock(return_value={"type": "abort"})
  user_input = create_user_input("sensor.kitchen_heating_energy")

  with patch(
    "custom_components.octopus_energy.config_flow.validate_cost_tracker_config",
    return_value={},
  ):
    await flow.async_step_reconfigure_cost_tracker(user_input)

  data_updates = flow.async_update_reload_and_abort.call_args.kwargs["data_updates"]
  assert data_updates[CONFIG_COST_TRACKER_TARGET_ENTITY_ID] == "sensor.lounge_cooling_energy"
  assert "unique_id" not in flow.async_update_reload_and_abort.call_args.kwargs


@pytest.mark.parametrize(
  "old_unique_id",
  [
    None,
    "octopus_energy_ct_A-TEST_sensor.lounge_cooling_energy",
  ],
)
@pytest.mark.asyncio
async def test_migration_repairs_unique_id_from_canonical_target(old_unique_id):
  config_entry = SimpleNamespace(
    version=10,
    data={
      CONFIG_KIND: CONFIG_KIND_COST_TRACKER,
      CONFIG_ACCOUNT_ID: "A-TEST",
      CONFIG_COST_TRACKER_TARGET_ENTITY_ID: "sensor.kitchen_heating_energy",
    },
    options={},
    title="Kitchen heating (cost tracker)",
    unique_id=old_unique_id,
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
