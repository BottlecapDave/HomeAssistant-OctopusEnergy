import logging
from datetime import datetime

from homeassistant.core import HomeAssistant

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)
from . import (
  calculate_electricity_consumption_and_cost,
)

from .base import (OctopusEnergyElectricitySensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCurrentAccumulativeElectricityCost(CoordinatorEntity, OctopusEnergyElectricitySensor):
  """Sensor for displaying the current days accumulative electricity cost."""

  def __init__(self, hass: HomeAssistant, coordinator, rates_coordinator, standing_charge_coordinator, tariff_code, meter, point):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._hass = hass
    self._tariff_code = tariff_code

    self._state = None
    self._last_reset = None
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
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_current_accumulative_cost"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Current Accumulative Cost"

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
    """Retrieve the currently calculated state"""
    consumption_data = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    rate_data = self._rates_coordinator.data[self._mpan] if self._rates_coordinator is not None and self._rates_coordinator.data is not None and self._mpan in self._rates_coordinator.data else None
    standing_charge = self._standing_charge_coordinator.data[self._mpan]["value_inc_vat"] if self._standing_charge_coordinator is not None and self._standing_charge_coordinator.data is not None and self._mpan in self._standing_charge_coordinator.data and "value_inc_vat" in self._standing_charge_coordinator.data[self._mpan] else None

    consumption_and_cost = calculate_electricity_consumption_and_cost(
      consumption_data,
      rate_data,
      standing_charge,
      None, # We want to always recalculate
      self._tariff_code
    )

    if (consumption_and_cost is not None):
      _LOGGER.debug(f"Calculated current electricity consumption cost for '{self._mpan}/{self._serial_number}'...")
      self._last_reset = consumption_and_cost["last_reset"]
      self._state = consumption_and_cost["total_cost"]

      self._attributes = {
        "mpan": self._mpan,
        "serial_number": self._serial_number,
        "is_export": self._is_export,
        "is_smart_meter": self._is_smart_meter,
        "tariff_code": self._tariff_code,
        "standing_charge": f'{consumption_and_cost["standing_charge"]}p',
        "total_without_standing_charge": f'£{consumption_and_cost["total_cost_without_standing_charge"]}',
        "total": f'£{consumption_and_cost["total_cost"]}',
        "last_calculated_timestamp": consumption_and_cost["last_calculated_timestamp"],
        "charges": list(map(lambda charge: {
          "from": charge["from"],
          "to": charge["to"],
          "rate": f'{charge["rate"]}p',
          "consumption": f'{charge["consumption"]} kWh',
          "consumption_raw": charge["consumption"],
          "cost": f'£{charge["cost"]}',
          "cost_raw": charge["cost"],
        }, consumption_and_cost["charges"]))
      }

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

        if x == "last_reset":
          self._last_reset = datetime.strptime(state.attributes[x], "%Y-%m-%dT%H:%M:%S%z")
    
      _LOGGER.debug(f'Restored OctopusEnergyCurrentAccumulativeElectricityCost state: {self._state}')