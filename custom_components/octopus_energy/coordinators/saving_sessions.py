import logging
from datetime import timedelta

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  DOMAIN,
  DATA_CLIENT,
  DATA_ACCOUNT_ID,
  DATA_SAVING_SESSIONS,
  DATA_SAVING_SESSIONS_COORDINATOR,
)

from ..api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_saving_sessions_coordinators(hass):
  if DATA_SAVING_SESSIONS_COORDINATOR in hass.data[DOMAIN]:
    return

  async def async_update_saving_sessions():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    if DATA_SAVING_SESSIONS not in hass.data[DOMAIN] or current.minute % 30 == 0:

      try:
        savings = await client.async_get_saving_sessions(hass.data[DOMAIN][DATA_ACCOUNT_ID])  
        hass.data[DOMAIN][DATA_SAVING_SESSIONS] = savings
      except:
        _LOGGER.debug('Failed to retrieve saving session information')
    
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
  
  await hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR].async_config_entry_first_refresh()