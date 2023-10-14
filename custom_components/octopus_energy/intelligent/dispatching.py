import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (now)
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

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentDispatching(CoordinatorEntity, BinarySensorEntity, OctopusEnergyIntelligentSensor, RestoreEntity):
  """Sensor for determining if an intelligent is dispatching."""

  def __init__(self, hass: HomeAssistant, coordinator, rates_coordinator, mpan, device):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)
  
    self._rates_coordinator = rates_coordinator
    self._mpan = mpan
    self._state = None
    self._attributes = {
      "planned_dispatches": [],
      "completed_dispatches": [],
      "last_updated_timestamp": None,
      "vehicle_battery_size_in_kwh": device["vehicleBatterySizeInKwh"],
      "charge_point_power_in_kw": device["chargePointPowerInKw"]
    }

    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_intelligent_dispatching"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Intelligent Dispatching"

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
    if (result is not None):
      self._attributes["planned_dispatches"] = dispatches_to_dictionary_list(result.dispatches.planned)
      self._attributes["completed_dispatches"] = dispatches_to_dictionary_list(result.dispatches.completed)
      self._attributes["last_updated_timestamp"] = result.last_retrieved
    else:
      self._attributes["planned_dispatches"] = []
      self._attributes["completed_dispatches"] = []

    current_date = now()
    self._state = is_in_planned_dispatch(current_date, result.dispatches.planned) or is_off_peak(current_date, rates)
    
    return self._state

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = state.state
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored OctopusEnergyIntelligentDispatching state: {self._state}')
