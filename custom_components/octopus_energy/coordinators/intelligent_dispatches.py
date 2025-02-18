import logging
from datetime import datetime, timedelta
from typing import Awaitable, Callable

from custom_components.octopus_energy.storage.intelligent_dispatches import async_save_cached_intelligent_dispatches
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
from ..api_client.intelligent_dispatches import IntelligentDispatchItem, IntelligentDispatches
from . import BaseCoordinatorResult
from ..api_client.intelligent_device import IntelligentDevice

from ..intelligent import clean_previous_dispatches, dictionary_list_to_dispatches, dispatches_to_dictionary_list, has_intelligent_tariff, mock_intelligent_dispatches

_LOGGER = logging.getLogger(__name__)

MAXIMUM_RATES_PER_HOUR = 20

class IntelligentDispatchDataUpdateCoordinator(DataUpdateCoordinator):
  
  def __init__(self, hass, name: str, account_id: str, manual_dispatch_refreshes: bool, refresh_dispatches) -> None:
    """Initialize coordinator."""
    self.__refresh_dispatches = refresh_dispatches
    self.__manual_dispatch_refreshes = manual_dispatch_refreshes
    self.__account_id = account_id
    super().__init__(
        hass,
        _LOGGER,
        name=name,
        update_method=self.__automatic_refresh_dispatches,
        update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
        always_update=True
    )

  async def __automatic_refresh_dispatches(self):
    if self.__manual_dispatch_refreshes == False:
      return await self.__refresh_dispatches()
    
    return (
      self.hass.data[DOMAIN][self.__account_id][DATA_INTELLIGENT_DISPATCHES] 
      if DOMAIN in self.hass.data and self.__account_id in self.hass.data[DOMAIN] and DATA_INTELLIGENT_DISPATCHES in self.hass.data[DOMAIN][self.__account_id]
      else None
    )

  async def refresh_dispatches(self):
    _LOGGER.debug('Refreshing dispatches')
    result = await self.__refresh_dispatches(is_manual_refresh=True)
    self.data = result
    self.async_update_listeners()
    return result

class IntelligentDispatchesCoordinatorResult(BaseCoordinatorResult):
  dispatches: IntelligentDispatches
  requests_current_hour: int
  requests_current_hour_last_reset: datetime

  def __init__(self, last_evaluated: datetime, request_attempts: int, dispatches: IntelligentDispatches, requests_current_hour: int, requests_current_hour_last_reset: datetime, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_INTELLIGENT, None, last_error)
    self.dispatches = dispatches
    self.requests_current_hour = requests_current_hour
    self.requests_current_hour_last_reset = requests_current_hour_last_reset

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

def has_dispatches_changed(existing_dispatches: IntelligentDispatches, new_dispatches: IntelligentDispatches):
  return (
    existing_dispatches.current_state != new_dispatches.current_state or
    len(existing_dispatches.completed) != len(new_dispatches.completed) or
    (
      len(existing_dispatches.completed) > 0 and
      (
        existing_dispatches.completed[0].start != new_dispatches.completed[0].start or
        existing_dispatches.completed[-1].start != new_dispatches.completed[-1].start
      )
    ) 
    or
    len(existing_dispatches.planned) != len(new_dispatches.planned) or
    (
      len(existing_dispatches.planned) > 0 and
      (
        existing_dispatches.planned[0].start != new_dispatches.planned[0].start or
        existing_dispatches.planned[-1].start != new_dispatches.planned[-1].start
      )
    )
  )

async def async_refresh_intelligent_dispatches(
  current: datetime,
  client: OctopusEnergyApiClient,
  account_info,
  intelligent_device: IntelligentDevice,
  existing_intelligent_dispatches_result: IntelligentDispatchesCoordinatorResult,
  is_data_mocked: bool,
  is_manual_refresh: bool,
  async_merge_dispatch_data: Callable[[str, list], Awaitable[list]],
  async_save_dispatches: Callable[[str, IntelligentDispatches], Awaitable[list]],
):
  requests_current_hour = existing_intelligent_dispatches_result.requests_current_hour if existing_intelligent_dispatches_result is not None else 0
  requests_last_reset = existing_intelligent_dispatches_result.requests_current_hour_last_reset if existing_intelligent_dispatches_result is not None else current

  if current - requests_last_reset >= timedelta(hours=1):
    requests_current_hour = 0
    requests_last_reset = current

  if requests_current_hour >= MAXIMUM_RATES_PER_HOUR:
    _LOGGER.debug('Maximum requests reached for current hour')
    return IntelligentDispatchesCoordinatorResult(
      existing_intelligent_dispatches_result.last_evaluated,
      existing_intelligent_dispatches_result.request_attempts,
      existing_intelligent_dispatches_result.dispatches,
      existing_intelligent_dispatches_result.requests_current_hour,
      existing_intelligent_dispatches_result.requests_current_hour_last_reset,
      last_error=f"Maximum requests of {MAXIMUM_RATES_PER_HOUR}/hour reached. Will reset after {requests_last_reset + timedelta(hours=1)}"
    )
  
  # We don't want manual refreshing to occur too many times
  if (is_manual_refresh and
      existing_intelligent_dispatches_result is not None and
      (existing_intelligent_dispatches_result.last_retrieved + timedelta(minutes=1)) > current):
    _LOGGER.debug('Maximum requests reached for current hour')
    return IntelligentDispatchesCoordinatorResult(
      existing_intelligent_dispatches_result.last_evaluated,
      existing_intelligent_dispatches_result.request_attempts,
      existing_intelligent_dispatches_result.dispatches,
      existing_intelligent_dispatches_result.requests_current_hour,
      existing_intelligent_dispatches_result.requests_current_hour_last_reset,
      last_error=f"Manual refreshing of dispatches cannot be be called again until {existing_intelligent_dispatches_result.last_retrieved + timedelta(minutes=1)}"
    )

  if (account_info is not None):
    account_id = account_info["id"]
    if (existing_intelligent_dispatches_result is None or 
        current >= existing_intelligent_dispatches_result.next_refresh or
        is_manual_refresh):
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
        _LOGGER.debug(f'Intelligent dispatches mocked for account {account_id}')

      if dispatches is not None:
        dispatches.completed = await async_merge_dispatch_data(account_id, dispatches.completed)

        if (existing_intelligent_dispatches_result is None or
            existing_intelligent_dispatches_result.dispatches is None or
            has_dispatches_changed(existing_intelligent_dispatches_result.dispatches, dispatches)):
          await async_save_dispatches(account_id, dispatches)

        return IntelligentDispatchesCoordinatorResult(current, 1, dispatches, requests_current_hour + 1, requests_last_reset)
      
      result = None
      if (existing_intelligent_dispatches_result is not None):
        result = IntelligentDispatchesCoordinatorResult(
          existing_intelligent_dispatches_result.last_evaluated,
          existing_intelligent_dispatches_result.request_attempts + 1,
          existing_intelligent_dispatches_result.dispatches,
          existing_intelligent_dispatches_result.requests_current_hour + 1,
          existing_intelligent_dispatches_result.requests_current_hour_last_reset,
          last_error=raised_exception
        )

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve new dispatches - using cached dispatches. See diagnostics sensor for more information.")
      else:
        # We want to force into our fallback mode
        result = IntelligentDispatchesCoordinatorResult(current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT), 2, None, requests_current_hour, requests_last_reset, last_error=raised_exception)
        _LOGGER.warning(f"Failed to retrieve new dispatches. See diagnostics sensor for more information.")

      return result
  
  return existing_intelligent_dispatches_result

async def async_setup_intelligent_dispatches_coordinator(hass, account_id: str, mock_intelligent_data: bool, manual_dispatch_refreshes: bool):
  async def async_update_intelligent_dispatches_data(is_manual_refresh = False):
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
      is_manual_refresh,
      lambda account_id, completed_dispatches: async_merge_dispatch_data(hass, account_id, completed_dispatches),
      lambda account_id, dispatches: async_save_cached_intelligent_dispatches(hass, account_id, dispatches)
    )
    
    return hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES]

  hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES_COORDINATOR] = IntelligentDispatchDataUpdateCoordinator(
    hass,
    name=f"intelligent_dispatches-{account_id}",
    account_id=account_id,
    refresh_dispatches=async_update_intelligent_dispatches_data,
    manual_dispatch_refreshes=manual_dispatch_refreshes
  )