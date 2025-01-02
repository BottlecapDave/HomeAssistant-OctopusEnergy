import logging

from custom_components.octopus_energy.storage.rate_weightings import async_save_cached_rate_weightings
from homeassistant.exceptions import ServiceValidationError

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
  SensorStateClass,
)

from .base import (OctopusEnergyElectricitySensor)
from ..utils.attributes import dict_to_typed_dict
from ..coordinators.electricity_rates import ElectricityRatesCoordinatorResult
from ..utils.weightings import merge_weightings, validate_rate_weightings
from ..const import DATA_CUSTOM_RATE_WEIGHTINGS_KEY, DOMAIN

from ..utils.rate_information import (get_current_rate_information)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyElectricityCurrentRate(CoordinatorEntity, OctopusEnergyElectricitySensor, RestoreSensor):
  """Sensor for displaying the current rate."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point, electricity_price_cap, account_id: str):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._state = None
    self._last_updated = None
    self._electricity_price_cap = electricity_price_cap
    self._account_id = account_id

    self._attributes = {
      "mpan": self._mpan,
      "serial_number": self._serial_number,
      "is_export": self._is_export,
      "is_smart_meter": self._is_smart_meter,
      "tariff": None,
      "start": None,
      "end": None,
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
    return f"Current Rate {self._export_name_addition}Electricity ({self._serial_number} {self._mpan})"
  
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
    # Find the current rate. We only need to do this every half an hour
    current = now()
    rates_result: ElectricityRatesCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if (rates_result is not None):
      _LOGGER.debug(f"Updating OctopusEnergyElectricityCurrentRate for '{self._mpan}/{self._serial_number}'")

      rate_information = get_current_rate_information(rates_result.rates, current)

      if rate_information is not None:
        self._attributes = {
          "mpan": self._mpan,
          "serial_number": self._serial_number,
          "is_export": self._is_export,
          "is_smart_meter": self._is_smart_meter,
          "tariff": rate_information["current_rate"]["tariff_code"],
          "start":  rate_information["current_rate"]["start"],
          "end":  rate_information["current_rate"]["end"],
          "is_capped":  rate_information["current_rate"]["is_capped"],
          "is_intelligent_adjusted":  rate_information["current_rate"]["is_intelligent_adjusted"],
          "current_day_min_rate": rate_information["min_rate_today"],
          "current_day_max_rate": rate_information["max_rate_today"],
          "current_day_average_rate": rate_information["average_rate_today"],
        }

        self._state = rate_information["current_rate"]["value_inc_vat"]
      else:
        self._attributes = {
          "mpan": self._mpan,
          "serial_number": self._serial_number,
          "is_export": self._is_export,
          "is_smart_meter": self._is_smart_meter,
          "tariff": None,
          "start": None,
          "end": None,
          "is_capped": None,
          "is_intelligent_adjusted": None,
          "current_day_min_rate": None,
          "current_day_max_rate": None,
          "current_day_average_rate": None
        }

        self._state = None

      if self._electricity_price_cap is not None:
        self._attributes["price_cap"] = self._electricity_price_cap

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
      _LOGGER.debug(f'Restored OctopusEnergyElectricityCurrentRate state: {self._state}')

  @callback
  async def async_register_rate_weightings(self, weightings):
    """Apply rate weightings"""
    result = validate_rate_weightings(weightings)
    if result.success == False:
      raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="invalid_rate_weightings",
        translation_placeholders={ 
          "error": result.error_message,
        },
      )
    
    key = DATA_CUSTOM_RATE_WEIGHTINGS_KEY.format(self._mpan)
    weightings = result.weightings
    weightings = merge_weightings(
      now(),
      weightings,
      self._hass.data[DOMAIN][self._account_id][key] 
      if key in self._hass.data[DOMAIN][self._account_id] 
      else []
    )

    self._hass.data[DOMAIN][self._account_id][key] = weightings
    
    await async_save_cached_rate_weightings(self._hass, self._mpan, result.weightings)