import logging
from datetime import datetime
from custom_components.octopus_energy.coordinators.current_consumption import CurrentConsumptionCoordinatorResult

from homeassistant.core import HomeAssistant, callback

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass
)
from . import (
  calculate_gas_consumption_and_cost,
)

from .base import (OctopusEnergyGasSensor)
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)
  
class OctopusEnergyCurrentAccumulativeGasCost(CoordinatorEntity, OctopusEnergyGasSensor, RestoreSensor):
  """Sensor for displaying the current days accumulative gas cost."""

  def __init__(self, hass: HomeAssistant, coordinator, rates_coordinator, standing_charge_coordinator, tariff_code, meter, point, calorific_value):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)
    
    self._hass = hass
    self._tariff_code = tariff_code

    self._state = None
    self._last_reset = None
    self._calorific_value = calorific_value
    self._rates_coordinator = rates_coordinator
    self._standing_charge_coordinator = standing_charge_coordinator

  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return self._is_smart_meter

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_current_accumulative_cost"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Gas {self._serial_number} {self._mprn} Current Accumulative Cost"

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
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the currently calculated state"""
    consumption_result: CurrentConsumptionCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    consumption_data = consumption_result.data if consumption_result is not None else None
    rate_data = self._rates_coordinator.data.rates if self._rates_coordinator is not None and self._rates_coordinator.data is not None else None
    standing_charge = self._standing_charge_coordinator.data.standing_charge["value_inc_vat"] if self._standing_charge_coordinator is not None and self._standing_charge_coordinator.data is not None else None
    
    consumption_and_cost = calculate_gas_consumption_and_cost(
      consumption_data,
      rate_data,
      standing_charge,
      None, # We want to always recalculate
      self._tariff_code,
      "kwh",
      self._calorific_value
    )

    if (consumption_and_cost is not None):
      _LOGGER.debug(f"Calculated current gas consumption cost for '{self._mprn}/{self._serial_number}'...")
      self._last_reset = consumption_and_cost["last_reset"]
      self._state = consumption_and_cost["total_cost"]

      self._attributes = {
        "mprn": self._mprn,
        "serial_number": self._serial_number,
        "tariff_code": self._tariff_code,
        "standing_charge": consumption_and_cost["standing_charge"],
        "total_without_standing_charge": consumption_and_cost["total_cost_without_standing_charge"],
        "total": consumption_and_cost["total_cost"],
        "last_evaluated": consumption_and_cost["last_evaluated"],
        "data_last_retrieved": consumption_result.last_retrieved if consumption_result is not None else None,
        "charges": list(map(lambda charge: {
          "start": charge["start"],
          "end": charge["end"],
          "rate": charge["rate"],
          "consumption": charge["consumption_kwh"],
          "cost": charge["cost"],
        }, consumption_and_cost["charges"])),
        "calorific_value": self._calorific_value
      }

    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state == "unknown" else state.state
      self._attributes = dict_to_typed_dict(state.attributes)

      _LOGGER.debug(f'Restored OctopusEnergyCurrentAccumulativeGasCost state: {self._state}')