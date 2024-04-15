import logging
from datetime import datetime

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass,
)

from homeassistant.util.dt import (now)

from . import (
  calculate_electricity_consumption_and_cost,
)

from ..coordinators import MultiCoordinatorEntity
from ..coordinators.current_consumption import CurrentConsumptionCoordinatorResult
from .base import (OctopusEnergyElectricitySensor)
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCurrentAccumulativeElectricityCostPeak(MultiCoordinatorEntity, OctopusEnergyElectricitySensor, RestoreSensor):
  """Sensor for displaying the current days accumulative electricity cost during peak hours."""

  def __init__(self, hass: HomeAssistant, coordinator, rates_coordinator, standing_charge_coordinator, meter, point):
    """Init sensor."""
    MultiCoordinatorEntity.__init__(self, coordinator, [rates_coordinator, standing_charge_coordinator])
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._state = None
    self._last_reset = None
    
    self._rates_coordinator = rates_coordinator
    self._standing_charge_coordinator = standing_charge_coordinator

  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_current_accumulative_cost_peak"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Current Accumulative Cost (Peak)"

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
    current = now()
    consumption_result: CurrentConsumptionCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    consumption_data = consumption_result.data if consumption_result is not None else None
    rate_data = self._rates_coordinator.data.rates if self._rates_coordinator is not None and self._rates_coordinator.data is not None else None
    standing_charge = self._standing_charge_coordinator.data.standing_charge["value_inc_vat"] if self._standing_charge_coordinator is not None and self._standing_charge_coordinator.data is not None else None
    
    consumption_and_cost = calculate_electricity_consumption_and_cost(
      current,
      consumption_data,
      rate_data,
      standing_charge,
      None # We want to always recalculate
    )

    if (consumption_and_cost is not None):
      _LOGGER.debug(f"Calculated current electricity consumption cost peak for '{self._mpan}/{self._serial_number}'...")

      self._last_reset = consumption_and_cost["last_reset"]
      self._state = consumption_and_cost["total_cost_peak"] if "total_cost_peak" in consumption_and_cost else 0

      self._attributes["last_evaluated"] = consumption_and_cost["last_evaluated"]
      self._attributes["data_last_retrieved"] = consumption_result.last_retrieved if consumption_result is not None else None

    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else state.state
      
      # For some reason this sensor is having issues with HA recognising last_reset updating unless we update it like the following :shrug:
      self._attributes = dict_to_typed_dict(state.attributes, ["last_reset"])
      self._last_reset = datetime.fromisoformat(state.attributes["last_reset"]) if "last_reset" in state.attributes else None
    
      _LOGGER.debug(f'Restored OctopusEnergyCurrentAccumulativeElectricityCostPeak state: {self._state}')