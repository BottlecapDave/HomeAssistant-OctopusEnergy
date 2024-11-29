import logging
from datetime import datetime, timedelta
from typing import Callable, Any

from homeassistant.util.dt import (now, as_local)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_SAVING_SESSIONS_FORCE_UPDATE,
  DOMAIN,
  DATA_CLIENT,
  DATA_SAVING_SESSIONS,
  DATA_SAVING_SESSIONS_COORDINATOR,
  EVENT_ALL_SAVING_SESSIONS,
  EVENT_NEW_SAVING_SESSION,
  REFRESH_RATE_IN_MINUTES_OCTOPLUS_SAVING_SESSIONS,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.saving_sessions import SavingSession
from . import BaseCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class SavingSessionsCoordinatorResult(BaseCoordinatorResult):
  available_events: list[SavingSession]
  joined_events: list[SavingSession]

  def __init__(self, last_evaluated: datetime, request_attempts: int, available_events: list[SavingSession], joined_events: list[SavingSession], last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_OCTOPLUS_SAVING_SESSIONS, None, last_error)
    self.available_events = available_events
    self.joined_events = joined_events

def filter_available_events(current: datetime, available_events: list[SavingSession], joined_events: list[SavingSession]) -> list[SavingSession]:
  filtered_events = []
  for upcoming_event in available_events:
    is_joined = False
    for joined_event in joined_events:
      if joined_event.id == upcoming_event.id:
        is_joined = True
        break

    if (upcoming_event.start >= current and is_joined == False):
      filtered_events.append(upcoming_event)

  return filtered_events

async def async_refresh_saving_sessions(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_id: str,
    existing_saving_sessions_result: SavingSessionsCoordinatorResult,
    fire_event: Callable[[str, "dict[str, Any]"], None],
) -> SavingSessionsCoordinatorResult:
  if existing_saving_sessions_result is None or current >= existing_saving_sessions_result.next_refresh:
    try:
      result = await client.async_get_saving_sessions(account_id)
      available_events = filter_available_events(current, result.available_events, result.joined_events)

      for available_event in available_events:
        is_new = True

        if existing_saving_sessions_result is not None:
          for existing_available_event in existing_saving_sessions_result.available_events:
            # Look at code instead of id, in case the code changes but the id stays the same
            if existing_available_event.code == available_event.code:
              is_new = False
              break

        if is_new:
          fire_event(EVENT_NEW_SAVING_SESSION, { 
            "account_id": account_id,
            "event_code": available_event.code,
            "event_id": available_event.id,
            "event_start": as_local(available_event.start),
            "event_end": as_local(available_event.end),
            "event_duration_in_minutes": available_event.duration_in_minutes,
            "event_octopoints_per_kwh": available_event.octopoints
          })

      joined_events = []
      for ev in result.joined_events:
        # Find original event so we can retrieve the octopoints per kwh
        original_event = None
        for available_event in result.available_events:
          if (available_event.id == ev.id):
            original_event = available_event
            break

        joined_events.append({
          "id": ev.id,
          "start": as_local(ev.start),
          "end": as_local(ev.end),
          "duration_in_minutes": ev.duration_in_minutes,
          "rewarded_octopoints": ev.octopoints,
          "octopoints_per_kwh": original_event.octopoints if original_event is not None else None
        })

      fire_event(EVENT_ALL_SAVING_SESSIONS, { 
        "account_id": account_id,
        "available_events": list(map(lambda ev: {
          "id": ev.id,
          "code": ev.code,
          "start": as_local(ev.start),
          "end": as_local(ev.end),
          "duration_in_minutes": ev.duration_in_minutes,
          "octopoints_per_kwh": ev.octopoints
        }, available_events)),
        "joined_events": joined_events, 
      })

      return SavingSessionsCoordinatorResult(current, 1, available_events, result.joined_events)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      
      result = None
      if (existing_saving_sessions_result is not None):
        result = SavingSessionsCoordinatorResult(
          existing_saving_sessions_result.last_evaluated,
          existing_saving_sessions_result.request_attempts + 1,
          existing_saving_sessions_result.available_events,
          existing_saving_sessions_result.joined_events,
          last_error=e
        )

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve saving sessions - using cached data. See diagnostics sensor for more information.")
      else:
        result = SavingSessionsCoordinatorResult(
          # We want to force into our fallback mode
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_SAVING_SESSIONS),
          2,
          [],
          [],
          last_error=e
        )
        _LOGGER.warning(f"Failed to retrieve saving sessions. See diagnostics sensor for more information.")
      
      return result
  
  return existing_saving_sessions_result

async def async_setup_saving_sessions_coordinators(hass, account_id: str):

  async def async_update_saving_sessions():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    force_update = hass.data[DOMAIN][account_id][DATA_SAVING_SESSIONS_FORCE_UPDATE] if DATA_SAVING_SESSIONS_FORCE_UPDATE in hass.data[DOMAIN][account_id] else False
    previous_result = hass.data[DOMAIN][account_id][DATA_SAVING_SESSIONS] if DATA_SAVING_SESSIONS in hass.data[DOMAIN][account_id] else None

    result = await async_refresh_saving_sessions(
      current,
      client,
      account_id,
      previous_result if force_update == False else None,
      hass.bus.async_fire
    )

    if result != previous_result:
      hass.data[DOMAIN][account_id][DATA_SAVING_SESSIONS_FORCE_UPDATE] = False

    hass.data[DOMAIN][account_id][DATA_SAVING_SESSIONS] = result
    return hass.data[DOMAIN][account_id][DATA_SAVING_SESSIONS]

  hass.data[DOMAIN][account_id][DATA_SAVING_SESSIONS_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"saving_sessions_{account_id}",
    update_method=async_update_saving_sessions,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )