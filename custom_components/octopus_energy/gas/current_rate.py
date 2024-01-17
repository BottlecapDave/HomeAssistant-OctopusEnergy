from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant, callback

from homeassistant.util.dt import (utcnow)
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
from ..utils.rate_information import get_current_rate_information
from ..coordinators.gas_rates import GasRatesCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyGasCurrentRate(CoordinatorEntity, OctopusEnergyGasSensor, RestoreSensor):
  """Sensor for displaying the current rate."""

  def __init__(self, hass: HomeAssistant, coordinator, tariff_code, meter, point, gas_price_cap):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)

    self._tariff_code = tariff_code
    self._gas_price_cap = gas_price_cap

    self._state = None
    self._last_updated = None

    self._attributes = {
      "mprn": self._mprn,
      "serial_number": self._serial_number,
      "is_smart_meter": self._is_smart_meter,
      "tariff": self._tariff_code,
      "start": None,
      "end": None,
      "is_capped": None,
    }

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f'octopus_energy_gas_{self._serial_number}_{self._mprn}_current_rate';
    
  @property
  def name(self):
    """Name of the sensor."""
    return f'Gas {self._serial_number} {self._mprn} Current Rate'
  
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
    """Retrieve the current rate for the sensor."""
    current = utcnow()
    rates_result: GasRatesCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if (rates_result is not None and (self._last_updated is None or self._last_updated < (current - timedelta(minutes=30)) or (current.minute % 30) == 0)):
      _LOGGER.debug(f"Updating OctopusEnergyGasCurrentRate for '{self._mprn}/{self._serial_number}'")

      rate_information = get_current_rate_information(rates_result.rates, current)

      if rate_information is not None:
        self._attributes = {
          "mprn": self._mprn,
          "serial_number": self._serial_number,
          "is_smart_meter": self._is_smart_meter,
          "tariff": self._tariff_code,
          "start": rate_information["current_rate"]["start"],
          "end": rate_information["current_rate"]["end"],
          "is_capped": rate_information["current_rate"]["is_capped"],
        }

        self._state = rate_information["current_rate"]["value_inc_vat"]
      else:
        self._attributes = {
          "mprn": self._mprn,
          "serial_number": self._serial_number,
          "is_smart_meter": self._is_smart_meter,
          "tariff": self._tariff_code,
          "start": None,
          "end": None,
          "is_capped": None,
        }

        self._state = None

      if self._gas_price_cap is not None:
        self._attributes["price_cap"] = self._gas_price_cap

      self._last_updated = current

    if rates_result is not None:
      self._attributes["data_last_retrieved"] = rates_result.last_retrieved

    self._attributes["last_evaluated"] = current
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state == "unknown" else state.state
      self._attributes = dict_to_typed_dict(state.attributes, ['all_rates', 'applicable_rates'])
    
      _LOGGER.debug(f'Restored OctopusEnergyGasCurrentRate state: {self._state}')