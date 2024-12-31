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
  DATA_INTELLIGENT_DEVICE,
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
from ..api_client.intelligent_device import IntelligentDevice

from ..intelligent import clean_previous_dispatches, dictionary_list_to_dispatches, dispatches_to_dictionary_list, has_intelligent_tariff, mock_intelligent_dispatches

_LOGGER = logging.getLogger(__name__)

class IntelligentDispatchesCoordinatorResult(BaseCoordinatorResult):
  dispatches: IntelligentDispatches

  def __init__(self, last_evaluated: datetime, request_attempts: int, dispatches: IntelligentDispatches, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_INTELLIGENT, None, last_error)
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
  intelligent_device: IntelligentDevice,
  existing_intelligent_dispatches_result: IntelligentDispatchesCoordinatorResult,
  is_data_mocked: bool,
  async_merge_dispatch_data: Callable[[str, list], Awaitable[list]]
):
  if (account_info is not None):
    account_id = account_info["id"]
    if (existing_intelligent_dispatches_result is None or current >= existing_intelligent_dispatches_result.next_refresh):
      dispatches = None
      raised_exception = None
      if has_intelligent_tariff(current, account_info) and intelligent_device is not None:
        try:
          dispatches = await client.async_get_intelligent_dispatches(account_id, intelligent_device.id)
          _LOGGER.debug(f'Intelligent dispatches retrieved for account {account_id}')
        except Exception as e:
          if isinstance(e, ApiException) == False:
            raise
          
          raised_exception=e
          _LOGGER.debug(f'Failed to retrieve intelligent dispatches for account {account_id}')

      if is_data_mocked:
        dispatches = mock_intelligent_dispatches()

      if dispatches is not None:
        dispatches.completed = await async_merge_dispatch_data(account_id, dispatches.completed)
        return IntelligentDispatchesCoordinatorResult(current, 1, dispatches)
      
      result = None
      if (existing_intelligent_dispatches_result is not None):
        result = IntelligentDispatchesCoordinatorResult(
          existing_intelligent_dispatches_result.last_evaluated,
          existing_intelligent_dispatches_result.request_attempts + 1,
          existing_intelligent_dispatches_result.dispatches,
          last_error=raised_exception
        )

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve new dispatches - using cached dispatches. See diagnostics sensor for more information.")
      else:
        # We want to force into our fallback mode
        result = IntelligentDispatchesCoordinatorResult(current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT), 2, None, last_error=raised_exception)
        _LOGGER.warning(f"Failed to retrieve new dispatches. See diagnostics sensor for more information.")

      return result
  
  return existing_intelligent_dispatches_result

async def async_setup_intelligent_dispatches_coordinator(hass, account_id: str, mock_intelligent_data: bool):
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
      hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE] if DATA_INTELLIGENT_DEVICE in hass.data[DOMAIN][account_id] else None,
      hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES] if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN][account_id] else None,
      mock_intelligent_data,
      lambda account_id, completed_dispatches: async_merge_dispatch_data(hass, account_id, completed_dispatches) 
    )
    
    return hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES]

  hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"intelligent_dispatches-{account_id}",
    update_method=async_update_intelligent_dispatches_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )