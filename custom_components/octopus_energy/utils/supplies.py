from ..const import (
  CONFIG_MAIN_SUPPLIES_TO_MONITOR,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
)


def get_supplies_to_monitor(config: dict) -> str:
  """Return the configured supplies, defaulting to the existing behaviour."""
  supplies = config.get(
    CONFIG_MAIN_SUPPLIES_TO_MONITOR,
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  )

  if supplies not in (
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  ):
    return CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS

  return supplies


def supports_electricity(config: dict) -> bool:
  """Return whether electricity supplies should be monitored."""
  return get_supplies_to_monitor(config) in (
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  )


def supports_gas(config: dict) -> bool:
  """Return whether gas supplies should be monitored."""
  return get_supplies_to_monitor(config) in (
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  )


def filter_account_info(account_info: dict | None, config: dict) -> dict | None:
  """Return an account view containing only the configured meter supplies."""
  if account_info is None:
    return None

  filtered_account_info = {**account_info}
  if supports_electricity(config) == False:
    filtered_account_info["electricity_meter_points"] = []
  if supports_gas(config) == False:
    filtered_account_info["gas_meter_points"] = []

  return filtered_account_info
