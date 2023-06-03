import logging
from datetime import datetime
from ..statistics.consumption import async_import_external_statistics_from_consumption

from homeassistant.core import HomeAssistant
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
  async_calculate_gas_consumption_and_cost,
)

from .base import (OctopusEnergyGasSensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyPreviousAccumulativeGasConsumptionKwh(CoordinatorEntity, OctopusEnergyGasSensor):
  """Sensor for displaying the previous days accumulative gas consumption in kwh."""

  def __init__(self, hass: HomeAssistant, coordinator, tariff_code, meter, point, calorific_value):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)

    self._hass = hass
    self._tariff_code = tariff_code
    self._native_consumption_units = meter["consumption_units"]
    self._state = None
    self._last_reset = None
    self._calorific_value = calorific_value

  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return self._is_smart_meter

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_accumulative_consumption_kwh"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Gas {self._serial_number} {self._mprn} Previous Accumulative Consumption (kWh)"

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
    consumption_data = self.coordinator.data["consumption"] if self.coordinator.data is not None and "consumption" in self.coordinator.data else None
    rate_data = self.coordinator.data["rates"] if self.coordinator.data is not None and "rates" in self.coordinator.data else None
    standing_charge = self.coordinator.data["standing_charge"] if self.coordinator.data is not None and "standing_charge" in self.coordinator.data else None

    consumption_and_cost = await async_calculate_gas_consumption_and_cost(
      consumption_data,
      rate_data,
      standing_charge,
      self._last_reset,
      self._tariff_code,
      self._native_consumption_units,
      self._calorific_value
    )

    if (consumption_and_cost is not None):
      _LOGGER.debug(f"Calculated previous gas consumption for '{self._mprn}/{self._serial_number}'...")

      await async_import_external_statistics_from_consumption(
        self._hass,
        f"gas_{self._serial_number}_{self._mprn}_previous_accumulative_consumption_kwh",
        self.name,
        consumption_and_cost["charges"],
        rate_data,
        ENERGY_KILO_WATT_HOUR,
        "consumption_kwh",
        False
      )

      self._state = consumption_and_cost["total_consumption_kwh"]
      self._last_reset = consumption_and_cost["last_reset"]

      self._attributes = {
        "mprn": self._mprn,
        "serial_number": self._serial_number,
        "is_estimated": self._native_consumption_units == "m³",
        "last_calculated_timestamp": consumption_and_cost["last_calculated_timestamp"],
        "charges": list(map(lambda charge: {
          "from": charge["from"],
          "to": charge["to"],
          "consumption_m3": charge["consumption_m3"],
          "consumption_kwh": charge["consumption_kwh"]
        }, consumption_and_cost["charges"])),
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
    
      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeGasConsumptionKwh state: {self._state}')