import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass
)
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)

class OctopusEnergySavingSessionPoints(CoordinatorEntity, SensorEntity, RestoreEntity):
  """Sensor for determining saving session points"""

  def __init__(self, hass: HomeAssistant, coordinator):
    """Init sensor."""

    super().__init__(coordinator)
  
    self._state = None
    self._attributes = {}

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_saving_session_points"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Saving Session Points"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:leaf"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL_INCREASING

  @property
  def state(self):
    """Update the points based on data."""
    saving_session = self.coordinator.data
    if (saving_session is not None and "points" in saving_session):
      self._state = saving_session["points"]
    else:
      self._state = 0

    return self._state

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None and self._state is None:
      self._state = state.state
      self._attributes = {}
      for x in state.attributes.keys():
        self._attributes[x] = state.attributes[x]
    
      _LOGGER.debug(f'Restored OctopusEnergySavingSessionPoints state: {self._state}')