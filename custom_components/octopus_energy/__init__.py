import logging
from datetime import timedelta
from homeassistant.util.dt import (utcnow, as_utc, parse_datetime)
import asyncio

from .const import (
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ACCOUNT_ID,
  
  CONFIG_TARGET_NAME,

  DATA_CLIENT,
  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_RATES,
  DATA_ELECTRICITY_TARIFF_CODE
)

from .api_client import OctopusEnergyApiClient

from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from .utils import (
  get_active_tariff_code
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""
  hass.data.setdefault(DOMAIN, {})

  if CONFIG_MAIN_API_KEY in entry.data:
    setup_dependencies(hass, entry.data)

    # Forward our entry to setup our default sensors
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
  elif CONFIG_TARGET_NAME in entry.data:
    # Forward our entry to setup our target rate sensors
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )
  
  entry.async_on_unload(entry.add_update_listener(options_update_listener))

  return True

async def async_get_current_electricity_agreement_tariff_code(client, config):
  account_info = await client.async_get_account(config[CONFIG_MAIN_ACCOUNT_ID])

  all_agreements = []
  if len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      all_agreements.extend(point["agreements"])
      active_tariff_code = get_active_tariff_code(point["agreements"])
      if active_tariff_code != None:
        return active_tariff_code
  
  raise Exception(f'Unable to find active agreement: {all_agreements}')

def setup_dependencies(hass, config):
  """Setup the coordinator and api client which will be shared by various entities"""

  if DATA_CLIENT not in hass.data[DOMAIN]:
    client = OctopusEnergyApiClient(config[CONFIG_MAIN_API_KEY])
    hass.data[DOMAIN][DATA_CLIENT] = client

    async def async_update_electricity_rates_data():
      """Fetch data from API endpoint."""
      # Only get data every half hour or if we don't have any data
      if (DATA_RATES not in hass.data[DOMAIN] or (utcnow().minute % 30) == 0 or len(hass.data[DOMAIN][DATA_RATES]) == 0):

        tariff_code = await async_get_current_electricity_agreement_tariff_code(client, config)
        hass.data[DOMAIN][DATA_ELECTRICITY_TARIFF_CODE] = tariff_code
        _LOGGER.info(f'tariff_code: {tariff_code}')

        utc_now = utcnow()
        period_from = as_utc(parse_datetime(utc_now.strftime("%Y-%m-%dT00:00:00Z")))
        period_to = as_utc(parse_datetime((utc_now + timedelta(days=2)).strftime("%Y-%m-%dT00:00:00Z")))

        hass.data[DOMAIN][DATA_RATES] = await client.async_get_electricity_rates(tariff_code, period_from, period_to)
      
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