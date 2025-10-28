import logging

from homeassistant.core import HomeAssistant, callback

from homeassistant.components.event import (
    EventEntity,
    EventExtraStoredData,
)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import (OctopusEnergyFanClubSensor)
from ..utils.attributes import dict_to_typed_dict
from ..const import EVENT_FAN_CLUB_DISCOUNTS
from . import get_fan_club_number

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyFanClubDiscounts(OctopusEnergyFanClubSensor, EventEntity, RestoreEntity):
  """Sensor for displaying the current day's rates."""

  def __init__(self, hass: HomeAssistant, account_id: str, discount_source: str):
    """Init sensor."""
    # Pass coordinator to base class

    self._hass = hass
    self._state = None
    self._last_updated = None
    self._account_id = account_id
    self._discount_source = discount_source

    self._attr_event_types = [EVENT_FAN_CLUB_DISCOUNTS]
    OctopusEnergyFanClubSensor.__init__(self, hass, "event")

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_fan_club_{self._account_id}_{get_fan_club_number(self._discount_source)}_discounts"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Discounts Fan Club ({get_fan_club_number(self._discount_source)}/{self._account_id})"

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
    if (event.data is not None and "account_id" in event.data and event.data["account_id"] == self._account_id and "source" in event.data and event.data["source"] == self._discount_source):
      self._trigger_event(event.event_type, event.data)
      self.async_write_ha_state()