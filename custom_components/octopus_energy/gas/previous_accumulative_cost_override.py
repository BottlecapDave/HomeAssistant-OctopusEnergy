import logging
from datetime import (datetime)

from homeassistant.core import HomeAssistant

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)

from . import (
  async_calculate_gas_consumption_and_cost,
  get_gas_tariff_override_key,
)

from ..api_client import (OctopusEnergyApiClient)

from .base import (OctopusEnergyGasSensor)

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)
  
class OctopusEnergyPreviousAccumulativeGasCostOverride(CoordinatorEntity, OctopusEnergyGasSensor):
  """Sensor for displaying the previous days accumulative gas cost for a different tariff."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, tariff_code, meter, point, calorific_value):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)
    
    self._hass = hass
    self._client = client
    self._tariff_code = tariff_code
    self._native_consumption_units = meter["consumption_units"]

    self._state = None
    self._last_reset = None
    self._calorific_value = calorific_value

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_accumulative_cost_override"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Gas {self._serial_number} {self._mprn} Previous Accumulative Cost Override"
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.MONETARY

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def unit_of_measurement(self):
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
  def state(self):
    """Retrieve the previously calculated state"""
    return self._state

  @property
  def should_poll(self):
    return True

  async def async_update(self):
    consumption_data = self.coordinator.data["consumption"] if self.coordinator.data is not None and "consumption" in self.coordinator.data else None

    tariff_override_key = get_gas_tariff_override_key(self._serial_number, self._mprn)
    is_old_data = self._last_reset is None or self._last_reset < consumption_data[-1]["interval_end"]
    is_tariff_present = tariff_override_key in self._hass.data[DOMAIN]
    has_tariff_changed = is_tariff_present and self._hass.data[DOMAIN][tariff_override_key] != self._tariff_code

    if (consumption_data is not None and len(consumption_data) > 0 and is_tariff_present and (is_old_data or has_tariff_changed)):
      _LOGGER.debug(f"Calculating previous gas consumption cost override for '{self._mprn}/{self._serial_number}'...")

      tariff_override = self._hass.data[DOMAIN][tariff_override_key]
      period_from = consumption_data[0]["interval_start"]
      period_to = consumption_data[-1]["interval_end"]
      rate_data = await self._client.async_get_gas_rates(tariff_override, period_from, period_to)
      standing_charge = await self._client.async_get_gas_standing_charge(tariff_override, period_from, period_to)

      consumption_and_cost = await async_calculate_gas_consumption_and_cost(
        consumption_data,
        rate_data,
        standing_charge["value_inc_vat"] if standing_charge is not None else None,
        None if has_tariff_changed else self._last_reset,
        tariff_override,
        self._native_consumption_units,
        self._calorific_value
      )

      self._tariff_code = tariff_override

      if (consumption_and_cost is not None):
        _LOGGER.debug(f"Calculated previous gas consumption cost override for '{self._mprn}/{self._serial_number}'...")

        self._last_reset = consumption_and_cost["last_reset"]
        self._state = consumption_and_cost["total_cost"]

        self._attributes = {
          "mprn": self._mprn,
          "serial_number": self._serial_number,
          "tariff_code": self._tariff_code,
          "standing_charge": f'{consumption_and_cost["standing_charge"]}p',
          "total_without_standing_charge": f'£{consumption_and_cost["total_cost_without_standing_charge"]}',
          "total": f'£{consumption_and_cost["total_cost"]}',
          "last_calculated_timestamp": consumption_and_cost["last_calculated_timestamp"],
          "charges": list(map(lambda charge: {
            "from": charge["from"],
            "to": charge["to"],
            "rate": f'{charge["rate"]}p',
            "consumption": f'{charge["consumption_kwh"]} kWh',
            "cost": charge["cost"]
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

      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeGasCostOverride state: {self._state}')