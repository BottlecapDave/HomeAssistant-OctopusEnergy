import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass,
)
from homeassistant.const import (
    UnitOfVolume
)

from homeassistant.util.dt import (now)

from ..coordinators.current_consumption import CurrentConsumptionCoordinatorResult
from .base import (OctopusEnergyGasSensor)
from ..utils.attributes import dict_to_typed_dict
from . import convert_kwh_to_m3

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCurrentTotalGasConsumptionCubicMeters(CoordinatorEntity, OctopusEnergyGasSensor, RestoreSensor):
  """Sensor for displaying the current total gas consumption in m3."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point, calorific_value: float):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)

    self._state = None
    self._last_reset = None
    self._calorific_value = calorific_value
    
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)

  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return self._is_smart_meter

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_current_total_consumption_m3"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Current Total Consumption (m3) Gas ({self._serial_number}/{self._mprn})"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.GAS

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL_INCREASING

  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return UnitOfVolume.CUBIC_METERS

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:fire"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the current days accumulative consumption"""
    current = now()
    consumption_result: CurrentConsumptionCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    consumption_data = consumption_result.data if consumption_result is not None else None

    if (consumption_data is not None and len(consumption_data) > 0):
      _LOGGER.debug(f"Calculated total gas consumption for '{self._mprn}/{self._serial_number}'...")

      if consumption_data[-1]["total_consumption"] is not None:
        if "is_kwh" not in consumption_data[-1] or consumption_data[-1]["is_kwh"] == True:
          self._state = convert_kwh_to_m3(consumption_data[-1]["total_consumption"], self._calorific_value) if consumption_data[-1]["total_consumption"] is not None and consumption_data[-1]["total_consumption"] != 0 else None
        else:
          self._state = consumption_data[-1]["total_consumption"] if consumption_data[-1]["total_consumption"] is not None and consumption_data[-1]["total_consumption"] != 0 else None

        self._attributes = {
          "mprn": self._mprn,
          "serial_number": self._serial_number,
          "is_smart_meter": self._is_smart_meter,
        }

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
    
      _LOGGER.debug(f'Restored state: {self._state}')