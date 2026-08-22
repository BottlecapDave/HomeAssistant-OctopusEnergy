import logging
from datetime import datetime, timedelta
from typing import Callable, Any

from homeassistant.util.dt import (now, as_local)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_POWER_DOWN_FORCE_UPDATE,
  DOMAIN,
  DATA_CLIENT,
  DATA_POWER_UP_DOWN_SESSIONS,
  DATA_POWER_UP_DOWN_COORDINATOR,
  EVENT_ALL_FREE_ELECTRICITY_SESSIONS,
  EVENT_ALL_POWER_UP_SESSIONS,
  EVENT_ALL_SAVING_SESSIONS,
  EVENT_NEW_FREE_ELECTRICITY_SESSION,
  EVENT_NEW_POWER_UP_SESSION,
  EVENT_NEW_SAVING_SESSION,
  EVENT_ALL_POWER_DOWN_SESSIONS,
  EVENT_NEW_POWER_DOWN_SESSION,
  REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.saving_sessions import SavingSession
from . import BaseCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class PowerUpDownSessionsCoordinatorResult(BaseCoordinatorResult):
  available_power_down_events: list[SavingSession]
  joined_power_down_events: list[SavingSession]
  available_power_up_events: list[SavingSession]
  joined_power_up_events: list[SavingSession]

  def __init__(self, last_evaluated: datetime, request_attempts: int, available_power_down_events: list[SavingSession], joined_power_down_events: list[SavingSession], available_power_up_events: list[SavingSession], joined_power_up_events: list[SavingSession], last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN, None, last_error)
    self.available_power_down_events = available_power_down_events
    self.joined_power_down_events = joined_power_down_events
    self.available_power_up_events = available_power_up_events
    self.joined_power_up_events = joined_power_up_events

def filter_available_events(current: datetime, available_events: list[SavingSession], joined_events: list[SavingSession], regionId: str | None) -> list[SavingSession]:
  filtered_events = []
  for upcoming_event in available_events:
    is_joined = False
    for joined_event in joined_events:
      if joined_event.id == upcoming_event.id:
        is_joined = True
        break

    is_in_region = upcoming_event.targetRegions is None or len(upcoming_event.targetRegions) == 0 or (regionId is not None and regionId in upcoming_event.targetRegions)
    if (is_in_region == False):
      _LOGGER.info(f"Excluding saving session {upcoming_event.code} as it is not in the correct region. Event regions: {','.join(upcoming_event.targetRegions)}, user region: {regionId}")

    if (upcoming_event.start >= current and
        is_joined == False and
        is_in_region):
      filtered_events.append(upcoming_event)

  return filtered_events

def get_start(event: SavingSession):
  return event.start

async def async_refresh_power_up_down_sessions(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_id: str,
    existing_power_down_sessions_result: PowerUpDownSessionsCoordinatorResult,
    fire_event: Callable[[str, "dict[str, Any]"], None],
) -> PowerUpDownSessionsCoordinatorResult:
  if existing_power_down_sessions_result is None or current >= existing_power_down_sessions_result.next_refresh:
    try:
      result = await client.async_get_saving_sessions(account_id)
      free_electricity_result = await client.async_get_free_electricity_sessions(account_id)
      available_power_down_events = filter_available_events(current, result.available_power_down_events, result.joined_power_down_events, result.regionId)
      available_power_up_events = filter_available_events(current, result.available_power_up_events, result.joined_power_up_events, result.regionId)

      for available_event in available_power_down_events:
        is_new = True

        if existing_power_down_sessions_result is not None:
          for existing_available_event in existing_power_down_sessions_result.available_power_down_events:
            # Look at code instead of id, in case the code changes but the id stays the same
            if existing_available_event.code == available_event.code:
              is_new = False
              break

        if is_new:
          fire_event(EVENT_NEW_SAVING_SESSION, { 
            "account_id": account_id,
            "account_region_id": result.regionId,
            "event_code": available_event.code,
            "event_id": available_event.id,
            "event_start": as_local(available_event.start),
            "event_end": as_local(available_event.end),
            "event_duration_in_minutes": available_event.duration_in_minutes,
            "event_octopoints_per_kwh": available_event.octopoints,
            "event_target_regions": available_event.targetRegions
          })

          fire_event(EVENT_NEW_POWER_DOWN_SESSION, { 
            "account_id": account_id,
            "account_region_id": result.regionId,
            "event_code": available_event.code,
            "event_id": available_event.id,
            "event_start": as_local(available_event.start),
            "event_end": as_local(available_event.end),
            "event_duration_in_minutes": available_event.duration_in_minutes,
            "event_octopoints_per_kwh": available_event.octopoints,
            "event_target_regions": available_event.targetRegions
          })

      joined_power_down_events = []
      for ev in result.joined_power_down_events:
        # Find original event so we can retrieve the octopoints per kwh
        original_event = None
        for available_event in result.available_power_down_events:
          if (available_event.id == ev.id):
            original_event = available_event
            break

        joined_power_down_events.append({
          "id": ev.id,
          "start": as_local(ev.start),
          "end": as_local(ev.end),
          "duration_in_minutes": ev.duration_in_minutes,
          "rewarded_octopoints": ev.octopoints,
          "octopoints_per_kwh": original_event.octopoints if original_event is not None else None,
          "target_regions": original_event.targetRegions if original_event is not None else []
        })

      fire_event(EVENT_ALL_SAVING_SESSIONS, { 
        "account_id": account_id,
        "account_region_id": result.regionId,
        "available_events": list(map(lambda ev: {
          "id": ev.id,
          "code": ev.code,
          "start": as_local(ev.start),
          "end": as_local(ev.end),
          "duration_in_minutes": ev.duration_in_minutes,
          "octopoints_per_kwh": ev.octopoints,
          "target_regions": ev.targetRegions
        }, available_power_down_events)),
        "joined_events": joined_power_down_events, 
      })

      fire_event(EVENT_ALL_POWER_DOWN_SESSIONS, { 
        "account_id": account_id,
        "account_region_id": result.regionId,
        "available_events": list(map(lambda ev: {
          "id": ev.id,
          "code": ev.code,
          "start": as_local(ev.start),
          "end": as_local(ev.end),
          "duration_in_minutes": ev.duration_in_minutes,
          "octopoints_per_kwh": ev.octopoints,
          "target_regions": ev.targetRegions
        }, available_power_down_events)),
        "joined_events": joined_power_down_events, 
      })

      # Power up sessions appear to be auto-joined when they're applicable
      combined_joined_power_up_events = []
      combined_joined_power_up_events.extend(free_electricity_result.data)
      combined_joined_power_up_events.extend(result.joined_power_up_events)
      combined_joined_power_up_events.sort(key=get_start)
      for available_event in combined_joined_power_up_events:
        is_new = True

        if existing_power_down_sessions_result is not None:
          for existing_available_event in existing_power_down_sessions_result.joined_power_up_events:
            if existing_available_event.id == available_event.id:
              is_new = False
              break

        if is_new:
          fire_event(EVENT_NEW_FREE_ELECTRICITY_SESSION, { 
            "account_id": account_id,
            "event_id": available_event.id,
            "event_code": available_event.code,
            "event_start": as_local(available_event.start),
            "event_end": as_local(available_event.end),
            "event_duration_in_minutes": available_event.duration_in_minutes
          })

          fire_event(EVENT_NEW_POWER_UP_SESSION, { 
            "account_id": account_id,
            "event_id": available_event.id,
            "event_code": available_event.code,
            "event_start": as_local(available_event.start),
            "event_end": as_local(available_event.end),
            "event_duration_in_minutes": available_event.duration_in_minutes
          })

      fire_event(EVENT_ALL_FREE_ELECTRICITY_SESSIONS, { 
        "account_id": account_id,
        "events": list(map(lambda ev: {
          "id": ev.id,
          "code": ev.code,
          "start": as_local(ev.start),
          "end": as_local(ev.end),
          "duration_in_minutes": ev.duration_in_minutes
        }, combined_joined_power_up_events)),
      })

      fire_event(EVENT_ALL_POWER_UP_SESSIONS, { 
        "account_id": account_id,
        "events": list(map(lambda ev: {
          "id": ev.id,
          "code": ev.code,
          "start": as_local(ev.start),
          "end": as_local(ev.end),
          "duration_in_minutes": ev.duration_in_minutes
        }, combined_joined_power_up_events)),
      })

      return PowerUpDownSessionsCoordinatorResult(current, 1, available_power_down_events, result.joined_power_down_events, available_power_up_events, combined_joined_power_up_events)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      
      result = None
      if (existing_power_down_sessions_result is not None):
        result = PowerUpDownSessionsCoordinatorResult(
          existing_power_down_sessions_result.last_evaluated,
          existing_power_down_sessions_result.request_attempts + 1,
          existing_power_down_sessions_result.available_power_down_events,
          existing_power_down_sessions_result.joined_power_down_events,
          existing_power_down_sessions_result.available_power_up_events,
          existing_power_down_sessions_result.joined_power_up_events,
          last_error=e
        )

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve saving sessions - using cached data. See diagnostics sensor for more information.")
      else:
        result = PowerUpDownSessionsCoordinatorResult(
          # We want to force into our fallback mode
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN),
          2,
          [],
          [],
          [],
          [],
          last_error=e
        )
        _LOGGER.warning(f"Failed to retrieve saving sessions. See diagnostics sensor for more information.")
      
      return result
  
  return existing_power_down_sessions_result

async def async_setup_power_up_down_coordinators(hass, account_id: str):

  async def async_update_power_down_sessions():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    force_update = hass.data[DOMAIN][account_id][DATA_POWER_DOWN_FORCE_UPDATE] if DATA_POWER_DOWN_FORCE_UPDATE in hass.data[DOMAIN][account_id] else False
    previous_result = hass.data[DOMAIN][account_id][DATA_POWER_UP_DOWN_SESSIONS] if DATA_POWER_UP_DOWN_SESSIONS in hass.data[DOMAIN][account_id] else None

    result = await async_refresh_power_up_down_sessions(
      current,
      client,
      account_id,
      previous_result if force_update == False else None,
      hass.bus.async_fire
    )

    if result != previous_result:
      hass.data[DOMAIN][account_id][DATA_POWER_DOWN_FORCE_UPDATE] = False

    hass.data[DOMAIN][account_id][DATA_POWER_UP_DOWN_SESSIONS] = result
    return hass.data[DOMAIN][account_id][DATA_POWER_UP_DOWN_SESSIONS]

  hass.data[DOMAIN][account_id][DATA_POWER_UP_DOWN_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"power_up_down_sessions_{account_id}",
    update_method=async_update_power_down_sessions,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )