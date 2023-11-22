from homeassistant.util.dt import (now)
import logging

from homeassistant.core import HomeAssistant

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass,
)

from .base import (OctopusEnergyElectricitySensor)
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCurrentElectricityDemand(CoordinatorEntity, OctopusEnergyElectricitySensor, RestoreSensor):
  """Sensor for displaying the current electricity demand."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._state = None
    self._latest_date = None
    self._attributes = {
      "last_evaluated": None
    }

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}_current_demand"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan} Current Demand"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.POWER

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.MEASUREMENT

  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return "W"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def native_value(self):
    """Handle updated data from the coordinator."""
    _LOGGER.debug('Updating OctopusEnergyCurrentElectricityConsumption')
    consumption_result = self.coordinator.data if self.coordinator is not None else None

    if (consumption_result is not None):
      self._state = consumption_result[-1]["demand"]
      self._attributes["last_evaluated"] = now()

    return self._state

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state == "unknown" else state.state
      self._attributes = dict_to_typed_dict(state.attributes)

      if "last_updated_timestamp" in self._attributes:
        del self._attributes["last_updated_timestamp"]
    
      _LOGGER.debug(f'Restored OctopusEnergyCurrentElectricityDemand state: {self._state}')