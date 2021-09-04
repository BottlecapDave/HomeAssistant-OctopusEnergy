import logging
import re
from datetime import timedelta
from homeassistant.util.dt import utcnow

from .const import (
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ACCOUNT_ID,
  CONFIG_TARGET_NAME,

  DATA_CLIENT,
  DATA_COORDINATOR,
  DATA_RATES
)

from .api_client import OctopusEnergyApiClient

from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from .utils import get_active_agreement

_LOGGER = logging.getLogger(__name__)

def setup_dependencies(hass, config):
  """Setup the coordinator and api client which will be shared by various entities"""
  client = OctopusEnergyApiClient(config[CONFIG_MAIN_API_KEY])
  hass.data[DOMAIN][DATA_CLIENT] = client

  async def async_update_data():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    if (DATA_RATES not in hass.data[DOMAIN] or (utcnow().minute % 30) == 0 or len(hass.data[DOMAIN][DATA_RATES]) == 0):

      # FIX: Ideally we'd only get the tariffs once at the start, but it's not working
      account_info = await client.async_get_account(config[CONFIG_MAIN_ACCOUNT_ID])

      current_agreement = None
      if len(account_info["electricity_meter_points"]) > 0:
        # We're only interested in the tariff of the first electricity point
        for point in account_info["electricity_meter_points"]:
          current_agreement = get_active_agreement(point["agreements"])
          if current_agreement != None:
            break

      if current_agreement == None:
        raise

      tariff_code = current_agreement["tariff_code"]
      matches = re.search("^[A-Z]-[0-9A-Z]+-([A-Z0-9-]+)-[A-Z]$", tariff_code)
      if matches == None:
        raise

      product_code = matches[1]

      _LOGGER.info('Updating rates...')
      hass.data[DOMAIN][DATA_RATES] = await client.async_get_rates(product_code, tariff_code)
    
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
  elif CONFIG_TARGET_NAME in entry.data:
    # Forward our entry to setup our target rate sensors
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )

  return True