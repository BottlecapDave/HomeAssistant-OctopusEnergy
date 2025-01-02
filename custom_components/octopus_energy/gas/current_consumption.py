import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.util.dt import (now)

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass
)
from homeassistant.const import (
    UnitOfEnergy
)

from ..coordinators.current_consumption import CurrentConsumptionCoordinatorResult
from .base import (OctopusEnergyGasSensor)
from ..utils.attributes import dict_to_typed_dict

from ..utils.consumption import (calculate_current_consumption, get_current_consumption_delta, get_total_consumption)

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
    self._last_evaluated = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_current_consumption"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Current Consumption Gas ({self._serial_number}/{self._mprn})"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.ENERGY

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return UnitOfEnergy.KILO_WATT_HOUR

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
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """The current consumption for the meter."""
    _LOGGER.debug('Updating OctopusEnergyCurrentGasConsumption')
    consumption_result: CurrentConsumptionCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    current_date = now()

    result = calculate_current_consumption(
      current_date,
      consumption_result,
      self._state,
      self._last_evaluated if self._last_evaluated is not None else current_date,
      self._previous_total_consumption
    )

    self._state = result.state
    self._latest_date = result.last_evaluated
    self._previous_total_consumption = result.total_consumption
    self._last_evaluated = current_date

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)

      if "last_updated_timestamp" in self._attributes:
        del self._attributes["last_updated_timestamp"]
        
      # With this included, was causing issues with statistics. Why other sensors are not effected...
      if "last_reset" in self._attributes:
        del self._attributes["last_reset"]
    
      _LOGGER.debug(f'Restored OctopusEnergyCurrentGasConsumption state: {self._state}')