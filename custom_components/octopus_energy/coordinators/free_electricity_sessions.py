import logging
from datetime import datetime, timedelta
from typing import Callable, Any

from homeassistant.util.dt import (now, as_local)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,
  DATA_CLIENT,
  DATA_FREE_ELECTRICITY_SESSIONS,
  DATA_FREE_ELECTRICITY_SESSIONS_COORDINATOR,
  EVENT_ALL_FREE_ELECTRICITY_SESSIONS,
  EVENT_NEW_FREE_ELECTRICITY_SESSION,
  REFRESH_RATE_IN_MINUTES_OCTOPLUS_FREE_ELECTRICITY_SESSIONS,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from . import BaseCoordinatorResult
from ..api_client.free_electricity_sessions import FreeElectricitySession

_LOGGER = logging.getLogger(__name__)

class FreeElectricitySessionsCoordinatorResult(BaseCoordinatorResult):
  events: list[FreeElectricitySession]

  def __init__(self, last_evaluated: datetime, request_attempts: int, events: list[FreeElectricitySession], last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_OCTOPLUS_FREE_ELECTRICITY_SESSIONS, None, last_error)
    self.events = events

async def async_refresh_free_electricity_sessions(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_id: str,
    existing_free_electricity_sessions_result: FreeElectricitySessionsCoordinatorResult,
    fire_event: Callable[[str, "dict[str, Any]"], None],
) -> FreeElectricitySessionsCoordinatorResult:
  if existing_free_electricity_sessions_result is None or current >= existing_free_electricity_sessions_result.next_refresh:
    try:
      result = await client.async_get_free_electricity_sessions(account_id)

      for available_event in result.data:
        is_new = True

        if existing_free_electricity_sessions_result is not None:
          for existing_available_event in existing_free_electricity_sessions_result.events:
            # Look at code instead of id, in case the code changes but the id stays the same
            if existing_available_event.code == available_event.code:
              is_new = False
              break

        if is_new:
          fire_event(EVENT_NEW_FREE_ELECTRICITY_SESSION, { 
            "account_id": account_id,
            "event_code": available_event.code,
            "event_start": as_local(available_event.start),
            "event_end": as_local(available_event.end),
            "event_duration_in_minutes": available_event.duration_in_minutes
          })

      fire_event(EVENT_ALL_FREE_ELECTRICITY_SESSIONS, { 
        "account_id": account_id,
        "events": list(map(lambda ev: {
          "code": ev.code,
          "start": as_local(ev.start),
          "end": as_local(ev.end),
          "duration_in_minutes": ev.duration_in_minutes
        }, result.data)),
      })

      return FreeElectricitySessionsCoordinatorResult(current, 1, result.data)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      
      result = None
      if (existing_free_electricity_sessions_result is not None):
        result = FreeElectricitySessionsCoordinatorResult(
          existing_free_electricity_sessions_result.last_evaluated,
          existing_free_electricity_sessions_result.request_attempts + 1,
          existing_free_electricity_sessions_result.events,
          last_error=e
        )

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve free electricity sessions - using cached data. See diagnostics sensor for more information.")
      else:
        result = FreeElectricitySessionsCoordinatorResult(
          # We want to force into our fallback mode
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_FREE_ELECTRICITY_SESSIONS),
          2,
          [],
          last_error=e
        )
        _LOGGER.warning(f"Failed to retrieve free electricity sessions. See diagnostics sensor for more information.")
      
      return result
  
  return existing_free_electricity_sessions_result

async def async_setup_free_electricity_sessions_coordinators(hass, account_id: str):

  async def async_update_free_electricity_sessions():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    previous_result = hass.data[DOMAIN][account_id][DATA_FREE_ELECTRICITY_SESSIONS] if DATA_FREE_ELECTRICITY_SESSIONS in hass.data[DOMAIN][account_id] else None

    result = await async_refresh_free_electricity_sessions(
      current,
      client,
      account_id,
      previous_result,
      hass.bus.async_fire
    )

    hass.data[DOMAIN][account_id][DATA_FREE_ELECTRICITY_SESSIONS] = result
    return hass.data[DOMAIN][account_id][DATA_FREE_ELECTRICITY_SESSIONS]

  hass.data[DOMAIN][account_id][DATA_FREE_ELECTRICITY_SESSIONS_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"free_electricity_sessions_{account_id}",
    update_method=async_update_free_electricity_sessions,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )