import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorStateClass,
)

from .base import OctopusEnergyIntelligentSensor
from ..coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult
from ..utils.attributes import dict_to_typed_dict
from ..api_client.intelligent_device import IntelligentDevice
from ..intelligent import get_dispatch_hours_for_intelligent_day

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentChargeCapHours(CoordinatorEntity, OctopusEnergyIntelligentSensor, RestoreSensor):
  """Sensor for determining the current intelligent state."""

  def __init__(self, hass: HomeAssistant, coordinator, device: IntelligentDevice, account_id: str):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)
  
    self._account_id = account_id
    self._state = None
    self._attributes = {}

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._device.id}_intelligent_charge_cap_hours"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Charge Cap Hours ({self._device.id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:power-plug-battery"

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL_INCREASING

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    current = now()
    result: IntelligentDispatchesCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if (result is not None and result.dispatches is not None):
      _LOGGER.debug(f"Updating OctopusEnergyIntelligentChargeCapHours for '{self._device.id}'")

      applicable_dispatches = []
      applicable_dispatches.extend(result.dispatches.started)
      applicable_dispatches.extend(result.dispatches.completed)

      self._state = get_dispatch_hours_for_intelligent_day(current, applicable_dispatches, True)
    else:
      self._state = None

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
      self._attributes = dict_to_typed_dict(state.attributes, [])
      _LOGGER.debug(f'Restored OctopusEnergyIntelligentCurrentState state: {self._state}')
