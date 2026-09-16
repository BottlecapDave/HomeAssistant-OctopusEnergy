import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (utcnow)

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorStateClass
)

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)

from ..coordinators.power_up_down_sessions import PowerUpDownSessionsCoordinatorResult
from ..const import REFRESH_RATE_IN_MINUTES_OCTOPLUS_POINTS
from ..utils.requests import calculate_next_refresh
from ..api_client import ApiException
from ..utils.attributes import dict_to_typed_dict
from .base import OctopusEnergyOctoplusSensor

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyOctoplusWeekendHappyHours(OctopusEnergyOctoplusSensor, CoordinatorEntity, RestoreSensor):
  """Sensor for determining weekend power hours"""
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str):
    """Init sensor."""
    OctopusEnergyOctoplusSensor.__init__(self, account_id)
    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_id = account_id
    self._state = None
    self._attributes = {}

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_octoplus_weekend_happy_hours"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octoplus Weekend Happy Hours ({self._account_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:trophy"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def state(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    result: PowerUpDownSessionsCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    self._state = int(result.weekend_happy_hours / 2) if result is not None else None

    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)
    
      _LOGGER.debug(f'Restored OctopusEnergyOctoplusWeekendHappyHours state: {self._state}')