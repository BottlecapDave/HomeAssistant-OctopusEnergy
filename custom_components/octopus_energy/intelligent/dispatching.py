from datetime import datetime
import logging

from custom_components.octopus_energy.const import DOMAIN
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.exceptions import ServiceValidationError

from homeassistant.util.dt import (utcnow, as_local)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from ..intelligent import (
  dispatches_to_dictionary_list,
  get_applicable_dispatch_periods,
  get_applicable_intelligent_dispatch_history,
  get_current_and_next_dispatching_periods,
  simple_dispatches_to_dictionary_list
)

from .base import OctopusEnergyIntelligentSensor
from ..coordinators.intelligent_dispatches import IntelligentDispatchDataUpdateCoordinator, IntelligentDispatchesCoordinatorResult
from ..utils.attributes import dict_to_typed_dict
from ..api_client.intelligent_device import IntelligentDevice
from ..coordinators import MultiCoordinatorEntity

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentDispatching(MultiCoordinatorEntity, BinarySensorEntity, OctopusEnergyIntelligentSensor, RestoreEntity):
  """Sensor for determining if an intelligent is dispatching."""

  def __init__(self,
               hass: HomeAssistant,
               coordinator: IntelligentDispatchDataUpdateCoordinator,
               device: IntelligentDevice,
               account_id: str,
               intelligent_rate_mode: str,
               manually_refresh_dispatches: bool):
    """Init sensor."""

    MultiCoordinatorEntity.__init__(self, coordinator, [])
    OctopusEnergyIntelligentSensor.__init__(self, device)
  
    self._account_id = account_id
    self._state = None
    self._intelligent_rate_mode = intelligent_rate_mode
    self._manually_refresh_dispatches = manually_refresh_dispatches
    self.__init_attributes__([], [], [])

    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._device.id}_intelligent_dispatching"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Intelligent Dispatching ({self._device.id})"

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
    return self._state
  
  def __init_attributes__(self, planned_dispatches, completed_dispatches, started_dispatches):
    self._attributes = {
      "planned_dispatches": planned_dispatches,
      "completed_dispatches": completed_dispatches,
      "started_dispatches": started_dispatches,
      "provider": self._device.provider,
      "vehicle_battery_size_in_kwh": self._device.vehicleBatterySizeInKwh,
      "charge_point_power_in_kw": self._device.chargePointPowerInKw,
      "current_start": None,
      "current_end": None,
      "next_start": None,
      "next_end": None,
      "manually_refresh_dispatches": self._manually_refresh_dispatches
    }
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine if OE is currently dispatching energy."""
    result: IntelligentDispatchesCoordinatorResult = self.coordinator.data if self.coordinator is not None else None

    current_date = utcnow()
    
    started_dispatches = result.dispatches.started if result is not None and result.dispatches is not None else []
    self.__init_attributes__(
      dispatches_to_dictionary_list(result.dispatches.planned, ignore_none=True) if result is not None else [],
      dispatches_to_dictionary_list(result.dispatches.completed if result is not None and result.dispatches is not None else [], ignore_none=False) if result is not None else [],
      simple_dispatches_to_dictionary_list(started_dispatches) if result is not None else [],
    )

    applicable_dispatches = get_applicable_dispatch_periods(result.dispatches.planned if result is not None and result.dispatches is not None else [],
                                                            result.dispatches.started if result is not None and result.dispatches is not None else [],
                                                            self._intelligent_rate_mode)

    (current_dispatch, next_dispatch) = get_current_and_next_dispatching_periods(current_date, applicable_dispatches)

    is_dispatching = False
    if current_dispatch is not None:
      self._attributes["current_start"] = current_dispatch.start
      self._attributes["current_end"] = current_dispatch.end
      is_dispatching = True
    else:
      self._attributes["current_start"] = None
      self._attributes["current_end"] = None

    if next_dispatch is not None:
      self._attributes["next_start"] = next_dispatch.start
      self._attributes["next_end"] = next_dispatch.end
    else:
      self._attributes["next_start"] = None
      self._attributes["next_end"] = None

    if self._state != is_dispatching:
      _LOGGER.debug(f"OctopusEnergyIntelligentDispatching state changed from {self._state} to {is_dispatching}; dispatches: {result.dispatches.to_dict() if result.dispatches is not None else None}; started_dispatches: {list(map(lambda x: x.to_dict(), started_dispatches)) if started_dispatches is not None else []}")
    
    self._state = is_dispatching

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or state.state is None else state.state.lower() == 'on'
      self._attributes = dict_to_typed_dict(state.attributes)
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored OctopusEnergyIntelligentDispatching state: {self._state}')

  @callback
  async def async_refresh_dispatches(self):
    """Refresh dispatches"""
    result: IntelligentDispatchesCoordinatorResult = await self.coordinator.refresh_dispatches()
    if result is not None and result.last_error is not None:
      raise ServiceValidationError(result.last_error)
    
  @callback
  async def async_get_point_in_time_intelligent_dispatch_history(self, point_in_time: datetime):
    """Refresh dispatches"""
    local_point_in_time = as_local(point_in_time)
    result: IntelligentDispatchesCoordinatorResult = await self.coordinator.refresh_dispatches()
    applicable_dispatches = get_applicable_intelligent_dispatch_history(result.history if result is not None else None, local_point_in_time)
    if applicable_dispatches is not None:
      return applicable_dispatches.to_dict()
    
    earliest_timestamp = (as_local(result.history.history[0].timestamp).isoformat()
                          if result is not None and
                          result.history is not None and
                          result.history.history is not None and
                          len(result.history.history) > 0 
                          else None)
    
    if earliest_timestamp is not None:
      raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="point_in_time_intelligent_dispatch_history_data_out_of_bounds",
        translation_placeholders={ 
          "earliest_timestamp": earliest_timestamp,
        },
      )
    
    raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="point_in_time_intelligent_dispatch_history_data_unavailable",
      )
