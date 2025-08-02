import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.number import RestoreNumber, NumberDeviceClass, NumberMode
from homeassistant.util.dt import (now)

from .base import (BaseOctopusEnergyHeatPumpSensor)
from ..utils.attributes import dict_to_typed_dict
from ..api_client.heat_pump import HeatPump
from ..coordinators.heat_pump_configuration_and_status import HeatPumpCoordinatorResult
from ..api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyHeatPumpFixedTargetFlowTemperature(CoordinatorEntity, RestoreNumber, BaseOctopusEnergyHeatPumpSensor):
  """Sensor for reading and setting the fixed target flow temperature of a heat pump."""

  def __init__(self, hass: HomeAssistant, client: OctopusEnergyApiClient, coordinator, heat_pump_id: str, heat_pump: HeatPump):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyHeatPumpSensor.__init__(self, hass, heat_pump_id, heat_pump, entity_domain="number")

  
    self._state = None
    self._client = client
    self._last_updated = None
    self._attr_native_min_value = 30
    self._attr_native_max_value = 70
    self._attr_native_step = 1
    self._attr_mode = NumberMode.BOX

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_heat_pump_{self._heat_pump_id}_fixed_target_flow_temperature"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Fixed Target Flow Temperature Heat Pump ({self._heat_pump_id})"

  @property
  def device_class(self):
    """The type of sensor"""
    return NumberDeviceClass.TEMPERATURE
  
  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return UnitOfTemperature.CELSIUS

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self) -> float:
    return self._state
  
  async def async_set_native_value(self, value: float) -> None:
    """Set new value."""
    if value and value % self._attr_native_step == 0:
      try:
        await self._client.async_set_heat_pump_fixed_target_flow_temp(
          self._heat_pump_id,
          value
        )
      except Exception as e:
        if self._is_mocked:
          _LOGGER.warning(f'Suppress async_set_native_value error due to mocking mode: {e}')
        else:
          raise

      self._state = value
      self._last_updated = now()
      self.async_write_ha_state()
    else:
      raise Exception(f"Value must be between {self._attr_native_min_value} and {self._attr_native_max_value} and be a multiple of {self._attr_native_step}")
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the configured fixed target flow temperature for the heat pump."""
    current = now()
    result: HeatPumpCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    
    if (result is not None 
        and result.data is not None 
        and result.data.octoHeatPumpControllerConfiguration is not None
        and result.data.octoHeatPumpControllerConfiguration.heatPump is not None
        and result.data.octoHeatPumpControllerConfiguration.heatPump.heatingFlowTemperature is not None
        and result.data.octoHeatPumpControllerConfiguration.heatPump.heatingFlowTemperature.currentTemperature is not None):
      _LOGGER.debug(f"Updating OctopusEnergyHeatPumpNumberFixedTargetFlowTemperature for '{self._heat_pump_id}'")

      self._state = float(result.data.octoHeatPumpControllerConfiguration.heatPump.heatingFlowTemperature.currentTemperature.value)
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
    
      _LOGGER.debug(f'Restored OctopusEnergyHeatPumpNumberFixedTargetFlowTemperature state: {self._state}')
