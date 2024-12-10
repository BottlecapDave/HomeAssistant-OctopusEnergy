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
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from . import (
  current_octoplus_sessions_event,
  get_next_octoplus_sessions_event
)

from ..utils.attributes import dict_to_typed_dict
from ..coordinators.free_electricity_sessions import FreeElectricitySessionsCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyFreeElectricitySessions(CoordinatorEntity, BinarySensorEntity, RestoreEntity):
  """Sensor for determining if a free electricity session is active."""
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_id = account_id
    self._state = None
    self._events = []
    self._attributes = {
      "current_event_start": None,
      "current_event_end": None,
      "current_event_duration_in_minutes": None,
      "next_event_start": None,
      "next_event_end": None,
      "next_event_duration_in_minutes": None
    }

    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

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
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine if the user is in a saving session."""
    self._attributes = {
      "current_event_start": None,
      "current_event_end": None,
      "current_event_duration_in_minutes": None,
      "next_event_start": None,
      "next_event_end": None,
      "next_event_duration_in_minutes": None
    }

    free_electricity_session: FreeElectricitySessionsCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    if (free_electricity_session is not None):
      self._events = free_electricity_session.events
    else:
      self._events = []

    current_date = utcnow()
    current_event = current_octoplus_sessions_event(current_date, self._events)
    if (current_event is not None):
      self._state = True
      self._attributes["current_event_start"] = current_event.start
      self._attributes["current_event_end"] = current_event.end
      self._attributes["current_event_duration_in_minutes"] = current_event.duration_in_minutes
    else:
      self._state = False

    next_event = get_next_octoplus_sessions_event(current_date, self._events)
    if (next_event is not None):
      self._attributes["next_event_start"] = next_event.start
      self._attributes["next_event_end"] = next_event.end
      self._attributes["next_event_duration_in_minutes"] = next_event.duration_in_minutes

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or state.state is None else state.state.lower() == 'on'
      self._attributes = dict_to_typed_dict(state.attributes)
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored state: {self._state}')
