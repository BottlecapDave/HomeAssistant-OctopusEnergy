import logging
from datetime import timedelta
from custom_components.octopus_energy.const import REFRESH_RATE_IN_MINUTES_OCTOPLUS_WHEEL_OF_FORTUNE
from custom_components.octopus_energy.utils.requests import calculate_next_refresh

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (utcnow)

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorStateClass
)
from ..api_client import ApiException, OctopusEnergyApiClient, RequestException
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyOctoplusPoints(RestoreSensor):
  """Sensor for determining octoplus points"""

  def __init__(self, hass: HomeAssistant, client: OctopusEnergyApiClient, account_id: str):
    """Init sensor."""
  
    self._client = client
    self._account_id = account_id
    self._state = None
    self._attributes = {
      "last_evaluated": None
    }
    self._last_evaluated = None
    self._next_refresh = None
    self._request_attempts = 1

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_octoplus_points"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy {self._account_id} Octoplus Points"

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
  
  async def async_update(self):
    now = utcnow()
    if self._next_refresh is None or now >= self._next_refresh:
      try:
        self._state = await self._client.async_get_octoplus_points()
        self._last_evaluated = now
        self._request_attempts = 1
      except  Exception as e:
        if isinstance(e, ApiException) == False:
          _LOGGER.error(e)
          raise
        _LOGGER.warning(f"Failed to retrieve octopoints")
        self._request_attempts = self._request_attempts + 1

      self._next_refresh = calculate_next_refresh(self._last_evaluated, self._request_attempts, REFRESH_RATE_IN_MINUTES_OCTOPLUS_WHEEL_OF_FORTUNE)
    
    self._attributes["data_last_retrieved"] = self._last_evaluated
    self._attributes["last_evaluated"] = self._last_evaluated

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None and self._state is None:
      self._state = None if state.state == "unknown" else state.state
      self._attributes = dict_to_typed_dict(state.attributes)
    
      _LOGGER.debug(f'Restored OctopusEnergyOctoplusPoints state: {self._state}')