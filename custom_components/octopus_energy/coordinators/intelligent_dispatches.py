import logging
from datetime import datetime, timedelta
from typing import Awaitable, Callable

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
  DATA_INTELLIGENT_DISPATCHES,
  DATA_INTELLIGENT_DISPATCHES_COORDINATOR,
  REFRESH_RATE_IN_MINUTES_INTELLIGENT,

  STORAGE_COMPLETED_DISPATCHES_NAME
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.intelligent_dispatches import IntelligentDispatches
from . import BaseCoordinatorResult

from ..intelligent import async_mock_intelligent_data, clean_previous_dispatches, dictionary_list_to_dispatches, dispatches_to_dictionary_list, has_intelligent_tariff, mock_intelligent_dispatches

_LOGGER = logging.getLogger(__name__)

class IntelligentDispatchesCoordinatorResult(BaseCoordinatorResult):
  dispatches: IntelligentDispatches

  def __init__(self, last_retrieved: datetime, request_attempts: int, dispatches: IntelligentDispatches):
    super().__init__(last_retrieved, request_attempts, REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    self.dispatches = dispatches

async def async_merge_dispatch_data(hass, account_id: str, completed_dispatches):
  storage_key = STORAGE_COMPLETED_DISPATCHES_NAME.format(account_id)
  store = storage.Store(hass, "1", storage_key)

  try:
    saved_dispatches = await store.async_load()
  except:
    saved_dispatches = []
    _LOGGER.warning('Local intelligent dispatch data corrupted. Resetting...')

  saved_completed_dispatches = dictionary_list_to_dispatches(saved_dispatches)

  new_data = clean_previous_dispatches(utcnow(), (saved_completed_dispatches if saved_completed_dispatches is not None else []) + completed_dispatches)

  await store.async_save(dispatches_to_dictionary_list(new_data))
  return new_data

async def async_refresh_intelligent_dispatches(
  current: datetime,
  client: OctopusEnergyApiClient,
  account_info,
  existing_intelligent_dispatches_result: IntelligentDispatchesCoordinatorResult,
  is_data_mocked: bool,
  async_merge_dispatch_data: Callable[[str, list], Awaitable[list]]
):
  if (account_info is not None):
    account_id = account_info["id"]
    if (existing_intelligent_dispatches_result is None or current >= existing_intelligent_dispatches_result.next_refresh):
      dispatches = None
      if has_intelligent_tariff(current, account_info):
        try:
          dispatches = await client.async_get_intelligent_dispatches(account_id)
          _LOGGER.debug(f'Intelligent dispatches retrieved for account {account_id}')
        except Exception as e:
          if isinstance(e, ApiException) == False:
            raise
          
          _LOGGER.debug('Failed to retrieve intelligent dispatches for account {account_id}')

      if is_data_mocked:
        dispatches = mock_intelligent_dispatches()

      if dispatches is not None:
        dispatches.completed = await async_merge_dispatch_data(account_id, dispatches.completed)
        return IntelligentDispatchesCoordinatorResult(current, 1, dispatches)
      
      result = None
      if (existing_intelligent_dispatches_result is not None):
        result = IntelligentDispatchesCoordinatorResult(
          existing_intelligent_dispatches_result.last_retrieved,
          existing_intelligent_dispatches_result.request_attempts + 1,
          existing_intelligent_dispatches_result.dispatches
        )
        _LOGGER.warning(f"Failed to retrieve new dispatches - using cached dispatches. Next attempt at {result.next_refresh}")
      else:
        # We want to force into our fallback mode
        result = IntelligentDispatchesCoordinatorResult(current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT), 2, None)
        _LOGGER.warning(f"Failed to retrieve new dispatches. Next attempt at {result.next_refresh}")

      return result
  
  return existing_intelligent_dispatches_result

async def async_setup_intelligent_dispatches_coordinator(hass, account_id: str):
  # Reset data rates as we might have new information
  hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES] = None
  
  async def async_update_intelligent_dispatches_data():
    """Fetch data from API endpoint."""
    # Request our account data to be refreshed
    account_coordinator = hass.data[DOMAIN][account_id][DATA_ACCOUNT_COORDINATOR]
    if account_coordinator is not None:
      await account_coordinator.async_request_refresh()

    current = utcnow()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
      
    hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES] = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES] if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN][account_id] else None,
      await async_mock_intelligent_data(hass, account_id),
      lambda account_id, completed_dispatches: async_merge_dispatch_data(hass, account_id, completed_dispatches) 
    )
    
    return hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES]

  hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="intelligent_dispatches",
    update_method=async_update_intelligent_dispatches_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )