from datetime import timedelta
import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.util.dt import (now)
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
from ..utils.rate_information import get_previous_rate_information
from ..coordinators.gas_rates import GasRatesCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyGasPreviousRate(CoordinatorEntity, OctopusEnergyGasSensor, RestoreSensor):
  """Sensor for displaying the previous rate."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)

    self._state = None
    self._last_updated = None

    self._attributes = {
      "mprn": self._mprn,
      "serial_number": self._serial_number,
      "is_smart_meter": self._is_smart_meter,
      "start": None,
      "end": None,
    }

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f'octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_rate'
    
  @property
  def name(self):
    """Name of the sensor."""
    return f'Previous Rate Gas ({self._serial_number}/{self._mprn})'
  
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
    return "GBP/kWh"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the previous rate for the sensor."""
    current = now()
    rates_result: GasRatesCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if (rates_result is not None):
      _LOGGER.debug(f"Updating OctopusEnergyGasPreviousRate for '{self._mprn}/{self._serial_number}'")

      rate_information = get_previous_rate_information(rates_result.rates, current)

      if rate_information is not None:
        self._attributes = {
          "mprn": self._mprn,
          "serial_number": self._serial_number,
          "is_smart_meter": self._is_smart_meter,
          "start": rate_information["previous_rate"]["start"],
          "end": rate_information["previous_rate"]["end"],
        }

        self._state = rate_information["previous_rate"]["value_inc_vat"]
      else:
        self._attributes = {
          "mprn": self._mprn,
          "serial_number": self._serial_number,
          "is_smart_meter": self._is_smart_meter,
          "start": None,
          "end": None,
        }

        self._state = None

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
      self._attributes = dict_to_typed_dict(state.attributes, ['all_rates', 'applicable_rates'])
    
      _LOGGER.debug(f'Restored OctopusEnergyGasPreviousRate state: {self._state}')