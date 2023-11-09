import logging
from datetime import datetime, timedelta
from typing import Callable, Any

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
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
  nonjoined_events: list[SavingSession]
  joined_events: list[SavingSession]

  def __init__(self, last_retrieved: datetime, nonjoined_events: list[SavingSession], joined_events: list[SavingSession]):
    self.last_retrieved = last_retrieved
    self.nonjoined_events = nonjoined_events
    self.joined_events = joined_events

def filter_nonjoined_events(current: datetime, upcoming_events: list[SavingSession], joined_events: list[SavingSession]) -> list[SavingSession]:
  filtered_events = []
  for upcoming_event in upcoming_events:

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
  if existing_saving_sessions_result is None or current.minute % 30 == 0:
    try:
      result = await client.async_get_saving_sessions(account_id)
      nonjoined_events = filter_nonjoined_events(current, result.upcoming_events, result.joined_events)

      for nonjoined_event in nonjoined_events:
        is_new = True

        if existing_saving_sessions_result is not None:
          for existing_nonjoined_event in existing_saving_sessions_result.nonjoined_events:
            if existing_nonjoined_event.id == nonjoined_event.id:
              is_new = False
              break

        if is_new:
          fire_event(EVENT_NEW_SAVING_SESSION, { 
            "account_id": account_id,
            "event_id": nonjoined_event.id,
            "event_start": nonjoined_event.start,
            "event_end": nonjoined_event.end,
            "event_octopoints": nonjoined_event.octopoints
          })

      fire_event(EVENT_ALL_SAVING_SESSIONS, { 
        "account_id": account_id,
        "nonjoined_events": list(map(lambda ev: {
          "id": ev.id,
          "start": ev.start,
          "end": ev.end,
          "octopoints": ev.octopoints
        }, nonjoined_events)),
        "joined_events": list(map(lambda ev: {
          "id": ev.id,
          "start": ev.start,
          "end": ev.end,
          "octopoints": ev.octopoints
        }, result.joined_events)), 
      })

      return SavingSessionsCoordinatorResult(current, nonjoined_events, result.joined_events)
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

    result = await async_refresh_saving_sessions(
      current,
      client,
      account_id,
      hass.data[DOMAIN][DATA_SAVING_SESSIONS] if DATA_SAVING_SESSIONS in hass.data[DOMAIN] else None,
      hass.bus.async_fire
    )

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