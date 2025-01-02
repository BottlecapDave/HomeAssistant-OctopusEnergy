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
  SensorStateClass
)

from .base import (OctopusEnergyGasSensor)
from ..utils.attributes import dict_to_typed_dict
from ..coordinators.gas_standing_charges import GasStandingChargeCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyGasCurrentStandingCharge(CoordinatorEntity, OctopusEnergyGasSensor, RestoreSensor):
  """Sensor for displaying the current standing charge."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)

    self._state = None
    self._latest_date = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f'octopus_energy_gas_{self._serial_number}_{self._mprn}_current_standing_charge';
    
  @property
  def name(self):
    """Name of the sensor."""
    return f'Current Standing Charge Gas ({self._serial_number}/{self._mprn})'
  
  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.MONETARY

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-gbp"

  @property
  def native_unit_of_measurement(self):
    """Unit of measurement of the sensor."""
    return "GBP"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the latest gas standing charge"""
    _LOGGER.debug('Updating OctopusEnergyGasCurrentStandingCharge')

    standard_charge_result: GasStandingChargeCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    
    if standard_charge_result is not None and standard_charge_result.standing_charge is not None:
      self._latest_date = standard_charge_result.standing_charge["start"]
      self._state = standard_charge_result.standing_charge["value_inc_vat"] / 100

      # Adjust our period, as our gas only changes on a daily basis
      self._attributes["start"] = standard_charge_result.standing_charge["start"]
      self._attributes["end"] = standard_charge_result.standing_charge["end"]
    else:
      self._state = None

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
      self._attributes = dict_to_typed_dict(state.attributes, ['valid_from', 'valid_to'])
      _LOGGER.debug(f'Restored OctopusEnergyGasCurrentStandingCharge state: {self._state}')