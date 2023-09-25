from homeassistant.util.dt import (now)
import logging

from homeassistant.core import HomeAssistant

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass
)
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR
)

from .base import (OctopusEnergyGasSensor)

from ..utils.consumption import (get_current_consumption_delta, get_total_consumption)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCurrentGasConsumption(CoordinatorEntity, OctopusEnergyGasSensor, RestoreSensor):
  """Sensor for displaying the current gas consumption."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)

    self._state = None
    self._latest_date = None
    self._previous_total_consumption = None
    self._attributes = {
      "last_updated_timestamp": None
    }

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_current_consumption"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Gas {self._serial_number} {self._mprn} Current Consumption"

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
    return "mdi:fire"

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
    """The current consumption for the meter."""
    _LOGGER.debug('Updating OctopusEnergyCurrentGasConsumption')
    consumption_result = self.coordinator.data if self.coordinator is not None else None

    current_date = now()
    if (consumption_result is not None):
      total_consumption = get_total_consumption(consumption_result)
      self._state = get_current_consumption_delta(current_date,
                                                  total_consumption,
                                                  self._attributes["last_updated_timestamp"] if self._attributes["last_updated_timestamp"] is not None else current_date,
                                                  self._previous_total_consumption)
      if (self._state is not None):
        self._latest_date = current_date
        self._attributes["last_updated_timestamp"] = current_date

      # Store the total consumption ready for the next run
      self._previous_total_consumption = total_consumption
    
    return self._state

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = state.state
    
      _LOGGER.debug(f'Restored OctopusEnergyCurrentGasConsumption state: {self._state}')