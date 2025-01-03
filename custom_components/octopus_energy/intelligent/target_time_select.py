import logging
from datetime import datetime, time, timedelta
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
from homeassistant.components.select import SelectEntity
from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import OctopusEnergyIntelligentSensor
from ..api_client import OctopusEnergyApiClient
from ..coordinators.intelligent_settings import IntelligentCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentTargetTimeSelect(CoordinatorEntity, SelectEntity, OctopusEnergyIntelligentSensor, RestoreEntity):
  """Sensor for setting the target time to charge the car to the desired percentage."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, device, account_id: str, is_mocked: bool):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)

    self._state = None
    self._last_updated = None
    self._client = client
    self._account_id = account_id
    self._attributes = {}
    self._is_mocked = is_mocked
    self.entity_id = generate_entity_id("select.{}", self.unique_id, hass=hass)

    self._options = []
    current_time = datetime(2025, 1, 1, 4, 0)
    final_time = datetime(2025, 1, 1, 11, 30)
    while current_time < final_time:
      self._options.append(f"{current_time.hour:02}:{current_time.minute:02}")
      current_time = current_time + timedelta(minutes=30)

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
  def options(self) -> list[str]:
      """Return the available tariffs."""
      return self._options

  @property
  def current_option(self) -> str:
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """The time that the car should be ready by."""
    settings_result: IntelligentCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if settings_result is None or (self._last_updated is not None and self._last_updated > settings_result.last_retrieved):
      return

    if settings_result.settings is not None:
      self._state = f"{settings_result.settings.ready_time_weekday.hour:02}:{settings_result.settings.ready_time_weekday.minute:02}"

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_select_option(self, option: str) -> None:
    """Change the selected option."""
    parts = option.split(":")
    value = time(int(parts[0]), int(parts[1]))
    try:
      await self._client.async_update_intelligent_car_target_time(
        self._account_id,
        self._device.id,
        value,
      )
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_select_option error due to mocking mode: {e}')
      else:
        raise

    self._state = option
    self._last_updated = utcnow()
    self.async_write_ha_state()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else state.state
      self._attributes = dict_to_typed_dict(state.attributes)
    
    if (self._state is None):
      self._state = None
    
    _LOGGER.debug(f'Restored OctopusEnergyIntelligentTargetTime state: {self._state}')