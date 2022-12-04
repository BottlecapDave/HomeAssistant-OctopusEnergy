import logging
from datetime import timedelta
import asyncio

from homeassistant.util.dt import (now, as_utc)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from .const import (
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ACCOUNT_ID,
  
  CONFIG_TARGET_NAME,

  DATA_CLIENT,
  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_RATES,
  DATA_ACCOUNT_ID,
  DATA_ACCOUNT,
  DATA_SAVING_SESSIONS,
  DATA_SAVING_SESSIONS_COORDINATOR
)

from .api_client import OctopusEnergyApiClient

from .utils import (
  get_active_tariff_code
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""
  hass.data.setdefault(DOMAIN, {})

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_dependencies(hass, entry.data)

    # Forward our entry to setup our default sensors
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )
  elif CONFIG_TARGET_NAME in entry.data:
    if DOMAIN not in hass.data or DATA_ELECTRICITY_RATES_COORDINATOR not in hass.data[DOMAIN] or DATA_ACCOUNT not in hass.data[DOMAIN]:
      raise ConfigEntryNotReady

    # Forward our entry to setup our target rate sensors
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )
  
  entry.async_on_unload(entry.add_update_listener(options_update_listener))

  return True

async def async_get_current_electricity_agreement_tariff_codes(client, config):
  account_info = await client.async_get_account(config[CONFIG_MAIN_ACCOUNT_ID])

  tariff_codes = {}
  current = now()
  if len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff_code = get_active_tariff_code(current, point["agreements"])
      # The type of meter (ie smart vs dumb) can change the tariff behaviour, so we
      # have to enumerate the different meters being used for each tariff as well.
      for meter in point["meters"]:
        is_smart_meter = meter["is_smart_meter"]
        if active_tariff_code != None:
          key = (point["mpan"], is_smart_meter)
          if key not in tariff_codes:
            tariff_codes[(point["mpan"], is_smart_meter)] = active_tariff_code
  
  return tariff_codes

async def async_setup_dependencies(hass, config):
  """Setup the coordinator and api client which will be shared by various entities"""

  if DATA_CLIENT not in hass.data[DOMAIN]:
    client = OctopusEnergyApiClient(config[CONFIG_MAIN_API_KEY])
    hass.data[DOMAIN][DATA_CLIENT] = client
    hass.data[DOMAIN][DATA_ACCOUNT_ID] = config[CONFIG_MAIN_ACCOUNT_ID]

    setup_rates_coordinator(hass, client, config)

    setup_saving_sessions_coordinators(hass, client)
 
    account_info = await client.async_get_account(config[CONFIG_MAIN_ACCOUNT_ID])

    hass.data[DOMAIN][DATA_ACCOUNT] = account_info

def setup_rates_coordinator(hass, client, config):
  async def async_update_electricity_rates_data():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    if (DATA_RATES not in hass.data[DOMAIN] or (current.minute % 30) == 0 or len(hass.data[DOMAIN][DATA_RATES]) == 0):

      tariff_codes = await async_get_current_electricity_agreement_tariff_codes(client, config)
      _LOGGER.debug(f'tariff_codes: {tariff_codes}')

      period_from = as_utc(current.replace(hour=0, minute=0, second=0, microsecond=0))
      period_to = as_utc((current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0))

      rates = {}
      for ((meter_point, is_smart_meter), tariff_code) in tariff_codes.items():
        key = meter_point
        new_rates = await client.async_get_electricity_rates(tariff_code, is_smart_meter, period_from, period_to)
        if new_rates != None:
          rates[key] = new_rates
        elif (DATA_RATES in hass.data[DOMAIN] and key in hass.data[DOMAIN][DATA_RATES]):
          _LOGGER.debug(f"Failed to retrieve new rates for {tariff_code}, so using cached rates")
          rates[key] = hass.data[DOMAIN][DATA_RATES][key]
      
      hass.data[DOMAIN][DATA_RATES] = rates
    
    return hass.data[DOMAIN][DATA_RATES]

  hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="rates",
    update_method=async_update_electricity_rates_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

def setup_saving_sessions_coordinators(hass, client: OctopusEnergyApiClient):
  async def async_update_saving_sessions():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    if DATA_SAVING_SESSIONS not in hass.data[DOMAIN] or current.minute % 30 == 0:
      savings = await client.async_get_saving_sessions(hass.data[DOMAIN][DATA_ACCOUNT_ID])
      
      hass.data[DOMAIN][DATA_SAVING_SESSIONS] = savings
    
    return hass.data[DOMAIN][DATA_SAVING_SESSIONS]

  hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="saving_sessions",
    update_method=async_update_saving_sessions,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

async def options_update_listener(hass, entry):
  """Handle options update."""
  await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    if CONFIG_MAIN_API_KEY in entry.data:
      target_domain = "sensor"
    elif CONFIG_TARGET_NAME in entry.data:
      target_domain = "binary_sensor"

    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, target_domain)]
        )
    )

    return unload_ok