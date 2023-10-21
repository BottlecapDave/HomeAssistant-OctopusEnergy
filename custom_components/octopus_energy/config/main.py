from ..const import (
  CONFIG_MAIN_ACCOUNT_ID,
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET,
  CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET,
  CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION
)
from ..api_client import OctopusEnergyApiClient

def merge_main_config(data: dict, options: dict, updated_config: dict = None):
  config = dict(data)
  if options is not None:
    config.update(options)

  if updated_config is not None:
    config.update(updated_config)

    if CONFIG_MAIN_ELECTRICITY_PRICE_CAP not in updated_config and CONFIG_MAIN_ELECTRICITY_PRICE_CAP in config:
      del config[CONFIG_MAIN_ELECTRICITY_PRICE_CAP]

    if CONFIG_MAIN_GAS_PRICE_CAP not in updated_config and CONFIG_MAIN_GAS_PRICE_CAP in config:
      del config[CONFIG_MAIN_GAS_PRICE_CAP]

  return config

async def async_validate_main_config(data):
  errors = {}

  client = OctopusEnergyApiClient(data[CONFIG_MAIN_API_KEY])
  account_info = await client.async_get_account(data[CONFIG_MAIN_ACCOUNT_ID])
  
  if (account_info is None):
    errors[CONFIG_MAIN_API_KEY] = "account_not_found"

  if data[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True:

    if data[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES] < 1:
      errors[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES] = "value_greater_than_zero"

    if data[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES] < 1:
      errors[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES] = "value_greater_than_zero"

  if data[CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET] < 1:
      errors[CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET] = "value_greater_than_zero"

  if data[CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET] < 1:
    errors[CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET] = "value_greater_than_zero"

  return errors