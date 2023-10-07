import logging
import asyncio
from datetime import timedelta
from custom_components.octopus_energy.utils import get_active_tariff_code

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.components.recorder import get_instance
from homeassistant.util.dt import (utcnow)

from .coordinators.account import async_setup_account_info_coordinator
from .coordinators.intelligent_dispatches import async_setup_intelligent_dispatches_coordinator
from .coordinators.intelligent_settings import async_setup_intelligent_settings_coordinator
from .coordinators.electricity_rates import async_setup_electricity_rates_coordinator
from .coordinators.saving_sessions import async_setup_saving_sessions_coordinators
from .statistics import get_statistic_ids_to_remove

from .const import (
  DOMAIN,

  CONFIG_KIND,
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ACCOUNT_ID,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  
  CONFIG_TARGET_NAME,

  DATA_CLIENT,
  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DATA_ACCOUNT_ID,
  DATA_ACCOUNT
)

ACCOUNT_PLATFORMS = ["sensor", "binary_sensor", "text", "number", "switch", "time", "event"]
TARGET_RATE_PLATFORMS = ["binary_sensor"]

from .api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_migrate_entry(hass, config_entry):
  """Migrate old entry."""
  _LOGGER.debug("Migrating from version %s", config_entry.version)

  if config_entry.version == 1:

    new = {**config_entry.data}

    if CONFIG_MAIN_ACCOUNT_ID in config_entry.data:
      new[CONFIG_KIND] = "account"

      if "live_consumption_refresh_in_minutes" in new:

        new[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES] = new["live_consumption_refresh_in_minutes"]
        new[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES] = new["live_consumption_refresh_in_minutes"]
    else:
      new[CONFIG_KIND] = "target_rate"

    config_entry.version = 2
    hass.config_entries.async_update_entry(config_entry, data=new)

  _LOGGER.debug("Migration to version %s successful", config_entry.version)

  return True

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""
  hass.data.setdefault(DOMAIN, {})

  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  if CONFIG_MAIN_API_KEY in config:
    await async_setup_dependencies(hass, config)

    await hass.config_entries.async_forward_entry_setups(entry, ACCOUNT_PLATFORMS)
  elif CONFIG_TARGET_NAME in config:
    if DOMAIN not in hass.data or DATA_ACCOUNT not in hass.data[DOMAIN]:
      raise ConfigEntryNotReady("Account has not been setup")
    
    now = utcnow()
    account_info = hass.data[DOMAIN][DATA_ACCOUNT]
    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      electricity_tariff_code = get_active_tariff_code(now, point["agreements"])
      if electricity_tariff_code is not None:
        for meter in point["meters"]:
          mpan = point["mpan"]
          serial_number = meter["serial_number"]
          electricity_rates_coordinator_key = DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number)
          if electricity_rates_coordinator_key not in hass.data[DOMAIN]:
            raise ConfigEntryNotReady(f"Electricity rates have not been setup for {mpan}/{serial_number}")

    await hass.config_entries.async_forward_entry_setups(entry, TARGET_RATE_PLATFORMS)
  
  entry.async_on_unload(entry.add_update_listener(options_update_listener))

  return True

async def async_setup_dependencies(hass, config):
  """Setup the coordinator and api client which will be shared by various entities"""

  electricity_price_cap = None
  if CONFIG_MAIN_ELECTRICITY_PRICE_CAP in config:
    electricity_price_cap = config[CONFIG_MAIN_ELECTRICITY_PRICE_CAP]

  gas_price_cap = None
  if CONFIG_MAIN_GAS_PRICE_CAP in config:
    gas_price_cap = config[CONFIG_MAIN_GAS_PRICE_CAP]

  _LOGGER.info(f'electricity_price_cap: {electricity_price_cap}')
  _LOGGER.info(f'gas_price_cap: {gas_price_cap}')

  client = OctopusEnergyApiClient(config[CONFIG_MAIN_API_KEY], electricity_price_cap, gas_price_cap)
  hass.data[DOMAIN][DATA_CLIENT] = client
  hass.data[DOMAIN][DATA_ACCOUNT_ID] = config[CONFIG_MAIN_ACCOUNT_ID]

  account_info = await client.async_get_account(config[CONFIG_MAIN_ACCOUNT_ID])
  if (account_info is None):
    raise ConfigEntryNotReady(f"Failed to retrieve account information")

  hass.data[DOMAIN][DATA_ACCOUNT] = account_info

  # Remove gas meter devices which had incorrect identifier
  if account_info is not None and len(account_info["gas_meter_points"]) > 0:
    device_registry = dr.async_get(hass)
    for point in account_info["gas_meter_points"]:
      mprn = point["mprn"]
      for meter in point["meters"]:
        serial_number = meter["serial_number"]
        device = device_registry.async_get_device(identifiers={(DOMAIN, f"electricity_{serial_number}_{mprn}")})
        if device is not None:
          device_registry.async_remove_device(device.id)

  now = utcnow()
  account_info = hass.data[DOMAIN][DATA_ACCOUNT]
  for point in account_info["electricity_meter_points"]:
    # We only care about points that have active agreements
    electricity_tariff_code = get_active_tariff_code(now, point["agreements"])
    if electricity_tariff_code is not None:
      for meter in point["meters"]:
        mpan = point["mpan"]
        serial_number = meter["serial_number"]
        is_export_meter = meter["is_export"]
        is_smart_meter = meter["is_smart_meter"]
        await async_setup_electricity_rates_coordinator(hass, mpan, serial_number, is_smart_meter, is_export_meter)

  await async_setup_account_info_coordinator(hass, config[CONFIG_MAIN_ACCOUNT_ID])

  await async_setup_intelligent_dispatches_coordinator(hass, config[CONFIG_MAIN_ACCOUNT_ID])

  await async_setup_intelligent_settings_coordinator(hass, config[CONFIG_MAIN_ACCOUNT_ID])
  
  await async_setup_saving_sessions_coordinators(hass)

async def options_update_listener(hass, entry):
  """Handle options update."""
  await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    """Unload a config entry."""

    unload_ok = False
    if CONFIG_MAIN_API_KEY in entry.data:
      unload_ok = await hass.config_entries.async_unload_platforms(entry, ACCOUNT_PLATFORMS)
    elif CONFIG_TARGET_NAME in entry.data:
      unload_ok = await hass.config_entries.async_unload_platforms(entry, TARGET_RATE_PLATFORMS)

    return unload_ok

def setup(hass, config):
  """Set up is called when Home Assistant is loading our component."""

  def purge_invalid_external_statistic_ids(call):
    """Handle the service call."""
      
    account_info = hass.data[DOMAIN][DATA_ACCOUNT]
    
    external_statistic_ids_to_remove = get_statistic_ids_to_remove(utcnow(), account_info)

    if len(external_statistic_ids_to_remove) > 0:
      get_instance(hass).async_clear_statistics(external_statistic_ids_to_remove)
      _LOGGER.debug(f'Removing the following external statistics: {external_statistic_ids_to_remove}')

  hass.services.register(DOMAIN, "purge_invalid_external_statistic_ids", purge_invalid_external_statistic_ids)

  # Return boolean to indicate that initialization was successful.
  return True