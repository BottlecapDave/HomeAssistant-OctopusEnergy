from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
import voluptuous as vol

from custom_components.octopus_energy.config.main import has_incompatible_account_child_entries
from custom_components.octopus_energy.config_flow import OctopusEnergyConfigFlow
from custom_components.octopus_energy.const import (
  CONFIG_ACCOUNT_ID,
  CONFIG_COST_TRACKER_TARGET_ENTITY_ID,
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_COST_TRACKER,
  CONFIG_KIND_TARIFF_COMPARISON,
  CONFIG_MAIN_CALORIFIC_VALUE,
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
  CONFIG_TARIFF_COMPARISON_MPAN_MPRN,
  CONFIG_TARIFF_COMPARISON_TARIFF_CODE,
  DATA_ACCOUNT,
  DOMAIN,
)


def get_schema_marker(schema, key):
  return next(marker for marker in schema.schema if marker.schema == key)


def create_entry(
  kind: str,
  account_id: str = "A-TEST",
  target: str | None = None,
  tariff_code: str | None = None,
):
  data = {
    CONFIG_KIND: kind,
    CONFIG_ACCOUNT_ID: account_id,
  }
  if kind == CONFIG_KIND_COST_TRACKER:
    data[CONFIG_COST_TRACKER_TARGET_ENTITY_ID] = target or "sensor.test"
  elif kind == CONFIG_KIND_TARIFF_COMPARISON:
    data[CONFIG_TARIFF_COMPARISON_MPAN_MPRN] = target
    if tariff_code is not None:
      data[CONFIG_TARIFF_COMPARISON_TARIFF_CODE] = tariff_code

  return SimpleNamespace(data=data)


def get_account_info():
  return {
    "electricity_meter_points": [{"mpan": "electricity-mpan"}],
    "gas_meter_points": [{"mprn": "gas-mprn"}],
  }


def test_account_schema_includes_required_supply_selection_and_optional_calorific_value():
  flow = OctopusEnergyConfigFlow()

  schema = flow.__setup_account_schema__()

  supplies_marker = get_schema_marker(schema, CONFIG_MAIN_SUPPLIES_TO_MONITOR)
  calorific_value_marker = get_schema_marker(schema, CONFIG_MAIN_CALORIFIC_VALUE)
  assert isinstance(supplies_marker, vol.Required)
  assert supplies_marker.default() == CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS
  assert isinstance(calorific_value_marker, vol.Optional)


def test_dual_supply_mode_is_compatible_with_all_child_entries():
  config = {
    CONFIG_KIND: CONFIG_KIND_ACCOUNT,
    CONFIG_ACCOUNT_ID: "A-TEST",
    CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  }
  entries = [
    create_entry(CONFIG_KIND_COST_TRACKER),
    create_entry(CONFIG_KIND_TARIFF_COMPARISON, target="electricity-mpan"),
    create_entry(CONFIG_KIND_TARIFF_COMPARISON, target="gas-mprn"),
  ]

  assert has_incompatible_account_child_entries(config, get_account_info(), entries) is False


def test_gas_only_mode_is_incompatible_with_cost_tracker():
  config = {
    CONFIG_ACCOUNT_ID: "A-TEST",
    CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
  }

  assert has_incompatible_account_child_entries(
    config,
    get_account_info(),
    [create_entry(CONFIG_KIND_COST_TRACKER)],
  ) is True


def test_single_supply_mode_is_incompatible_with_comparison_for_disabled_supply():
  electricity_config = {
    CONFIG_ACCOUNT_ID: "A-TEST",
    CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
  }
  gas_config = {
    CONFIG_ACCOUNT_ID: "A-TEST",
    CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
  }

  assert has_incompatible_account_child_entries(
    electricity_config,
    get_account_info(),
    [create_entry(CONFIG_KIND_TARIFF_COMPARISON, target="gas-mprn")],
  ) is True
  assert has_incompatible_account_child_entries(
    gas_config,
    get_account_info(),
    [create_entry(CONFIG_KIND_TARIFF_COMPARISON, target="electricity-mpan")],
  ) is True


def test_single_supply_mode_uses_tariff_code_when_meter_is_missing_from_account_snapshot():
  config = {
    CONFIG_ACCOUNT_ID: "A-TEST",
    CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
  }

  assert has_incompatible_account_child_entries(
    config,
    {"electricity_meter_points": [], "gas_meter_points": []},
    [create_entry(
      CONFIG_KIND_TARIFF_COMPARISON,
      target="missing-gas-mprn",
      tariff_code="G-1R-TEST-A",
    )],
  ) is True


def test_single_supply_mode_ignores_compatible_unrelated_and_unidentifiable_children():
  config = {
    CONFIG_ACCOUNT_ID: "A-TEST",
    CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
  }
  entries = [
    create_entry(CONFIG_KIND_TARIFF_COMPARISON, target="electricity-mpan"),
    create_entry(CONFIG_KIND_TARIFF_COMPARISON, target="unknown"),
    create_entry(CONFIG_KIND_TARIFF_COMPARISON, account_id="A-OTHER", target="gas-mprn"),
  ]

  assert has_incompatible_account_child_entries(config, get_account_info(), entries) is False


def create_reconfigure_flow(child_entries, include_runtime_account=True):
  account_id = "A-TEST"
  account_entry = SimpleNamespace(data={
    CONFIG_KIND: CONFIG_KIND_ACCOUNT,
    CONFIG_ACCOUNT_ID: account_id,
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  })
  config_entries = Mock()
  config_entries.async_entries.return_value = [account_entry, *child_entries]
  flow = OctopusEnergyConfigFlow()
  domain_data = {
    account_id: {
      DATA_ACCOUNT: SimpleNamespace(account=get_account_info()),
    }
  } if include_runtime_account else {}
  flow.hass = SimpleNamespace(
    data={DOMAIN: domain_data},
    config_entries=config_entries,
  )
  flow._get_reconfigure_entry = Mock(return_value=account_entry)
  flow.async_show_form = Mock(return_value={"type": "form"})
  flow.async_update_reload_and_abort = Mock(return_value={"type": "abort"})
  return flow


@pytest.mark.asyncio
async def test_reconfigure_account_blocks_supply_used_by_child_entry():
  # Arrange
  flow = create_reconfigure_flow([create_entry(CONFIG_KIND_COST_TRACKER)])

  # Act
  with patch(
    "custom_components.octopus_energy.config_flow.async_validate_main_config",
    new=AsyncMock(return_value={}),
  ):
    await flow.async_step_reconfigure_account({
      CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
    })

  # Assert
  errors = flow.async_show_form.call_args.kwargs["errors"]
  assert errors[CONFIG_MAIN_SUPPLIES_TO_MONITOR] == "incompatible_child_entries"
  flow.async_update_reload_and_abort.assert_not_called()


@pytest.mark.asyncio
async def test_reconfigure_account_updates_when_children_are_compatible():
  # Arrange
  flow = create_reconfigure_flow([
    create_entry(CONFIG_KIND_TARIFF_COMPARISON, target="electricity-mpan"),
  ])

  # Act
  with patch(
    "custom_components.octopus_energy.config_flow.async_validate_main_config",
    new=AsyncMock(return_value={}),
  ):
    await flow.async_step_reconfigure_account({
      CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
    })

  # Assert
  flow.async_update_reload_and_abort.assert_called_once()
  data_updates = flow.async_update_reload_and_abort.call_args.kwargs["data_updates"]
  assert data_updates[CONFIG_MAIN_SUPPLIES_TO_MONITOR] == CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY


@pytest.mark.asyncio
async def test_reconfigure_account_handles_unloaded_runtime_account():
  flow = create_reconfigure_flow([], include_runtime_account=False)

  with patch(
    "custom_components.octopus_energy.config_flow.async_validate_main_config",
    new=AsyncMock(return_value={}),
  ):
    await flow.async_step_reconfigure_account({
      CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
    })

  flow.async_update_reload_and_abort.assert_called_once()


@pytest.mark.asyncio
async def test_reconfigure_account_can_clear_existing_calorific_value():
  flow = create_reconfigure_flow([])
  flow._get_reconfigure_entry.return_value.data[CONFIG_MAIN_CALORIFIC_VALUE] = 39.5

  with patch(
    "custom_components.octopus_energy.config_flow.async_validate_main_config",
    new=AsyncMock(return_value={}),
  ):
    await flow.async_step_reconfigure_account({
      CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
    })

  data_updates = flow.async_update_reload_and_abort.call_args.kwargs["data_updates"]
  assert CONFIG_MAIN_CALORIFIC_VALUE not in data_updates
