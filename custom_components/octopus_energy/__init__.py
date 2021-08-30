import logging
from datetime import timedelta
from homeassistant.util.dt import utcnow

from .const import (
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_TARIFF,
  CONFIG_MAIN_TARIFF_CODE,

  DATA_CLIENT,
  DATA_COORDINATOR,
  DATA_RATES
)

from .api_client import OctopusEnergyApiClient

from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

_LOGGER = logging.getLogger(__name__)

def setup_dependencies(hass, config):
  """Setup the coordinator and api client which will be shared by various entities"""
  client = OctopusEnergyApiClient(config[CONFIG_MAIN_API_KEY], config[CONFIG_MAIN_TARIFF])
  hass.data[DOMAIN][DATA_CLIENT] = client

  async def async_update_data():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    if (DATA_RATES not in hass.data[DOMAIN] or (utcnow().minute % 30) == 0):
      _LOGGER.info('Updating rates...')
      hass.data[DOMAIN][DATA_RATES] = await client.async_get_rates('AGILE-18-02-21', config[CONFIG_MAIN_TARIFF_CODE])
    
    return hass.data[DOMAIN][DATA_RATES]

  hass.data[DOMAIN][DATA_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="rates",
    update_method=async_update_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""

  hass.data.setdefault(DOMAIN, {})

  if CONFIG_MAIN_API_KEY in entry.data:
    setup_dependencies(hass, entry.data)

  # Forward our entry to setup our default sensors
  hass.async_create_task(
    hass.config_entries.async_forward_entry_setup(entry, "sensor")
  )

  return True