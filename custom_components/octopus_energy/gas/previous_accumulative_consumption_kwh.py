import logging
from datetime import datetime

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass
)
from homeassistant.const import (
    UnitOfEnergy
)

from homeassistant.util.dt import (utcnow)

from . import (
  calculate_gas_consumption_and_cost,
)

from .base import (OctopusEnergyGasSensor)
from ..utils.attributes import dict_to_typed_dict
from ..coordinators.previous_consumption_and_rates import PreviousConsumptionCoordinatorResult
from ..statistics.consumption import async_import_external_statistics_from_consumption, get_gas_consumption_statistic_unique_id

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyPreviousAccumulativeGasConsumptionKwh(CoordinatorEntity, OctopusEnergyGasSensor, RestoreSensor):
  """Sensor for displaying the previous days accumulative gas consumption in kwh."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point, calorific_value):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)

    self._hass = hass
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
    return f"Previous Accumulative Consumption (kWh) Gas ({self._serial_number}/{self._mprn})"

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
  def native_value(self):
    """Retrieve the previous days accumulative consumption"""
    return self._state
  
  @property
  def should_poll(self) -> bool:
    return True
    
  async def async_update(self):
    await super().async_update()

    if not self.enabled:
      return
    
    result: PreviousConsumptionCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    consumption_data = result.consumption if result is not None else None
    rate_data = result.rates if result is not None else None
    standing_charge = result.standing_charge if result is not None else None

    consumption_and_cost = calculate_gas_consumption_and_cost(
      consumption_data,
      rate_data,
      standing_charge,
      self._last_reset,
      self._native_consumption_units,
      self._calorific_value
    )

    if (consumption_and_cost is not None):
      _LOGGER.debug(f"Calculated previous gas consumption for '{self._mprn}/{self._serial_number}'...")

      await async_import_external_statistics_from_consumption(
        utcnow(),
        self._hass,
        get_gas_consumption_statistic_unique_id(self._serial_number, self._mprn, True),
        self.name,
        consumption_and_cost["charges"],
        rate_data,
        UnitOfEnergy.KILO_WATT_HOUR,
        "consumption_kwh"
      )

      self._state = consumption_and_cost["total_consumption_kwh"]
      self._last_reset = consumption_and_cost["last_reset"]

      self._attributes = {
        "mprn": self._mprn,
        "serial_number": self._serial_number,
        "is_estimated": self._native_consumption_units == "m³",
        "charges": list(map(lambda charge: {
          "start": charge["start"],
          "end": charge["end"],
          "consumption_m3": charge["consumption_m3"],
          "consumption_kwh": charge["consumption_kwh"]
        }, consumption_and_cost["charges"])),
        "calorific_value": self._calorific_value
      }
    
    self._attributes = dict_to_typed_dict(self._attributes)

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)
    
      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeGasConsumptionKwh state: {self._state}')