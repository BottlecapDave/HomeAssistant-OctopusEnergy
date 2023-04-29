import logging
from datetime import datetime
from ..import_statistic import async_import_statistics_from_consumption

from homeassistant.core import HomeAssistant
from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)
from homeassistant.const import (
    VOLUME_CUBIC_METERS
)

from . import (
  calculate_gas_consumption,
)

from .base import (OctopusEnergyGasSensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyPreviousAccumulativeGasConsumption(CoordinatorEntity, OctopusEnergyGasSensor):
  """Sensor for displaying the previous days accumulative gas reading."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point, calorific_value):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)

    self._hass = hass
    self._native_consumption_units = meter["consumption_units"]
    self._state = None
    self._last_reset = None
    self._calorific_value = calorific_value

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_accumulative_consumption"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Gas {self._serial_number} {self._mprn} Previous Accumulative Consumption"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.GAS

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return VOLUME_CUBIC_METERS

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
    return self._last_reset

  @property
  def state(self):
    """Retrieve the previous days accumulative consumption"""
    return self._state
  
  @property
  def should_poll(self) -> bool:
    return True
    
  async def async_update(self):
    consumption = calculate_gas_consumption(
      self.coordinator.data,
      self._last_reset,
      self._native_consumption_units,
      self._calorific_value
    )

    if (consumption is not None):
      _LOGGER.debug(f"Calculated previous gas consumption for '{self._mprn}/{self._serial_number}'...")

      if self._last_reset is not None and self._last_reset != consumption["last_reset"] and consumption["consumptions"] is not None:
        await async_import_statistics_from_consumption(
          self._hass,
          utcnow(),
          self.unique_id,
          self.name,
          consumption["consumptions"],
          VOLUME_CUBIC_METERS,
          "consumption_m3"
        )
        _LOGGER.debug(f"Imported statistics for '{self._mprn}/{self._serial_number}'...")

      self._state = consumption["total_m3"]
      self._last_reset = consumption["last_reset"]

      self._attributes = {
        "mprn": self._mprn,
        "serial_number": self._serial_number,
        "is_estimated": self._native_consumption_units != "m³",
        "total_kwh": consumption["total_kwh"],
        "total_m3": consumption["total_m3"],
        "last_calculated_timestamp": consumption["last_calculated_timestamp"],
        "charges": consumption["consumptions"],
        "calorific_value": self._calorific_value
      }

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

        if x == "last_reset":
          self._last_reset = datetime.strptime(state.attributes[x], "%Y-%m-%dT%H:%M:%S%z")
    
      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeGasConsumption state: {self._state}')