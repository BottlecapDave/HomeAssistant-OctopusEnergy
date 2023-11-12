import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorStateClass
)
from ..utils import account_id_to_unique_key
from ..coordinators.wheel_of_fortune import WheelOfFortuneSpinsCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyWheelOfFortuneElectricitySpins(CoordinatorEntity, RestoreSensor):
  """Sensor for current wheel of fortune spins for electricity"""

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_id = account_id
    self._state = None
    self._attributes = {
      "last_evaluated": None
    }
    self._last_evaluated = None

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{account_id_to_unique_key(self._account_id)}_wheel_of_fortune_spins_electricity"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy {self._account_id} Wheel Of Fortune Spins Electricity"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:star-circle"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def state(self):
    result: WheelOfFortuneSpinsCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if result is not None:
      self._state = result.spins.electricity
      self._attributes["last_evaluated"] = result.last_retrieved

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
    
      _LOGGER.debug(f'Restored OctopusEnergyWheelOfFortuneElectricitySpins state: {self._state}')