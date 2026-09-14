import logging

from homeassistant.core import HomeAssistant, ServiceValidationError, callback

from ..api_client import OctopusEnergyApiClient
from ..const import DATA_POWER_UP_DOWN_FORCE_UPDATE, DOMAIN, EVENT_ALL_POWER_UP_SESSIONS
from .free_electricity_sessions_events import OctopusEnergyOctoplusFreeElectricitySessionEvents

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyOctoplusPowerUpEvents(OctopusEnergyOctoplusFreeElectricitySessionEvents):
  """Sensor for displaying the upcoming power up events."""

  _attr_translation_key = "power_up_sessions"

  def __init__(self, hass: HomeAssistant, client: OctopusEnergyApiClient, account_id: str):
    """Init sensor."""
    super().__init__(hass, account_id)

    self._client = client
    self._attr_event_types = [EVENT_ALL_POWER_UP_SESSIONS]

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_octoplus_power_up_events"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Octoplus Power Up Events ({self._account_id})"

  @callback
  async def async_join_weekend_happy_hour_event(self, event_code: str):
    """Join weekend happy hour session event"""

    result = await self._client.async_redeem_weekend_happy_hour(self._account_id, event_code)
    if (result.is_successful == False):
      raise ServiceValidationError(result.errors[0])

    self._hass.data[DOMAIN][self._account_id][DATA_POWER_UP_DOWN_FORCE_UPDATE] = True
    return { "success": True }
