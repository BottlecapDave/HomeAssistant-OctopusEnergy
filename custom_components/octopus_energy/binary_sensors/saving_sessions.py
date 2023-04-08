import logging

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from ..sensors import (
  current_saving_sessions_event,
  get_next_saving_sessions_event
)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergySavingSessions(CoordinatorEntity, BinarySensorEntity, RestoreEntity):
  """Sensor for determining if a saving session is active."""

  def __init__(self, coordinator):
    """Init sensor."""

    super().__init__(coordinator)
  
    self._state = None
    self._events = []
    self._attributes = {
      "joined_events": [],
      "next_joined_event_start": None
    }

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_saving_sessions"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Saving Session"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:leaf"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    """The state of the sensor."""
    saving_session = self.coordinator.data
    if (saving_session is not None and "events" in saving_session):
      self._events = saving_session["events"]
    else:
      self._events = []
    
    self._attributes = {
      "joined_events": self._events,
      "next_joined_event_start": None,
      "next_joined_event_end": None,
      "next_joined_event_duration_in_minutes": None
    }

    current_date = now()
    current_event = current_saving_sessions_event(current_date, self._events)
    if (current_event is not None):
      self._state = True
      self._attributes["current_joined_event_start"] = current_event["start"]
      self._attributes["current_joined_event_end"] = current_event["end"]
      self._attributes["current_joined_event_duration_in_minutes"] = current_event["duration_in_minutes"]
    else:
      self._state = False

    next_event = get_next_saving_sessions_event(current_date, self._events)
    if (next_event is not None):
      self._attributes["next_joined_event_start"] = next_event["start"]
      self._attributes["next_joined_event_end"] = next_event["end"]
      self._attributes["next_joined_event_duration_in_minutes"] = next_event["duration_in_minutes"]

    return self._state

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = state.state
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored state: {self._state}')
