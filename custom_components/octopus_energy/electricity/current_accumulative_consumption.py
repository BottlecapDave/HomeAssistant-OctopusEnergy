from homeassistant.util.dt import (now)
import logging

from homeassistant.core import HomeAssistant

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR
)

from .base import (OctopusEnergyElectricitySensor)

from ..utils.consumption import (get_total_consumption)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCurrentAccumulativeElectricityConsumption(CoordinatorEntity, OctopusEnergyElectricitySensor):
  """Sensor for displaying the current accumulative electricity consumption."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._state = None
    self._latest_date = None
    self._previous_total_consumption = None
    self._attributes = {
      "last_updated_timestamp": None
    }

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}_current_accumulative_consumption"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan} Current Accumulative Consumption"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.ENERGY

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return ENERGY_KILO_WATT_HOUR

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def last_reset(self):
    """Return the time when the sensor was last reset, if any."""
    return self._latest_date
  
  @property
  def state(self):
    """Retrieve the latest electricity consumption"""
    _LOGGER.debug('Updating OctopusEnergyCurrentAccumulativeElectricityConsumption')
    consumption_result = self.coordinator.data

    if (consumption_result is not None and len(consumption_result) > 0):
      self._state = get_total_consumption(consumption_result)
      if (self._state is not None):
        self._latest_date = consumption_result[0]["interval_start"]
        self._attributes["last_updated_timestamp"] = now()
        self._attributes["charges"] = list(map(lambda charge: {
          "from": charge["interval_start"],
          "to": charge["interval_end"],
          "consumption": charge["consumption"]
        }, consumption_result))
    
    return self._state

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = state.state
    
      _LOGGER.debug(f'Restored OctopusEnergyCurrentAccumulativeElectricityConsumption state: {self._state}')