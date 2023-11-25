import logging
from datetime import datetime, timedelta
from typing import Callable, Any

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_SAVING_SESSIONS_FORCE_UPDATE,
  DOMAIN,
  DATA_CLIENT,
  DATA_ACCOUNT_ID,
  DATA_SAVING_SESSIONS,
  DATA_SAVING_SESSIONS_COORDINATOR,
  EVENT_ALL_SAVING_SESSIONS,
  EVENT_NEW_SAVING_SESSION,
)

from ..api_client import OctopusEnergyApiClient
from ..api_client.saving_sessions import SavingSession

_LOGGER = logging.getLogger(__name__)

class SavingSessionsCoordinatorResult:
  last_retrieved: datetime
  available_events: list[SavingSession]
  joined_events: list[SavingSession]

  def __init__(self, last_retrieved: datetime, available_events: list[SavingSession], joined_events: list[SavingSession]):
    self.last_retrieved = last_retrieved
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
  if existing_saving_sessions_result is None or (existing_saving_sessions_result.last_retrieved + timedelta(minutes=30)) < current or current.minute % 30 == 0:
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
            "event_start": available_event.start,
            "event_end": available_event.end,
            "event_octopoints_per_kwh": available_event.octopoints
          })

      fire_event(EVENT_ALL_SAVING_SESSIONS, { 
        "account_id": account_id,
        "available_events": list(map(lambda ev: {
          "id": ev.id,
          "code": ev.code,
          "start": ev.start,
          "end": ev.end,
          "octopoints_per_kwh": ev.octopoints
        }, available_events)),
        "joined_events": list(map(lambda ev: {
          "id": ev.id,
          "start": ev.start,
          "end": ev.end,
          "rewarded_octopoints": ev.octopoints
        }, result.joined_events)), 
      })

      return SavingSessionsCoordinatorResult(current, available_events, result.joined_events)
    except:
      _LOGGER.debug('Failed to retrieve saving session information')
  
  return existing_saving_sessions_result

async def async_setup_saving_sessions_coordinators(hass):
  account_id = hass.data[DOMAIN][DATA_ACCOUNT_ID]

  async def async_update_saving_sessions():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    force_update = hass.data[DOMAIN][DATA_SAVING_SESSIONS_FORCE_UPDATE] if DATA_SAVING_SESSIONS_FORCE_UPDATE in hass.data[DOMAIN] else False
    previous_result = hass.data[DOMAIN][DATA_SAVING_SESSIONS] if DATA_SAVING_SESSIONS in hass.data[DOMAIN] else None

    result = await async_refresh_saving_sessions(
      current,
      client,
      account_id,
      previous_result if force_update == False else None,
      hass.bus.async_fire
    )

    if result != previous_result:
      hass.data[DOMAIN][DATA_SAVING_SESSIONS_FORCE_UPDATE] = False

    hass.data[DOMAIN][DATA_SAVING_SESSIONS] = result
    return hass.data[DOMAIN][DATA_SAVING_SESSIONS]

  hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"{account_id}_saving_sessions",
    update_method=async_update_saving_sessions,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )
  
  await hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR].async_config_entry_first_refresh()