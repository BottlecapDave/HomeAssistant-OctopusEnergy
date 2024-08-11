import logging

from homeassistant.core import HomeAssistant

from homeassistant.components.text import TextEntity

from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.helpers.entity import generate_entity_id

from ..api_client_home_pro import OctopusEnergyHomeProApiClient

from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyHomeProScreenText(TextEntity, RestoreEntity):
  """Sensor for determining the text on the home pro"""

  def __init__(self, hass: HomeAssistant, account_id: str, client: OctopusEnergyHomeProApiClient):
    """Init sensor."""
    self._hass = hass
    self._client = client
    self._account_id = account_id
    self._attr_native_value = None

    self.entity_id = generate_entity_id("text.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_home_pro_screen"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Home Pro Screen ({self._account_id})"
  
  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:led-strip"

  async def async_set_value(self, value: str) -> None:
    """Update the value."""
    self._attr_native_value = value
    animation_type = "static"
    if value is not None and len(value) > 3:
      animation_type = "scroll"

    await self._client.async_set_screen(self._attr_native_value, animation_type, "text", 200, 100)
    self.async_write_ha_state()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None:
      if state.state is not None:
        self._attr_native_value = state.state
        self._attr_state = state.state
      
      self._attributes = dict_to_typed_dict(state.attributes)
    
      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeElectricityCostTariffOverride state: {self._attr_state}')