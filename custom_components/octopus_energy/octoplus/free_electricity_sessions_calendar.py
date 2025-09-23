from datetime import datetime
import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (utcnow)

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEvent,
)
from homeassistant.helpers.restore_state import RestoreEntity

from . import (
  current_octoplus_sessions_event,
  get_next_octoplus_sessions_event
)

from ..utils.attributes import dict_to_typed_dict
from ..coordinators.free_electricity_sessions import FreeElectricitySessionsCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyFreeElectricitySessionsCalendar(CoordinatorEntity, CalendarEntity, RestoreEntity):
  """Sensor for determining if a free electricity session is active."""
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_id = account_id
    self._event = None
    self._events = []

    self.entity_id = generate_entity_id("calendar.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_octoplus_free_electricity_session"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octoplus Free Electricity ({self._account_id})"
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine if the user is in a free electricity session."""

    free_electricity_session: FreeElectricitySessionsCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    if (free_electricity_session is not None):
      self._events = free_electricity_session.events
    else:
      self._events = []

    current_date = utcnow()
    current_event = current_octoplus_sessions_event(current_date, self._events)
    if (current_event is not None):
      self._attr_event = CalendarEvent(
        summary="Octopus Energy Free Electricity",
        start=current_event.start,
        end=current_event.end,
      )
    else:
      next_event = get_next_octoplus_sessions_event(current_date, self._events)
      if (next_event is not None):
        self._attr_event = CalendarEvent(
          summary="Octopus Energy Free Electricity",
          start=next_event.start,
          end=next_event.end,
        )

    super()._handle_coordinator_update()

  async def async_get_events(
    self, hass, start_date: datetime, end_date: datetime
  ) -> list[CalendarEvent]:
    """Get all events in a specific time frame."""
    events = []
    if self._events is not None:
      for event in self._events:
        if event.start < end_date and event.end > start_date:
          events.append(CalendarEvent(
            summary="Octopus Energy Free Electricity",
            start=event.start,
            end=event.end,
          ))

    return events
