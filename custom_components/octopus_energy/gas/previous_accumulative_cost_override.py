import logging
import asyncio

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

from homeassistant.util.dt import (utcnow)

from . import (
  calculate_gas_consumption_and_cost
)

from ..api_client import (ApiException, OctopusEnergyApiClient)

from .base import (OctopusEnergyGasSensor)
from ..utils.attributes import dict_to_typed_dict
from ..utils.requests import calculate_next_refresh
from ..coordinators.previous_consumption_and_rates import PreviousConsumptionCoordinatorResult
from ..utils import get_tariff_parts, private_rates_to_public_rates

from ..const import CONFIG_TARIFF_COMPARISON_NAME, CONFIG_TARIFF_COMPARISON_PRODUCT_CODE, CONFIG_TARIFF_COMPARISON_TARIFF_CODE, EVENT_GAS_PREVIOUS_CONSUMPTION_TARIFF_COMPARISON_RATES, MINIMUM_CONSUMPTION_DATA_LENGTH, REFRESH_RATE_IN_MINUTES_PREVIOUS_CONSUMPTION

_LOGGER = logging.getLogger(__name__)
  
class OctopusEnergyPreviousAccumulativeGasCostOverride(CoordinatorEntity, OctopusEnergyGasSensor, RestoreSensor):
  """Sensor for displaying the previous days accumulative gas cost for a different tariff."""

  def __init__(self, hass: HomeAssistant, account_id: str, coordinator, client: OctopusEnergyApiClient, meter, point, calorific_value, config):
    """Init sensor."""
    
    self._hass = hass
    self._client = client
    self._config = config
    self._native_consumption_units = meter["consumption_units"]
    self._account_id = account_id

    self._state = None
    self._last_reset = None
    self._calorific_value = calorific_value

    self._next_refresh = None
    self._last_retrieved  = None
    self._request_attempts = 1

    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_accumulative_cost_{self._config[CONFIG_TARIFF_COMPARISON_NAME]}"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"{self._config[CONFIG_TARIFF_COMPARISON_NAME]} Previous Accumulative Cost Override Gas ({self._serial_number}/{self._mprn})"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.MONETARY

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return "GBP"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-gbp"

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
    """Retrieve the previously calculated state"""
    return self._state

  @property
  def should_poll(self):
    return True

  async def async_update(self):
    await super().async_update()

    if not self.enabled:
      return
    
    current = utcnow()
    result: PreviousConsumptionCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    consumption_data = result.consumption if result is not None and result.consumption is not None and len(result.consumption) > 0 else None

    is_old_data = (result is not None and (self._last_retrieved is None or result.last_retrieved >= self._last_retrieved)) and (self._next_refresh is None or current >= self._next_refresh)

    if (consumption_data is not None and len(consumption_data) >= MINIMUM_CONSUMPTION_DATA_LENGTH and is_old_data):
      period_from = consumption_data[0]["start"]
      period_to = consumption_data[-1]["end"]
      target_product_code = self._config[CONFIG_TARIFF_COMPARISON_PRODUCT_CODE]
      target_tariff_code = self._config[CONFIG_TARIFF_COMPARISON_TARIFF_CODE]

      try:
        _LOGGER.debug(f"Retrieving rates and standing charge overrides for '{self._mprn}/{self._serial_number}' ({period_from} - {period_to})...")
        [rate_data, standing_charge] = await asyncio.gather(
          self._client.async_get_gas_rates(target_product_code, target_tariff_code, period_from, period_to),
          self._client.async_get_gas_standing_charge(target_product_code, target_tariff_code, period_from, period_to)
        )

        _LOGGER.debug(f"Rates and standing charge overrides for '{self._mprn}/{self._serial_number}' ({period_from} - {period_to}) retrieved")

        consumption_and_cost = calculate_gas_consumption_and_cost(
          consumption_data,
          rate_data,
          standing_charge["value_inc_vat"] if standing_charge is not None else None,
          None,
          self._native_consumption_units,
          self._calorific_value
        )

        if (consumption_and_cost is not None):
          _LOGGER.debug(f"Calculated previous gas consumption cost override for '{self._mprn}/{self._serial_number}'...")

          self._last_reset = consumption_and_cost["last_reset"]
          self._state = consumption_and_cost["total_cost"]

          self._attributes = {
            "mprn": self._mprn,
            "serial_number": self._serial_number,
            "product_code": target_product_code,
            "tariff_code": target_tariff_code,
            "standing_charge": consumption_and_cost["standing_charge"],
            "total_without_standing_charge": consumption_and_cost["total_cost_without_standing_charge"],
            "total": consumption_and_cost["total_cost"],
            "charges": list(map(lambda charge: {
              "start": charge["start"],
              "end": charge["end"],
              "rate": charge["rate"],
              "consumption": charge["consumption_kwh"],
              "cost": charge["cost"]
            }, consumption_and_cost["charges"])),
            "calorific_value": self._calorific_value
          }
          
          self._hass.bus.async_fire(EVENT_GAS_PREVIOUS_CONSUMPTION_TARIFF_COMPARISON_RATES,
                                    dict_to_typed_dict({
                                      "mprn": self._mprn,
                                      "serial_number": self._serial_number,
                                      "product_code": target_product_code,
                                      "tariff_code": target_tariff_code,
                                      "rates": private_rates_to_public_rates(rate_data) 
                                    }))

          self._attempts_to_retrieve = 1
          self._last_retrieved = current
          self._next_refresh = calculate_next_refresh(current, self._request_attempts, REFRESH_RATE_IN_MINUTES_PREVIOUS_CONSUMPTION)
        else:
          _LOGGER.debug(f"Consumption and cost overrides not available for '{self._mprn}/{self._serial_number}' ({self._last_reset})")
      except Exception as e:
        if isinstance(e, ApiException) == False:
          raise
        
        self._request_attempts = self._request_attempts + 1
        self._next_refresh = calculate_next_refresh(
          result.last_retrieved,
          self._request_attempts,
          REFRESH_RATE_IN_MINUTES_PREVIOUS_CONSUMPTION
        )
        _LOGGER.warning(f'Failed to retrieve previous accumulative cost override data - using cached data. Next attempt at {self._next_refresh}')

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

      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeGasCostOverride state: {self._state}')