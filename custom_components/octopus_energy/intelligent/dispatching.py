import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from ..intelligent import (
  is_in_planned_dispatch
)

from .base import OctopusEnergyIntelligentSensor

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentDispatching(CoordinatorEntity, BinarySensorEntity, OctopusEnergyIntelligentSensor, RestoreEntity):
  """Sensor for determining if an intelligent is dispatching."""

  def __init__(self, hass: HomeAssistant, coordinator, device):
    """Init sensor."""

    super().__init__(coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)
  
    self._state = None
    self._attributes = {
      "planned_dispatches": [],
      "completed_dispatches": [],
      "last_retrieved": None
    }

    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_intelligent_dispatching"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Intelligent Dispatching"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:power-plug-battery"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    """Determine if OE is currently dispatching energy."""
    dispatches = self.coordinator.data
    if (dispatches is not None):
      self._attributes["planned_dispatches"] = self.coordinator.data["planned"]
      self._attributes["completed_dispatches"] = self.coordinator.data["completed"]

      if "last_updated" in self.coordinator.data:
        self._attributes["last_updated_timestamp"] = self.coordinator.data["last_updated"]
    else:
      self._attributes["planned_dispatches"] = []
      self._attributes["completed_dispatches"] = []

    current_date = now()
    self._state = is_in_planned_dispatch(current_date, self._attributes["planned_dispatches"])
    
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
    
    _LOGGER.debug(f'Restored OctopusEnergyIntelligentDispatching state: {self._state}')
