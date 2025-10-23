import re
from ..const import (
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_ACCOUNT_ID,
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,
  CONFIG_MAIN_HOME_MINI_SETTINGS,
  CONFIG_MAIN_HOME_PRO_SETTINGS,
  CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES,
  CONFIG_MAIN_INTELLIGENT_RATE_MODE,
  CONFIG_MAIN_INTELLIGENT_SETTINGS,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_OLD_ACCOUNT_ID,
  CONFIG_MAIN_OLD_API_KEY,
  CONFIG_MAIN_PRICE_CAP_SETTINGS,
  CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION,
  CONFIG_MAIN_HOME_PRO_ADDRESS,
  CONFIG_MAIN_HOME_PRO_API_KEY
)
from ..api_client import AuthenticationException, OctopusEnergyApiClient, RequestException, ServerException
from ..api_client_home_pro import OctopusEnergyHomeProApiClient

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

  return new_data

async def async_validate_main_config(data, account_ids = []):
  errors = {}

  if data[CONFIG_ACCOUNT_ID] in account_ids:
    errors[CONFIG_ACCOUNT_ID] = "duplicate_account"
    return errors
  
  if CONFIG_MAIN_API_KEY not in data:
    errors[CONFIG_MAIN_API_KEY] = "api_key_not_set"
    return errors
  
  client = OctopusEnergyApiClient(data[CONFIG_MAIN_API_KEY])

  try:
    account_info = await client.async_get_account(data[CONFIG_ACCOUNT_ID])
  except RequestException:
    # Treat errors as not finding the account
    account_info = None
  except ServerException:
    errors[CONFIG_MAIN_API_KEY] = "server_error"
  
  if (CONFIG_MAIN_API_KEY not in errors and account_info is None):
    errors[CONFIG_MAIN_API_KEY] = "account_not_found"

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
