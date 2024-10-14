import logging
from datetime import time
import time as time_time

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.time import TimeEntity
from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import OctopusEnergyIntelligentSensor
from ..api_client import OctopusEnergyApiClient
from ..coordinators.intelligent_settings import IntelligentCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentTargetTime(CoordinatorEntity, TimeEntity, OctopusEnergyIntelligentSensor, RestoreEntity):
  """Sensor for setting the target time to charge the car to the desired percentage."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, device, account_id: str):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)

    self._state = time()
    self._last_updated = None
    self._client = client
    self._account_id = account_id
    self._attributes = {}
    self.entity_id = generate_entity_id("time.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_intelligent_target_time"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Intelligent Target Time ({self._account_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:battery-clock"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self) -> time:
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """The time that the car should be ready by."""
    settings_result: IntelligentCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if settings_result is None or (self._last_updated is not None and self._last_updated > settings_result.last_retrieved):
      return self._state

    if settings_result.settings is not None:
      self._state = settings_result.settings.ready_time_weekday

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_set_value(self, value: time) -> None:
    """Set new value."""
    await self._client.async_update_intelligent_car_target_time(
      self._account_id,
      self._device.id,
      value,
    )
    self._state = value
    self._last_updated = utcnow()
    self.async_write_ha_state()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      time_state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else time_time.strptime(state.state, "%H:%M:%S")
      if time_state is not None:
        self._state = time(hour=time_state.tm_hour, minute=time_state.tm_min, second=min(time_state.tm_sec, 59))  # account for leap seconds
      
      self._attributes = dict_to_typed_dict(state.attributes)
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored OctopusEnergyIntelligentTargetTime state: {self._state}')