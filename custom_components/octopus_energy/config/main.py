from ..const import (
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_ACCOUNT_ID,
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_OLD_ACCOUNT_ID,
  CONFIG_MAIN_OLD_API_KEY,
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

  return new_data

def merge_main_config(data: dict, options: dict, updated_config: dict = None):
  config = dict(data)
  if options is not None:
    config.update(options)

  if updated_config is not None:
    config.update(updated_config)

    # This is the only way to set the unsetting of data
    if CONFIG_MAIN_ELECTRICITY_PRICE_CAP not in updated_config and CONFIG_MAIN_ELECTRICITY_PRICE_CAP in config:
      config[CONFIG_MAIN_ELECTRICITY_PRICE_CAP] = None

    if CONFIG_MAIN_GAS_PRICE_CAP not in updated_config and CONFIG_MAIN_GAS_PRICE_CAP in config:
      config[CONFIG_MAIN_GAS_PRICE_CAP] = None

    if CONFIG_MAIN_HOME_PRO_ADDRESS not in updated_config and CONFIG_MAIN_HOME_PRO_ADDRESS in config:
      config[CONFIG_MAIN_HOME_PRO_ADDRESS] = None

    if CONFIG_MAIN_HOME_PRO_API_KEY not in updated_config and CONFIG_MAIN_HOME_PRO_API_KEY in config:
      config[CONFIG_MAIN_HOME_PRO_API_KEY] = None

  return config

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

  if data[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True:

    if data[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES] < 1:
      errors[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES] = "value_greater_than_zero"

    if data[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES] < 1:
      errors[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES] = "value_greater_than_zero"

  if ((CONFIG_MAIN_HOME_PRO_API_KEY in data and
       data[CONFIG_MAIN_HOME_PRO_API_KEY] is not None and
       (CONFIG_MAIN_HOME_PRO_ADDRESS not in data or data[CONFIG_MAIN_HOME_PRO_ADDRESS] is None))):
    errors[CONFIG_MAIN_HOME_PRO_ADDRESS] = "all_home_pro_values_not_set"

  if (CONFIG_MAIN_HOME_PRO_ADDRESS in data and
      data[CONFIG_MAIN_HOME_PRO_ADDRESS] is not None and
      CONFIG_MAIN_HOME_PRO_API_KEY in data and
      data[CONFIG_MAIN_HOME_PRO_API_KEY] is not None):
    home_pro_client = OctopusEnergyHomeProApiClient(data[CONFIG_MAIN_HOME_PRO_ADDRESS], data[CONFIG_MAIN_HOME_PRO_API_KEY] if CONFIG_MAIN_HOME_PRO_API_KEY in data else None)

    try:
      can_connect = await home_pro_client.async_ping()
      if can_connect == False:
        errors[CONFIG_MAIN_HOME_PRO_ADDRESS] = "home_pro_not_responding"
    except AuthenticationException:
      errors[CONFIG_MAIN_HOME_PRO_ADDRESS] = "home_pro_authentication_failed"
    except:
      errors[CONFIG_MAIN_HOME_PRO_ADDRESS] = "home_pro_connection_failed"

  return errors