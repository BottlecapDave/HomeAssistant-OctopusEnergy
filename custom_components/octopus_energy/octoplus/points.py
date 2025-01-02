import logging
from datetime import timedelta
import math

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (utcnow)

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorStateClass
)

from ..const import DOMAIN, REFRESH_RATE_IN_MINUTES_OCTOPLUS_POINTS
from ..utils.requests import calculate_next_refresh
from ..api_client import ApiException, OctopusEnergyApiClient, RequestException
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyOctoplusPoints(RestoreSensor):
  """Sensor for determining octoplus points"""
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, client: OctopusEnergyApiClient, account_id: str):
    """Init sensor."""
  
    self._client = client
    self._account_id = account_id
    self._state = None
    self._last_evaluated = None
    self._next_refresh = None
    self._request_attempts = 1
    self._attributes = {}

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_octoplus_points"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octoplus Points ({self._account_id})"

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
      await self.async_refresh_points()
    
    self._attributes = dict_to_typed_dict(self._attributes)

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)
    
      _LOGGER.debug(f'Restored OctopusEnergyOctoplusPoints state: {self._state}')

  @callback
  async def async_redeem_points_into_account_credit(self, points_to_redeem: int):
    """Redeem points"""
    redeemable_points = self._attributes["redeemable_points"] if "redeemable_points" in self._attributes else 0
    if redeemable_points < 1:
      raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="octoplus_points_no_points",
      )
    elif points_to_redeem > redeemable_points:
      raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="octoplus_points_maximum_points",
        translation_placeholders={ 
          "redeemable_points": redeemable_points, 
        },
      )

    result = await self._client.async_redeem_octoplus_points_into_account_credit(self._account_id, points_to_redeem)
    if result.is_successful:
      await self.async_refresh_points()

  async def async_refresh_points(self):
    now = utcnow()
    try:
      self._state = await self._client.async_get_octoplus_points()
      self._attributes["redeemable_points"] = math.floor(self._state / 8) * 8 if self._state is not None else 0
      self._last_evaluated = now
      self._request_attempts = 1
    except  Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      _LOGGER.warning(f"Failed to retrieve octopoints")
      self._request_attempts = self._request_attempts + 1

    self._next_refresh = calculate_next_refresh(self._last_evaluated, self._request_attempts, REFRESH_RATE_IN_MINUTES_OCTOPLUS_POINTS)