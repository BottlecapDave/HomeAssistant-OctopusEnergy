import logging

from homeassistant.core import HomeAssistant, callback

from homeassistant.components.event import (
    EventEntity,
    EventExtraStoredData,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import generate_entity_id

from ..const import DATA_SAVING_SESSIONS_FORCE_UPDATE, DOMAIN, EVENT_ALL_SAVING_SESSIONS

from ..api_client import OctopusEnergyApiClient
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyOctoplusSavingSessionEvents(EventEntity, RestoreEntity):
  """Sensor for displaying the upcoming saving sessions."""

  def __init__(self, hass: HomeAssistant, client: OctopusEnergyApiClient, account_id: str):
    """Init sensor."""

    self._client = client
    self._account_id = account_id
    self._hass = hass
    self._state = None
    self._last_updated = None

    self._attr_event_types = [EVENT_ALL_SAVING_SESSIONS]
    self.entity_id = generate_entity_id("event.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_octoplus_saving_session_events"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octoplus Saving Session Events ({self._account_id})"

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    
    self._hass.bus.async_listen(self._attr_event_types[0], self._async_handle_event)

  async def async_get_last_event_data(self):
    data = await super().async_get_last_event_data()
    return EventExtraStoredData.from_dict({
      "last_event_type": data.last_event_type,
      "last_event_attributes": dict_to_typed_dict(data.last_event_attributes),
    })

  @callback
  def _async_handle_event(self, event) -> None:
    if (event.data is not None and "account_id" in event.data and event.data["account_id"] == self._account_id):
      self._trigger_event(event.event_type, event.data)
      self.async_write_ha_state()

  @callback
  async def async_join_saving_session_event(self, event_code: str):
    """Join saving session event"""

    result = await self._client.async_join_octoplus_saving_session(self._account_id, event_code)
    if (result.is_successful == False):
      raise Exception(result.errors[0])
    else:
      self._hass.data[DOMAIN][self._account_id][DATA_SAVING_SESSIONS_FORCE_UPDATE] = True