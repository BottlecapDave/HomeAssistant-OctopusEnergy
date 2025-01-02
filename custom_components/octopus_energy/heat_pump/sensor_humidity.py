from datetime import datetime
import logging
from typing import List

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass,
)

from .base import (BaseOctopusEnergyHeatPumpSensorSensor)
from ..utils.attributes import dict_to_typed_dict
from ..api_client.heat_pump import HeatPump, Sensor, SensorConfiguration
from ..coordinators.heat_pump_configuration_and_status import HeatPumpCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyHeatPumpSensorHumidity(CoordinatorEntity, BaseOctopusEnergyHeatPumpSensorSensor, RestoreSensor):
  """Sensor for displaying the humidity of a heat pump sensor."""

  def __init__(self, hass: HomeAssistant, coordinator, heat_pump_id: str, heat_pump: HeatPump, sensor: SensorConfiguration):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyHeatPumpSensorSensor.__init__(self, hass, heat_pump_id, heat_pump, sensor)

    self._state = None
    self._last_updated = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_heat_pump_{self._heat_pump_id}_{self._sensor.code}_humidity"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Humidity ({self._sensor.displayName}) Heat Pump ({self._heat_pump_id})"

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.MEASUREMENT

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.HUMIDITY

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:thermometer"

  @property
  def native_unit_of_measurement(self):
    """Unit of measurement of the sensor."""
    return "%"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the current sensor humidity."""
    current = now()
    result: HeatPumpCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if (result is not None and 
        result.data is not None and 
        result.data.octoHeatPumpControllerStatus is not None and
        result.data.octoHeatPumpControllerStatus.sensors):
      _LOGGER.debug(f"Updating OctopusEnergyHeatPumpSensorHumidity for '{self._heat_pump_id}/{self._sensor.code}'")

      self._state = None
      sensors: List[Sensor] = result.data.octoHeatPumpControllerStatus.sensors
      for sensor in sensors:
        if sensor.code == self._sensor.code and sensor.telemetry is not None:
          self._state = sensor.telemetry.humidityPercentage
          self._attributes["retrieved_at"] = datetime.fromisoformat(sensor.telemetry.retrievedAt)

      self._last_updated = current

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
      self._attributes = dict_to_typed_dict(state.attributes, [])

      self._attributes["type"] = self._sensor.type
      self._attributes["code"] = self._sensor.code
    
      _LOGGER.debug(f'Restored OctopusEnergyHeatPumpSensorHumidity state: {self._state}')