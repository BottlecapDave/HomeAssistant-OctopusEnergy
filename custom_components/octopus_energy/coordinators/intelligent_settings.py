import logging
from datetime import timedelta

from ..intelligent import async_mock_intelligent_data, clean_previous_dispatches, has_intelligent_tariff, mock_intelligent_settings

from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)
from homeassistant.helpers import storage

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,

  DATA_CLIENT,
  DATA_ACCOUNT,
  DATA_ACCOUNT_COORDINATOR,
  DATA_INTELLIGENT_SETTINGS,
  DATA_INTELLIGENT_SETTINGS_COORDINATOR,
)

from ..api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_intelligent_settings_coordinator(hass, account_id: str):
  # Reset data rates as we might have new information
  hass.data[DOMAIN][DATA_INTELLIGENT_SETTINGS] = None
  
  async def async_update_intelligent_settings_data():
    """Fetch data from API endpoint."""
    # Request our account data to be refreshed
    account_coordinator = hass.data[DOMAIN][DATA_ACCOUNT_COORDINATOR]
    if account_coordinator is not None:
      await account_coordinator.async_request_refresh()

    current = utcnow()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    if (DATA_ACCOUNT in hass.data[DOMAIN]):

      settings = None
      if has_intelligent_tariff(current, hass.data[DOMAIN][DATA_ACCOUNT]):
        try:
          settings = await client.async_get_intelligent_settings(account_id)
          _LOGGER.debug(f'Intelligent settings retrieved for account {account_id}')
        except:
          _LOGGER.debug('Failed to retrieve intelligent dispatches for account {account_id}')

      if await async_mock_intelligent_data(hass):
        settings = mock_intelligent_settings()

      if settings is not None:
        hass.data[DOMAIN][DATA_INTELLIGENT_SETTINGS] = settings
        hass.data[DOMAIN][DATA_INTELLIGENT_SETTINGS]["last_updated"] = utcnow()
      elif (DATA_INTELLIGENT_SETTINGS in hass.data[DOMAIN]):
        _LOGGER.debug(f"Failed to retrieve intelligent settings, so using cached settings")
    
    return hass.data[DOMAIN][DATA_INTELLIGENT_SETTINGS]

  hass.data[DOMAIN][DATA_INTELLIGENT_SETTINGS_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="intelligent_settings",
    update_method=async_update_intelligent_settings_data,
    update_interval=timedelta(minutes=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  await hass.data[DOMAIN][DATA_INTELLIGENT_SETTINGS_COORDINATOR].async_config_entry_first_refresh()