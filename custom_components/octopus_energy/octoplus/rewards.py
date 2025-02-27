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

from ..const import DOMAIN, REFRESH_RATE_IN_MINUTES_OCTOPLUS_REWARDS, DATA_REWARDS, EVENT_NEW_REWARD
from ..utils.requests import calculate_next_refresh
from ..api_client import ApiException, OctopusEnergyApiClient, RequestException
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyOctoplusRewards(RestoreSensor):
  """Sensor for determining octoplus rewards"""

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
    self._hass = hass

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_octoplus_rewards"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Octoplus Rewards ({self._account_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:gift"

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
      await self.async_refresh_rewards()

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

      _LOGGER.debug(f'Restored OctopusEnergyOctoplusRewards state: {self._state}')

  @callback
  async def async_claim_octoplus_reward(self, reward_slug: str):
    """Claim octoplus reward"""
    result = await self._client.async_claim_octoplus_reward(self._account_id, reward_slug)
    if result.reward_id is not None:
      await self.async_refresh_rewards()

  async def async_refresh_rewards(self):
    now = utcnow()
    try:
      rewards = await self._client.async_get_octoplus_rewards(account_id=self._account_id)

      available_rewards = [entry for entry in rewards if entry["status"] == "PENDING"]

      self._state = len(available_rewards)
      self._attributes["claimedRewards"] = len([entry for entry in rewards if entry["status"] == "ISSUED"])

      previous_rewards = self._hass.data[DOMAIN][self._account_id][DATA_REWARDS] if DATA_REWARDS in self._hass.data[DOMAIN][self._account_id] else []
      previous_reward_ids = { reward["id"] for reward in previous_rewards }

      new_available_rewards = [reward for reward in available_rewards if reward["id"] not in previous_reward_ids]

      if len(new_available_rewards):
        self._hass.data[DOMAIN][self._account_id][DATA_REWARDS] = available_rewards

        for reward in new_available_rewards:
          fire_event(EVENT_NEW_REWARD, {
            "account_id": self._account_id,
            "reward_slug": reward["offer"]["slug"]
          })

      self._last_evaluated = now
      self._request_attempts = 1
    except  Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      _LOGGER.warning(f"Failed to retrieve octoplus rewards")
      self._request_attempts = self._request_attempts + 1

    self._next_refresh = calculate_next_refresh(self._last_evaluated, self._request_attempts, REFRESH_RATE_IN_MINUTES_OCTOPLUS_REWARDS)
