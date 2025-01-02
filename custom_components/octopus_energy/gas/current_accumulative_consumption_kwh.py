import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass
)
from homeassistant.const import (
    UnitOfEnergy
)

from ..coordinators import MultiCoordinatorEntity
from ..coordinators.current_consumption import CurrentConsumptionCoordinatorResult
from .base import (OctopusEnergyGasSensor)
from ..utils.attributes import dict_to_typed_dict

from . import calculate_gas_consumption_and_cost

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCurrentAccumulativeGasConsumptionKwh(MultiCoordinatorEntity, OctopusEnergyGasSensor, RestoreSensor):
  """Sensor for displaying the current accumulative gas consumption."""

  def __init__(self, hass: HomeAssistant, coordinator, rates_coordinator, standing_charge_coordinator, meter, point, calorific_value):
    """Init sensor."""
    MultiCoordinatorEntity.__init__(self, coordinator, [rates_coordinator, standing_charge_coordinator])
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)
    
    self._hass = hass

    self._state = None
    self._last_reset = None
    self._calorific_value = calorific_value
    self._rates_coordinator = rates_coordinator
    self._standing_charge_coordinator = standing_charge_coordinator

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_current_accumulative_consumption_kwh"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Current Accumulative Consumption Gas ({self._serial_number}/{self._mprn})"

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
    return self._last_reset
  
  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the current days accumulative consumption"""
    consumption_result: CurrentConsumptionCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    consumption_data = consumption_result.data if consumption_result is not None else None
    rate_data = self._rates_coordinator.data.rates if self._rates_coordinator is not None and self._rates_coordinator.data is not None else None
    standing_charge = self._standing_charge_coordinator.data.standing_charge["value_inc_vat"] if self._standing_charge_coordinator is not None and self._standing_charge_coordinator.data is not None and self._standing_charge_coordinator.data.standing_charge is not None else None
    
    consumption_and_cost = calculate_gas_consumption_and_cost(
      consumption_data,
      rate_data,
      standing_charge,
      None, # We want to always recalculate
      "kwh", # Our current sensor always reports in kwh
      self._calorific_value
    )

    if (consumption_and_cost is not None):
      _LOGGER.debug(f"Calculated previous gas consumption for '{self._mprn}/{self._serial_number}'...")

      self._state = consumption_and_cost["total_consumption_kwh"]
      self._last_reset = consumption_and_cost["last_reset"]

      self._attributes = {
        "mprn": self._mprn,
        "serial_number": self._serial_number,
        "is_estimated": False,
        "charges": list(map(lambda charge: {
          "start": charge["start"],
          "end": charge["end"],
          "consumption": charge["consumption_kwh"]
        }, consumption_and_cost["charges"])),
        "calorific_value": self._calorific_value
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
      self._attributes = dict_to_typed_dict(state.attributes, ["total"])
    
      _LOGGER.debug(f'Restored OctopusEnergyCurrentAccumulativeGasConsumption state: {self._state}')