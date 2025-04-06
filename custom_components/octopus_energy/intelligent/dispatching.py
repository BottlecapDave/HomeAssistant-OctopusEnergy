import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.exceptions import ServiceValidationError

from homeassistant.util.dt import (utcnow)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from ..intelligent import (
  dispatches_to_dictionary_list
)

from ..utils import get_off_peak_times
from .base import OctopusEnergyIntelligentSensor
from ..coordinators.intelligent_dispatches import IntelligentDispatchDataUpdateCoordinator, IntelligentDispatchesCoordinatorResult
from ..utils.attributes import dict_to_typed_dict
from ..api_client.intelligent_device import IntelligentDevice
from ..coordinators import MultiCoordinatorEntity

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentDispatching(MultiCoordinatorEntity, BinarySensorEntity, OctopusEnergyIntelligentSensor, RestoreEntity):
  """Sensor for determining if an intelligent is dispatching."""

  def __init__(self, hass: HomeAssistant, coordinator: IntelligentDispatchDataUpdateCoordinator, rates_coordinator, mpan: str, device: IntelligentDevice, account_id: str, planned_dispatches_supported: bool):
    """Init sensor."""

    MultiCoordinatorEntity.__init__(self, coordinator, [rates_coordinator])
    OctopusEnergyIntelligentSensor.__init__(self, device)
  
    self._rates_coordinator = rates_coordinator
    self._mpan = mpan
    self._account_id = account_id
    self._state = None
    self._planned_dispatches_supported = planned_dispatches_supported
    self.__init_attributes__([], [], [])

    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_intelligent_dispatching"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Intelligent Dispatching ({self._account_id})"

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
    }
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine if OE is currently dispatching energy."""
    result: IntelligentDispatchesCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    rates = self._rates_coordinator.data.rates if self._rates_coordinator is not None and self._rates_coordinator.data is not None else None

    current_date = utcnow()
    planned_dispatches = result.dispatches.planned if result is not None and result.dispatches is not None and self._planned_dispatches_supported else []
    
    self.__init_attributes__(
      dispatches_to_dictionary_list(planned_dispatches) if result is not None else [],
      dispatches_to_dictionary_list(result.dispatches.completed if result is not None and result.dispatches is not None else []) if result is not None else [],
      dispatches_to_dictionary_list(result.dispatches.started if result is not None and result.dispatches is not None else []) if result is not None else [],
    )

    off_peak_times = get_off_peak_times(current_date, rates, True)
    is_dispatching = False
    
    if off_peak_times is not None and len(off_peak_times) > 0:
      time = off_peak_times.pop(0)
      if time.start <= current_date:
        self._attributes["current_start"] = time.start
        self._attributes["current_end"] = time.end
        is_dispatching = True

        if len(off_peak_times) > 0:
          self._attributes["next_start"] = off_peak_times[0].start
          self._attributes["next_end"] = off_peak_times[0].end
        else:
          self._attributes["next_start"] = None
          self._attributes["next_end"] = None
      else:
        self._attributes["current_start"] = None
        self._attributes["current_end"] = None
        self._attributes["next_start"] = time.start
        self._attributes["next_end"] = time.end
    else:
      self._attributes["current_start"] = None
      self._attributes["current_end"] = None
      self._attributes["next_start"] = None
      self._attributes["next_end"] = None

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
