import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (now, utcnow)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from ..intelligent import (
  dispatches_to_dictionary_list,
  is_in_planned_dispatch
)

from ..utils import is_off_peak

from .base import OctopusEnergyIntelligentSensor
from ..coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentDispatching(CoordinatorEntity, BinarySensorEntity, OctopusEnergyIntelligentSensor, RestoreEntity):
  """Sensor for determining if an intelligent is dispatching."""

  def __init__(self, hass: HomeAssistant, coordinator, rates_coordinator, mpan: str, device, account_id: str):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)
  
    self._rates_coordinator = rates_coordinator
    self._mpan = mpan
    self._account_id = account_id
    self._state = None
    self._attributes = {
      "planned_dispatches": [],
      "completed_dispatches": [],
      "last_evaluated": None,
      "vehicle_battery_size_in_kwh": device["vehicleBatterySizeInKwh"],
      "charge_point_power_in_kw": device["chargePointPowerInKw"]
    }

    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_intelligent_dispatching"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy {self._account_id} Intelligent Dispatching"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:power-plug-battery"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    """Determine if OE is currently dispatching energy."""
    result: IntelligentDispatchesCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    rates = self._rates_coordinator.data.rates if self._rates_coordinator is not None and self._rates_coordinator.data is not None else None

    current_date = utcnow()
    self._state = is_in_planned_dispatch(current_date, result.dispatches.planned if result.dispatches is not None else []) or is_off_peak(current_date, rates)

    self._attributes = {
      "planned_dispatches": dispatches_to_dictionary_list(result.dispatches.planned if result.dispatches is not None else []) if result is not None else [],
      "completed_dispatches": dispatches_to_dictionary_list(result.dispatches.completed if result.dispatches is not None else []) if result is not None else [],
      "data_last_retrieved": result.last_retrieved if result is not None else None,
      "last_evaluated": current_date 
    }
    
    return self._state

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = None if state.state == "unknown" else state.state
      self._attributes = dict_to_typed_dict(state.attributes)
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored OctopusEnergyIntelligentDispatching state: {self._state}')
