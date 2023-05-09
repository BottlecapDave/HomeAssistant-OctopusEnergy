import logging
from datetime import datetime
from ..statistics.consumption import async_import_external_statistics_from_consumption

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
    ENERGY_KILO_WATT_HOUR
)

from . import (
  calculate_electricity_consumption,
)

from .base import (OctopusEnergyElectricitySensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyPreviousAccumulativeElectricityConsumption(CoordinatorEntity, OctopusEnergyElectricitySensor):
  """Sensor for displaying the previous days accumulative electricity reading."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._state = None
    self._last_reset = None
    self._hass = hass

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_previous_accumulative_consumption"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Previous Accumulative Consumption"

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
    return self._last_reset

  @property
  def state(self):
    """Retrieve the previous days accumulative consumption"""
    return self._state
  
  @property
  def should_poll(self) -> bool:
    return True
    
  async def async_update(self):
    consumption_data = self.coordinator.data["consumption"] if "consumption" in self.coordinator.data else None
    rate_data = self.coordinator.data["rates"] if "rates" in self.coordinator.data else None

    consumption_result = calculate_electricity_consumption(
      consumption_data,
      self._last_reset
    )

    if (consumption_result is not None):
      _LOGGER.debug(f"Calculated previous electricity consumption for '{self._mpan}/{self._serial_number}'...")

      await async_import_external_statistics_from_consumption(
        self._hass,
        f"electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_previous_accumulative_consumption",
        self.name,
        consumption_data,
        rate_data,
        ENERGY_KILO_WATT_HOUR,
        "consumption"
      )

      self._state = consumption_result["total"]
      self._last_reset = consumption_result["last_reset"]

      self._attributes = {
        "mpan": self._mpan,
        "serial_number": self._serial_number,
        "is_export": self._is_export,
        "is_smart_meter": self._is_smart_meter,
        "total": consumption_result["total"],
        "last_calculated_timestamp": consumption_result["last_calculated_timestamp"],
        "charges": consumption_result["consumptions"]
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

      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeElectricityConsumption state: {self._state}')