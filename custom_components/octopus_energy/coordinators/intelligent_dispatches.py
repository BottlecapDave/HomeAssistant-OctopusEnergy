import logging
from datetime import timedelta

from ..coordinators import async_get_current_electricity_agreement_tariff_codes
from ..intelligent import async_mock_intelligent_data, clean_previous_dispatches, is_intelligent_tariff, mock_intelligent_dispatches

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
  DATA_INTELLIGENT_DISPATCHES,
  DATA_INTELLIGENT_DISPATCHES_COORDINATOR,

  STORAGE_COMPLETED_DISPATCHES_NAME
)

from ..api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

async def async_merge_dispatch_data(hass, account_id: str, completed_dispatches):
  storage_key = STORAGE_COMPLETED_DISPATCHES_NAME.format(account_id)
  store = storage.Store(hass, "1", storage_key)

  saved_completed_dispatches = await store.async_load()

  new_data = clean_previous_dispatches(utcnow(), (saved_completed_dispatches if saved_completed_dispatches is not None else []) + completed_dispatches)

  await store.async_save(new_data)
  return new_data

async def async_setup_intelligent_dispatches_coordinator(hass, account_id: str):
  # Reset data rates as we might have new information
  hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES] = None

  if DATA_INTELLIGENT_DISPATCHES_COORDINATOR in hass.data[DOMAIN]:
    _LOGGER.info("Intelligent coordinator has already been configured, so skipping")
    return
  
  async def async_update_intelligent_dispatches_data():
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

      dispatches = None
      for ((meter_point), tariff_code) in tariff_codes.items():
        if is_intelligent_tariff(tariff_code):
          try:
            dispatches = await client.async_get_intelligent_dispatches(account_id)
          except:
            _LOGGER.debug('Failed to retrieve intelligent dispatches')
          break

      if await async_mock_intelligent_data(hass):
        dispatches = mock_intelligent_dispatches()

      if dispatches is not None:
        dispatches["completed"] = await async_merge_dispatch_data(hass, account_id, dispatches["completed"])
        hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES] = dispatches
        hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES]["last_updated"] = utcnow()
      elif (DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN]):
        _LOGGER.debug(f"Failed to retrieve new dispatches, so using cached dispatches")
    
    return hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES]

  hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="intelligent_dispatches",
    update_method=async_update_intelligent_dispatches_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

  await hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES_COORDINATOR].async_config_entry_first_refresh()