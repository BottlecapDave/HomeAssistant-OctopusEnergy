import re
from ..const import (
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_COST_TRACKER,
  CONFIG_KIND_TARIFF_COMPARISON,
  CONFIG_ACCOUNT_ID,
  CONFIG_TARIFF_COMPARISON_MPAN_MPRN,
  CONFIG_TARIFF_COMPARISON_TARIFF_CODE,
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,
  CONFIG_MAIN_HOME_MINI_SETTINGS,
  CONFIG_MAIN_HOME_PRO_SETTINGS,
  CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES,
  CONFIG_MAIN_INTELLIGENT_RATE_MODE,
  CONFIG_MAIN_INTELLIGENT_SETTINGS,
  CONFIG_MAIN_LEGACY_SAVING_SESSIONS_FREE_ELECTRICITY_PRESENT,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_OLD_ACCOUNT_ID,
  CONFIG_MAIN_OLD_API_KEY,
  CONFIG_MAIN_PRICE_CAP_SETTINGS,
  CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
  CONFIG_MAIN_HOME_PRO_ADDRESS,
  CONFIG_MAIN_HOME_PRO_API_KEY
)
from ..api_client import AuthenticationException, OctopusEnergyApiClient, RequestException, ServerException
from ..api_client_home_pro import OctopusEnergyHomeProApiClient


def has_incompatible_account_child_entries(config: dict, account_info: dict | None, entries: list) -> bool:
  """Return whether child entries use a supply that would be disabled."""
  supplies_to_monitor = config.get(
    CONFIG_MAIN_SUPPLIES_TO_MONITOR,
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  )
  if supplies_to_monitor == CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS:
    return False

  electricity_meter_points = account_info.get("electricity_meter_points", []) if account_info is not None else []
  gas_meter_points = account_info.get("gas_meter_points", []) if account_info is not None else []
  electricity_mpans = {point["mpan"] for point in electricity_meter_points}
  gas_mprns = {point["mprn"] for point in gas_meter_points}

  for entry in entries:
    entry_config = entry.data
    if entry_config.get(CONFIG_ACCOUNT_ID) != config.get(CONFIG_ACCOUNT_ID):
      continue

    if (supplies_to_monitor == CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS and
        entry_config.get(CONFIG_KIND) == CONFIG_KIND_COST_TRACKER):
      return True

    if entry_config.get(CONFIG_KIND) == CONFIG_KIND_TARIFF_COMPARISON:
      target = entry_config.get(CONFIG_TARIFF_COMPARISON_MPAN_MPRN)
      tariff_code = entry_config.get(CONFIG_TARIFF_COMPARISON_TARIFF_CODE, "")
      is_electricity = target in electricity_mpans or tariff_code.startswith("E-")
      is_gas = target in gas_mprns or tariff_code.startswith("G-")
      if (supplies_to_monitor == CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS and
          is_electricity):
        return True
      if (supplies_to_monitor == CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY and
          is_gas):
        return True

  return False

async def async_migrate_main_config(version: int, data: {}):
  new_data = {**data}

  if (version <= 1):
    new_data[CONFIG_KIND] = CONFIG_KIND_ACCOUNT

    if "live_consumption_refresh_in_minutes" in new_data:
      new_data[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES] = new_data["live_consumption_refresh_in_minutes"]
      new_data[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES] = new_data["live_consumption_refresh_in_minutes"]

  if (version <= 2):
    new_data[CONFIG_KIND] = CONFIG_KIND_ACCOUNT

    if CONFIG_MAIN_OLD_API_KEY in new_data:
      new_data[CONFIG_MAIN_API_KEY] = new_data[CONFIG_MAIN_OLD_API_KEY]
      del new_data[CONFIG_MAIN_OLD_API_KEY]

    if CONFIG_MAIN_OLD_ACCOUNT_ID in new_data:
      new_data[CONFIG_ACCOUNT_ID] = new_data[CONFIG_MAIN_OLD_ACCOUNT_ID]
      del new_data[CONFIG_MAIN_OLD_ACCOUNT_ID]

  if (version <= 5):
    if CONFIG_MAIN_HOME_PRO_ADDRESS in new_data:
      new_data[CONFIG_MAIN_HOME_PRO_ADDRESS] = f"{new_data[CONFIG_MAIN_HOME_PRO_ADDRESS]}".replace(":8000", "")

  if (version <= 6):
    if (CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in new_data or 
        CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES in new_data or
        CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES in new_data):
      new_data[CONFIG_MAIN_HOME_MINI_SETTINGS] = {}

      if CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in new_data:
        new_data[CONFIG_MAIN_HOME_MINI_SETTINGS][CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] = new_data[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION]
        del new_data[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION]

      if CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES in new_data:
        new_data[CONFIG_MAIN_HOME_MINI_SETTINGS][CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES] = new_data[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES]
        del new_data[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES]

      if CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES in new_data:
        new_data[CONFIG_MAIN_HOME_MINI_SETTINGS][CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES] = new_data[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES]
        del new_data[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES]

    if (CONFIG_MAIN_HOME_PRO_ADDRESS in new_data or CONFIG_MAIN_HOME_PRO_API_KEY in new_data):
      
      new_data[CONFIG_MAIN_HOME_PRO_SETTINGS] = {}

      if CONFIG_MAIN_HOME_PRO_ADDRESS in new_data:
        new_data[CONFIG_MAIN_HOME_PRO_SETTINGS][CONFIG_MAIN_HOME_PRO_ADDRESS] = new_data[CONFIG_MAIN_HOME_PRO_ADDRESS]
        del new_data[CONFIG_MAIN_HOME_PRO_ADDRESS]

      if CONFIG_MAIN_HOME_PRO_API_KEY in new_data:
        new_data[CONFIG_MAIN_HOME_PRO_SETTINGS][CONFIG_MAIN_HOME_PRO_API_KEY] = new_data[CONFIG_MAIN_HOME_PRO_API_KEY]
        del new_data[CONFIG_MAIN_HOME_PRO_API_KEY]

    if CONFIG_MAIN_ELECTRICITY_PRICE_CAP in new_data or CONFIG_MAIN_GAS_PRICE_CAP in new_data:
      new_data[CONFIG_MAIN_PRICE_CAP_SETTINGS] = {}

      if CONFIG_MAIN_ELECTRICITY_PRICE_CAP in new_data:
        new_data[CONFIG_MAIN_PRICE_CAP_SETTINGS][CONFIG_MAIN_ELECTRICITY_PRICE_CAP] = new_data[CONFIG_MAIN_ELECTRICITY_PRICE_CAP]
        del new_data[CONFIG_MAIN_ELECTRICITY_PRICE_CAP]

      if CONFIG_MAIN_GAS_PRICE_CAP in new_data:
        new_data[CONFIG_MAIN_PRICE_CAP_SETTINGS][CONFIG_MAIN_GAS_PRICE_CAP] = new_data[CONFIG_MAIN_GAS_PRICE_CAP]
        del new_data[CONFIG_MAIN_GAS_PRICE_CAP]

    if CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES in new_data or CONFIG_MAIN_INTELLIGENT_RATE_MODE in new_data:
      new_data[CONFIG_MAIN_INTELLIGENT_SETTINGS] = {}

      if CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES in new_data:
        new_data[CONFIG_MAIN_INTELLIGENT_SETTINGS][CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES] = new_data[CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES]
        del new_data[CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES]

      if CONFIG_MAIN_INTELLIGENT_RATE_MODE in new_data:
        new_data[CONFIG_MAIN_INTELLIGENT_SETTINGS][CONFIG_MAIN_INTELLIGENT_RATE_MODE] = new_data[CONFIG_MAIN_INTELLIGENT_RATE_MODE]
        del new_data[CONFIG_MAIN_INTELLIGENT_RATE_MODE]

  if (version <= 7):
    if (CONFIG_MAIN_HOME_PRO_SETTINGS in new_data and
        CONFIG_MAIN_HOME_PRO_ADDRESS in new_data[CONFIG_MAIN_HOME_PRO_SETTINGS]):
      
      matches = re.search(r"^http://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$", new_data[CONFIG_MAIN_HOME_PRO_SETTINGS][CONFIG_MAIN_HOME_PRO_ADDRESS]) if new_data[CONFIG_MAIN_HOME_PRO_SETTINGS][CONFIG_MAIN_HOME_PRO_ADDRESS] is not None else None
      if matches is None:
        del new_data[CONFIG_MAIN_HOME_PRO_SETTINGS]

  if (version <= 9):
    new_data[CONFIG_MAIN_LEGACY_SAVING_SESSIONS_FREE_ELECTRICITY_PRESENT] = True

  if (version <= 12 and CONFIG_MAIN_SUPPLIES_TO_MONITOR not in new_data):
    new_data[CONFIG_MAIN_SUPPLIES_TO_MONITOR] = CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS

  return new_data

async def async_validate_main_config(data, account_ids = []):
  errors = {}

  supplies_to_monitor = data.get(
    CONFIG_MAIN_SUPPLIES_TO_MONITOR,
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  )
  if supplies_to_monitor not in (
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
    CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  ):
    errors[CONFIG_MAIN_SUPPLIES_TO_MONITOR] = "invalid_supplies_to_monitor"

  if data[CONFIG_ACCOUNT_ID] in account_ids:
    errors[CONFIG_ACCOUNT_ID] = "duplicate_account"
    return errors
  
  if CONFIG_MAIN_API_KEY not in data:
    errors[CONFIG_MAIN_API_KEY] = "api_key_not_set"
    return errors
  
  client = OctopusEnergyApiClient(data[CONFIG_MAIN_API_KEY])
  account_info = None

  try:
    account_info = await client.async_get_account(data[CONFIG_ACCOUNT_ID])
  except RequestException:
    # Treat errors as not finding the account
    account_info = None
  except ServerException:
    errors[CONFIG_MAIN_API_KEY] = "server_error"
  
  if (CONFIG_MAIN_API_KEY not in errors and account_info is None):
    errors[CONFIG_MAIN_API_KEY] = "account_not_found"

  if account_info is not None:
    if (supplies_to_monitor == CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY and
        len(account_info.get("electricity_meter_points", [])) < 1):
      errors[CONFIG_MAIN_SUPPLIES_TO_MONITOR] = "selected_supply_not_found"
    elif (supplies_to_monitor == CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS and
          len(account_info.get("gas_meter_points", [])) < 1):
      errors[CONFIG_MAIN_SUPPLIES_TO_MONITOR] = "selected_supply_not_found"

  if (CONFIG_MAIN_HOME_MINI_SETTINGS in data and 
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in data[CONFIG_MAIN_HOME_MINI_SETTINGS] and
      data[CONFIG_MAIN_HOME_MINI_SETTINGS][CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True):
    errors[CONFIG_MAIN_HOME_MINI_SETTINGS] = {}

    if (CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES in data[CONFIG_MAIN_HOME_MINI_SETTINGS] and 
        data[CONFIG_MAIN_HOME_MINI_SETTINGS][CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES] < 1):
      errors[CONFIG_MAIN_HOME_MINI_SETTINGS][CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES] = "value_greater_than_zero"

    if (CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES in data[CONFIG_MAIN_HOME_MINI_SETTINGS] and 
        data[CONFIG_MAIN_HOME_MINI_SETTINGS][CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES] < 1):
      errors[CONFIG_MAIN_HOME_MINI_SETTINGS][CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES] = "value_greater_than_zero"

    if len(errors[CONFIG_MAIN_HOME_MINI_SETTINGS]) < 1:
      del errors[CONFIG_MAIN_HOME_MINI_SETTINGS]

  if CONFIG_MAIN_HOME_PRO_SETTINGS in data:
    if ((CONFIG_MAIN_HOME_PRO_API_KEY in data[CONFIG_MAIN_HOME_PRO_SETTINGS] and
        data[CONFIG_MAIN_HOME_PRO_SETTINGS][CONFIG_MAIN_HOME_PRO_API_KEY] is not None and
        (CONFIG_MAIN_HOME_PRO_ADDRESS not in data[CONFIG_MAIN_HOME_PRO_SETTINGS] or data[CONFIG_MAIN_HOME_PRO_SETTINGS][CONFIG_MAIN_HOME_PRO_ADDRESS] is None))):
      errors[CONFIG_MAIN_HOME_PRO_SETTINGS] = "all_home_pro_values_not_set"

    if (CONFIG_MAIN_HOME_PRO_ADDRESS in data[CONFIG_MAIN_HOME_PRO_SETTINGS] and
        data[CONFIG_MAIN_HOME_PRO_SETTINGS][CONFIG_MAIN_HOME_PRO_ADDRESS] is not None):
      home_pro_client = OctopusEnergyHomeProApiClient(
        data[CONFIG_MAIN_HOME_PRO_SETTINGS][CONFIG_MAIN_HOME_PRO_ADDRESS],
        data[CONFIG_MAIN_HOME_PRO_SETTINGS][CONFIG_MAIN_HOME_PRO_API_KEY] 
        if CONFIG_MAIN_HOME_PRO_API_KEY in data[CONFIG_MAIN_HOME_PRO_SETTINGS]
        else None
      )

      try:
        can_connect = await home_pro_client.async_ping()
        if can_connect == False:
          errors[CONFIG_MAIN_HOME_PRO_SETTINGS] = "home_pro_not_responding"
      except AuthenticationException:
        errors[CONFIG_MAIN_HOME_PRO_SETTINGS] = "home_pro_authentication_failed"
      except:
        errors[CONFIG_MAIN_HOME_PRO_SETTINGS] = "home_pro_connection_failed"

  return errors
