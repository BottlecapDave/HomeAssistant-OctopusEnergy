import logging
from datetime import datetime, timedelta
from typing import Awaitable, Callable

from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_INTELLIGENT_DEVICE_COORDINATOR,
  DATA_INTELLIGENT_DEVICES,
  DOMAIN,

  DATA_CLIENT,
  DATA_ACCOUNT,
  DATA_ACCOUNT_COORDINATOR,
  DATA_INTELLIGENT_DISPATCHES,
  DATA_INTELLIGENT_DISPATCHES_COORDINATOR,
  INTELLIGENT_SOURCE_BUMP_CHARGE_OPTIONS,
  REFRESH_RATE_IN_MINUTES_INTELLIGENT,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.intelligent_dispatches import IntelligentDispatchItem, IntelligentDispatches, SimpleIntelligentDispatchItem
from . import BaseCoordinatorResult
from ..api_client.intelligent_device import IntelligentDevice
from ..storage.intelligent_dispatches import async_save_cached_intelligent_dispatches

from ..intelligent import clean_intelligent_dispatch_history, clean_previous_dispatches, has_dispatches_changed, has_intelligent_tariff, mock_intelligent_dispatches
from ..coordinators.intelligent_device import IntelligentDeviceCoordinatorResult
from ..storage.intelligent_dispatches_history import IntelligentDispatchesHistory, async_save_cached_intelligent_dispatches_history

_LOGGER = logging.getLogger(__name__)

MAXIMUM_DISPATCH_REQUESTS_PER_HOUR = 20

class IntelligentDispatchDataUpdateCoordinator(DataUpdateCoordinator):
  
  def __init__(self, hass, name: str, account_id: str, device_id: str, manual_dispatch_refreshes: bool, refresh_dispatches) -> None:
    """Initialize coordinator."""
    self.__refresh_dispatches = refresh_dispatches
    self.__manual_dispatch_refreshes = manual_dispatch_refreshes
    self.__account_id = account_id
    self.__device_id = device_id
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
      self.hass.data[DOMAIN][self.__account_id][DATA_INTELLIGENT_DISPATCHES][self.__device_id]
      if DOMAIN in self.hass.data and self.__account_id in self.hass.data[DOMAIN] and DATA_INTELLIGENT_DISPATCHES in self.hass.data[DOMAIN][self.__account_id] and self.__device_id in self.hass.data[DOMAIN][self.__account_id][DATA_INTELLIGENT_DISPATCHES]
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
  history: IntelligentDispatchesHistory
  requests_current_hour: int
  requests_current_hour_last_reset: datetime

  def __init__(self, last_evaluated: datetime, request_attempts: int, dispatches: IntelligentDispatches, history: IntelligentDispatchesHistory, requests_current_hour: int, requests_current_hour_last_reset: datetime, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_INTELLIGENT, None, last_error)
    self.dispatches = dispatches
    self.history = history
    self.requests_current_hour = requests_current_hour
    self.requests_current_hour_last_reset = requests_current_hour_last_reset

def merge_started_dispatches(current: datetime,
                             current_state: str,
                             started_dispatches: list[SimpleIntelligentDispatchItem],
                             planned_dispatches: list[IntelligentDispatchItem]):
  new_started_dispatches = clean_previous_dispatches(current, started_dispatches)
  new_started_dispatches = list(map(lambda item: SimpleIntelligentDispatchItem(item.start, item.end), new_started_dispatches))

  if current_state == "SMART_CONTROL_IN_PROGRESS":
    for planned_dispatch in planned_dispatches:
      if planned_dispatch.start <= current and planned_dispatch.end >= current:
        # Skip any bump charges
        if (planned_dispatch.source.lower() in INTELLIGENT_SOURCE_BUMP_CHARGE_OPTIONS if planned_dispatch.source is not None else False):
          continue

        is_extended = False
        start = current.replace(minute=0 if current.minute < 30 else 30, second=0, microsecond=0)
        end = start + timedelta(minutes=30)
        for started_dispatch in new_started_dispatches:
          if (started_dispatch.end == end):
            # Skip as we are already covering the current 30 minute period
            is_extended = True
            break
          elif (started_dispatch.end == start):
            started_dispatch.end = end
            is_extended = True
            break

        if is_extended == False:
          new_started_dispatches.append(SimpleIntelligentDispatchItem(start, end))

  return new_started_dispatches

async def async_retrieve_intelligent_dispatches(
  current: datetime,
  client: OctopusEnergyApiClient,
  account_info,
  intelligent_device: IntelligentDevice | None,
  existing_intelligent_dispatches_result: IntelligentDispatchesCoordinatorResult,
  is_data_mocked: bool,
  is_manual_refresh: bool,
  planned_dispatches_supported: bool,
):
  if (account_info is not None):
    account_id = account_info["id"]
    if (existing_intelligent_dispatches_result is None or 
        current >= existing_intelligent_dispatches_result.next_refresh or
        is_manual_refresh):

      requests_current_hour = existing_intelligent_dispatches_result.requests_current_hour if existing_intelligent_dispatches_result is not None else 0
      requests_last_reset = existing_intelligent_dispatches_result.requests_current_hour_last_reset if existing_intelligent_dispatches_result is not None else current

      if current - requests_last_reset >= timedelta(hours=1):
        requests_current_hour = 0
        requests_last_reset = current
      
      if requests_current_hour >= MAXIMUM_DISPATCH_REQUESTS_PER_HOUR:
        error = f"Maximum requests of {MAXIMUM_DISPATCH_REQUESTS_PER_HOUR}/hour reached. Will reset after {requests_last_reset + timedelta(hours=1)}"
        _LOGGER.debug(error)
        return IntelligentDispatchesCoordinatorResult(
          existing_intelligent_dispatches_result.last_evaluated,
          existing_intelligent_dispatches_result.request_attempts,
          existing_intelligent_dispatches_result.dispatches,
          existing_intelligent_dispatches_result.history,
          existing_intelligent_dispatches_result.requests_current_hour,
          existing_intelligent_dispatches_result.requests_current_hour_last_reset,
          last_error=error
        )
      
      # We don't want manual refreshing to occur too many times
      if (is_manual_refresh and
          existing_intelligent_dispatches_result is not None and
          (existing_intelligent_dispatches_result.last_retrieved + timedelta(minutes=1)) > current):
        error = f"Manual refreshing of dispatches cannot be be called again until {existing_intelligent_dispatches_result.last_retrieved + timedelta(minutes=1)}"
        _LOGGER.debug(error)
        return IntelligentDispatchesCoordinatorResult(
          existing_intelligent_dispatches_result.last_evaluated,
          existing_intelligent_dispatches_result.request_attempts,
          existing_intelligent_dispatches_result.dispatches,
          existing_intelligent_dispatches_result.history,
          existing_intelligent_dispatches_result.requests_current_hour,
          existing_intelligent_dispatches_result.requests_current_hour_last_reset,
          last_error=error
        )

      dispatches = None
      raised_exception = None
      if has_intelligent_tariff(current, account_info) and intelligent_device is not None:
        try:
          dispatches = await client.async_get_intelligent_dispatches(account_id, intelligent_device.id)

          if dispatches is not None:
            _LOGGER.debug(f'Intelligent dispatches retrieved for account {account_id}')
          else:
            raised_exception = "Failed to retrieve intelligent dispatches found for account {account_id}"
        except Exception as e:
          if isinstance(e, ApiException) == False:
            raise
          
          raised_exception=e
          _LOGGER.debug(f'Failed to retrieve intelligent dispatches for account {account_id}')
      else:
        _LOGGER.debug('Skipping due to not on intelligent tariff')

      if is_data_mocked:
        dispatches = mock_intelligent_dispatches(device_id=intelligent_device.id)
        _LOGGER.debug(f'Intelligent dispatches mocked for account {account_id}')

      if dispatches is not None:
        if planned_dispatches_supported == False:
          # If planned dispatches are not supported, then we should clear down the planned dispatches as they are not useful
          _LOGGER.debug("Clearing planned dispatches due to not being supported for provider")
          dispatches.planned.clear()

        dispatches.completed = clean_previous_dispatches(current,
                                                         (existing_intelligent_dispatches_result.dispatches.completed if existing_intelligent_dispatches_result is not None and existing_intelligent_dispatches_result.dispatches is not None and existing_intelligent_dispatches_result.dispatches.completed is not None else []) + dispatches.completed)
        
        new_history = clean_intelligent_dispatch_history(current,
                                                         dispatches,
                                                         existing_intelligent_dispatches_result.history.history if existing_intelligent_dispatches_result is not None else [])

        return IntelligentDispatchesCoordinatorResult(current, 1, dispatches, IntelligentDispatchesHistory(new_history), requests_current_hour + 1, requests_last_reset)
      
      result = None
      if (existing_intelligent_dispatches_result is not None):
        result = IntelligentDispatchesCoordinatorResult(
          existing_intelligent_dispatches_result.last_evaluated,
          existing_intelligent_dispatches_result.request_attempts + 1,
          existing_intelligent_dispatches_result.dispatches,
          existing_intelligent_dispatches_result.history,
          existing_intelligent_dispatches_result.requests_current_hour + 1,
          existing_intelligent_dispatches_result.requests_current_hour_last_reset,
          last_error=raised_exception
        )

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve new dispatches - using cached dispatches. See diagnostics sensor for more information.")
      else:
        # We want to force into our fallback mode
        result = IntelligentDispatchesCoordinatorResult(
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT),
          2,
          None,
          IntelligentDispatchesHistory([]),
          requests_current_hour,
          requests_last_reset,
          last_error=raised_exception
        )
        _LOGGER.warning(f"Failed to retrieve new dispatches. See diagnostics sensor for more information.")

      return result
  else:
    _LOGGER.debug('Account info is missing')
  
  return existing_intelligent_dispatches_result

async def async_refresh_intelligent_dispatches(
  current: datetime,
  client: OctopusEnergyApiClient,
  account_info,
  intelligent_device: IntelligentDevice | None,
  existing_intelligent_dispatches_result: IntelligentDispatchesCoordinatorResult,
  is_data_mocked: bool,
  is_manual_refresh: bool,
  planned_dispatches_supported: bool,
  async_save_dispatches: Callable[[IntelligentDispatches], Awaitable[list]],
  async_save_dispatches_history: Callable[[IntelligentDispatchesHistory], Awaitable[list]],
):
  result = await async_retrieve_intelligent_dispatches(
    current,
    client,
    account_info,
    intelligent_device,
    existing_intelligent_dispatches_result,
    is_data_mocked,
    is_manual_refresh,
    planned_dispatches_supported
  )

  if result is not None and result.dispatches is not None:
    if result.last_retrieved < current:
      _LOGGER.debug(f'Skipping started dispatches processing as data has not been refreshed recently - last_retrieved: {result.last_retrieved}; current: {current}')
      # If we haven't refreshed recently, then we can't accurately process started dispatches
      return result
    
    result.dispatches.started = merge_started_dispatches(current,
                                                         result.dispatches.current_state,
                                                         existing_intelligent_dispatches_result.dispatches.started 
                                                         if existing_intelligent_dispatches_result is not None and existing_intelligent_dispatches_result.dispatches is not None and existing_intelligent_dispatches_result.dispatches.started is not None
                                                         else [],
                                                         result.dispatches.planned)

    if (existing_intelligent_dispatches_result is None or
        existing_intelligent_dispatches_result.dispatches is None or
        has_dispatches_changed(existing_intelligent_dispatches_result.dispatches, result.dispatches)):
      await async_save_dispatches(result.dispatches)
      await async_save_dispatches_history(result.history)

  return result

async def async_setup_intelligent_dispatches_coordinator(
    hass,
    account_id: str,
    device_id: str,
    mock_intelligent_data: bool,
    manual_dispatch_refreshes: bool,
    planned_dispatches_supported: bool):
  async def async_update_intelligent_dispatches_data(is_manual_refresh = False):
    """Fetch data from API endpoint."""
    # Request our account data to be refreshed
    account_coordinator = hass.data[DOMAIN][account_id][DATA_ACCOUNT_COORDINATOR]
    if account_coordinator is not None:
      await account_coordinator.async_request_refresh()

    intelligent_device_coordinator = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE_COORDINATOR]
    if intelligent_device_coordinator is not None:
      await intelligent_device_coordinator.async_request_refresh()

    intelligent_result: IntelligentDeviceCoordinatorResult = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICES] if DATA_INTELLIGENT_DEVICES in hass.data[DOMAIN][account_id] else None
    intelligent_device: IntelligentDevice | None = next((device for device in intelligent_result.devices if device.id == device_id), None) if intelligent_result is not None else None

    current = utcnow()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
    existing_intelligent_dispatches_result = (hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES][device_id]
                                              if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN][account_id] and
                                              device_id in hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES] 
                                              else None)
      
    hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES][device_id] = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_intelligent_dispatches_result,
      mock_intelligent_data,
      is_manual_refresh,
      planned_dispatches_supported,
      lambda dispatches: async_save_cached_intelligent_dispatches(hass, device_id, dispatches),
      lambda history: async_save_cached_intelligent_dispatches_history(hass, device_id, history)
    )
    
    return hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES][device_id]

  hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES_COORDINATOR.format(device_id)] = IntelligentDispatchDataUpdateCoordinator(
    hass,
    name=f"intelligent_dispatches_{device_id}",
    account_id=account_id,
    device_id=device_id,
    refresh_dispatches=async_update_intelligent_dispatches_data,
    manual_dispatch_refreshes=manual_dispatch_refreshes
  )