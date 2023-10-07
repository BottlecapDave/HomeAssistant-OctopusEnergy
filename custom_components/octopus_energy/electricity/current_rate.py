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
  SensorStateClass,
)

from .base import (OctopusEnergyElectricitySensor)

from ..utils.rate_information import (get_current_rate_information)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyElectricityCurrentRate(CoordinatorEntity, OctopusEnergyElectricitySensor, RestoreSensor):
  """Sensor for displaying the current rate."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point, tariff_code, electricity_price_cap):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._state = None
    self._last_updated = None
    self._electricity_price_cap = electricity_price_cap
    self._tariff_code = tariff_code

    self._attributes = {
      "mpan": self._mpan,
      "serial_number": self._serial_number,
      "is_export": self._is_export,
      "is_smart_meter": self._is_smart_meter,
      "tariff": self._tariff_code,
      "all_rates": [],
      "applicable_rates": [],
      "valid_from": None,
      "valid_to": None,
      "is_capped": None,
      "is_intelligent_adjusted": None,
      "current_day_min_rate": None,
      "current_day_max_rate": None,
      "current_day_average_rate": None
    }

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_current_rate"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Current Rate"
  
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
    # Find the current rate. We only need to do this every half an hour
    current = now()
    rates = self.coordinator.data.rates if self.coordinator is not None and self.coordinator.data is not None else None
    if (self._last_updated is None or self._last_updated < (current - timedelta(minutes=30)) or (current.minute % 30) == 0):
      _LOGGER.debug(f"Updating OctopusEnergyElectricityCurrentRate for '{self._mpan}/{self._serial_number}'")

      rate_information = get_current_rate_information(rates, current)

      if rate_information is not None:
        self._attributes = {
          "mpan": self._mpan,
          "serial_number": self._serial_number,
          "is_export": self._is_export,
          "is_smart_meter": self._is_smart_meter,
          "tariff": self._tariff_code,
          "valid_from":  rate_information["current_rate"]["valid_from"],
          "valid_to":  rate_information["current_rate"]["valid_to"],
          "is_capped":  rate_information["current_rate"]["is_capped"],
          "is_intelligent_adjusted":  rate_information["current_rate"]["is_intelligent_adjusted"],
          "current_day_min_rate": rate_information["min_rate_today"],
          "current_day_max_rate": rate_information["max_rate_today"],
          "current_day_average_rate": rate_information["average_rate_today"],
          "all_rates": rate_information["all_rates"],
          "applicable_rates": rate_information["applicable_rates"],
        }

        self._state = rate_information["current_rate"]["value_inc_vat"] / 100
      else:
        self._attributes = {
          "mpan": self._mpan,
          "serial_number": self._serial_number,
          "is_export": self._is_export,
          "is_smart_meter": self._is_smart_meter,
          "tariff": self._tariff_code,
          "valid_from": None,
          "valid_to": None,
          "is_capped": None,
          "is_intelligent_adjusted": None,
          "current_day_min_rate": None,
          "current_day_max_rate": None,
          "current_day_average_rate": None,
          "all_rates": [],
          "applicable_rates": [],
        }

        self._state = None

      if self._electricity_price_cap is not None:
        self._attributes["price_cap"] = self._electricity_price_cap

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
    
      _LOGGER.debug(f'Restored OctopusEnergyElectricityCurrentRate state: {self._state}')