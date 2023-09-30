from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant

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
from ..utils.rate_information import get_current_rate_information

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
      "all_rates": [],
      "applicable_rates": [],
      "valid_from": None,
      "valid_to": None,
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
  def unit_of_measurement(self):
    """Unit of measurement of the sensor."""
    return "GBP/kWh"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state(self):
    """Retrieve the current rate for the sensor."""
    current = now()
    rates = self.coordinator.data.rates if self.coordinator is not None and self.coordinator.data is not None else None
    if (self._last_updated is None or self._last_updated < (current - timedelta(minutes=30)) or (current.minute % 30) == 0):
      _LOGGER.debug(f"Updating OctopusEnergyGasCurrentRate for '{self._mprn}/{self._serial_number}'")

      rate_information = get_current_rate_information(rates, current)

      if rate_information is not None:
        self._attributes = {
          "mprn": self._mprn,
          "serial_number": self._serial_number,
          "is_smart_meter": self._is_smart_meter,
          "tariff": self._tariff_code,
          "valid_from": rate_information["current_rate"]["valid_from"],
          "valid_to": rate_information["current_rate"]["valid_to"],
          "is_capped": rate_information["current_rate"]["is_capped"],
          "all_rates": rate_information["all_rates"],
          "applicable_rates": rate_information["applicable_rates"],
        }

        self._state = rate_information["current_rate"]["value_inc_vat"] / 100
      else:
        self._attributes = {
          "mprn": self._mprn,
          "serial_number": self._serial_number,
          "is_smart_meter": self._is_smart_meter,
          "tariff": self._tariff_code,
          "valid_from": None,
          "valid_to": None,
          "is_capped": None,
          "all_rates": [],
          "applicable_rates": [],
        }

        self._state = None

      if self._gas_price_cap is not None:
        self._attributes["price_cap"] = self._gas_price_cap

      self._last_updated = current

    return self._state

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
    
      _LOGGER.debug(f'Restored OctopusEnergyGasCurrentRate state: {self._state}')