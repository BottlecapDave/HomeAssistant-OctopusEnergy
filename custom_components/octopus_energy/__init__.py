import logging
import asyncio
from datetime import timedelta

from homeassistant.exceptions import ConfigEntryNotReady

from .coordinators.account import async_setup_account_info_coordinator
from .coordinators.intelligent_dispatches import async_setup_intelligent_dispatches_coordinator
from .coordinators.intelligent_settings import async_setup_intelligent_settings_coordinator
from .coordinators.electricity_rates import async_setup_electricity_rates_coordinator
from .coordinators.saving_sessions import async_setup_saving_sessions_coordinators

from .const import (
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ACCOUNT_ID,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,
  
  CONFIG_TARGET_NAME,

  DATA_CLIENT,
  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_ACCOUNT_ID,
  DATA_ACCOUNT
)

from .api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""
  hass.data.setdefault(DOMAIN, {})

  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  if CONFIG_MAIN_API_KEY in config:
    await async_setup_dependencies(hass, config)

    # Forward our entry to setup our default sensors
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )

    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "text")
    )

    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "number")
    )

    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "switch")
    )

    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "time")
    )
  elif CONFIG_TARGET_NAME in config:
    if DOMAIN not in hass.data or DATA_ELECTRICITY_RATES_COORDINATOR not in hass.data[DOMAIN] or DATA_ACCOUNT not in hass.data[DOMAIN]:
      raise ConfigEntryNotReady

    # Forward our entry to setup our target rate sensors
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )
  
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

  hass.data[DOMAIN][DATA_ACCOUNT] = account_info

  await async_setup_account_info_coordinator(hass, config[CONFIG_MAIN_ACCOUNT_ID])

  await async_setup_intelligent_dispatches_coordinator(hass, config[CONFIG_MAIN_ACCOUNT_ID])

  await async_setup_intelligent_settings_coordinator(hass, config[CONFIG_MAIN_ACCOUNT_ID])
  
  await async_setup_electricity_rates_coordinator(hass, config[CONFIG_MAIN_ACCOUNT_ID])

  await async_setup_saving_sessions_coordinators(hass)

async def options_update_listener(hass, entry):
  """Handle options update."""
  await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    """Unload a config entry."""

    unload_ok = False
    if CONFIG_MAIN_API_KEY in entry.data:
      unload_ok = all(
        await asyncio.gather(
            *[
              hass.config_entries.async_forward_entry_unload(entry, "sensor"),
              hass.config_entries.async_forward_entry_unload(entry, "binary_sensor"),
              hass.config_entries.async_forward_entry_unload(entry, "text"),
              hass.config_entries.async_forward_entry_unload(entry, "number"),
              hass.config_entries.async_forward_entry_unload(entry, "switch"),
              hass.config_entries.async_forward_entry_unload(entry, "time")
             ]
        )
      )
    elif CONFIG_TARGET_NAME in entry.data:
      unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")]
        )
      )

    return unload_ok