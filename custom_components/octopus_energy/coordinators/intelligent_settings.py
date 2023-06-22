import logging
from datetime import timedelta

from . import async_get_current_electricity_agreement_tariff_codes
from ..intelligent import async_mock_intelligent_data, clean_previous_dispatches, is_intelligent_tariff, mock_intelligent_settings

from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)
from homeassistant.helpers import storage

from ..const import (
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

  if DATA_INTELLIGENT_SETTINGS_COORDINATOR in hass.data[DOMAIN]:
    _LOGGER.info("Intelligent coordinator has already been configured, so skipping")
    return
  
  async def async_update_intelligent_settings_data():
    """Fetch data from API endpoint."""
    # Request our account data to be refreshed
    account_coordinator = hass.data[DOMAIN][DATA_ACCOUNT_COORDINATOR]
    if account_coordinator is not None:
      await account_coordinator.async_request_refresh()

    # Only get data every half hour or if we don't have any data
    current = utcnow()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    if (DATA_ACCOUNT in hass.data[DOMAIN]):

      tariff_codes = await async_get_current_electricity_agreement_tariff_codes(hass, client, account_id)
      _LOGGER.debug(f'tariff_codes: {tariff_codes}')

      settings = None
      for ((meter_point), tariff_code) in tariff_codes.items():
        if is_intelligent_tariff(tariff_code):
          try:
            settings = await client.async_get_intelligent_settings(account_id)
          except:
            _LOGGER.debug('Failed to retrieve intelligent dispatches')
          break

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
    update_interval=timedelta(minutes=1),
  )

  await hass.data[DOMAIN][DATA_INTELLIGENT_SETTINGS_COORDINATOR].async_config_entry_first_refresh()