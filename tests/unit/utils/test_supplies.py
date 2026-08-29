from copy import deepcopy

import pytest

from custom_components.octopus_energy.const import (
  CONFIG_MAIN_SUPPLIES_TO_MONITOR,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
)
from custom_components.octopus_energy.utils.supplies import (
  filter_account_info,
  get_supplies_to_monitor,
  supports_electricity,
  supports_gas,
)


@pytest.mark.parametrize(
  "config",
  [
    {},
    {CONFIG_MAIN_SUPPLIES_TO_MONITOR: "invalid"},
    {CONFIG_MAIN_SUPPLIES_TO_MONITOR: None},
  ],
)
def test_get_supplies_to_monitor_when_value_missing_or_invalid_then_dual_fuel_returned(config):
  assert get_supplies_to_monitor(config) == CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS


@pytest.mark.parametrize(
  "supplies_to_monitor,supports_electricity_result,supports_gas_result",
  [
    (CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY, True, False),
    (CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS, False, True),
    (CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS, True, True),
  ],
)
def test_when_supplies_configured_then_support_is_reported(
  supplies_to_monitor,
  supports_electricity_result,
  supports_gas_result,
):
  config = {CONFIG_MAIN_SUPPLIES_TO_MONITOR: supplies_to_monitor}

  assert get_supplies_to_monitor(config) == supplies_to_monitor
  assert supports_electricity(config) is supports_electricity_result
  assert supports_gas(config) is supports_gas_result


def test_filter_account_info_when_account_is_none_then_none_returned():
  assert filter_account_info(None, {}) is None


@pytest.mark.parametrize(
  "supplies_to_monitor,expected_electricity_meter_points,expected_gas_meter_points",
  [
    (
      CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
      [{"mpan": "electricity-meter"}],
      [],
    ),
    (
      CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
      [],
      [{"mprn": "gas-meter"}],
    ),
    (
      CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
      [{"mpan": "electricity-meter"}],
      [{"mprn": "gas-meter"}],
    ),
    (
      "invalid",
      [{"mpan": "electricity-meter"}],
      [{"mprn": "gas-meter"}],
    ),
  ],
)
def test_filter_account_info_returns_selected_supplies_without_mutating_source(
  supplies_to_monitor,
  expected_electricity_meter_points,
  expected_gas_meter_points,
):
  account_info = {
    "id": "A-TEST",
    "octoplus_enrolled": True,
    "property_ids": ["property-1"],
    "electricity_meter_points": [{"mpan": "electricity-meter"}],
    "gas_meter_points": [{"mprn": "gas-meter"}],
    "additional_data": {"preserved": True},
  }
  original_account_info = deepcopy(account_info)

  result = filter_account_info(
    account_info,
    {CONFIG_MAIN_SUPPLIES_TO_MONITOR: supplies_to_monitor},
  )

  assert result is not account_info
  assert result["electricity_meter_points"] == expected_electricity_meter_points
  assert result["gas_meter_points"] == expected_gas_meter_points
  assert result["id"] == "A-TEST"
  assert result["octoplus_enrolled"] is True
  assert result["property_ids"] == ["property-1"]
  assert result["additional_data"] == {"preserved": True}
  assert account_info == original_account_info
