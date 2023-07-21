import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.switch import SwitchEntity
from homeassistant.util.dt import (utcnow)

from .base import OctopusEnergyIntelligentSensor
from ..api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentSmartCharge(CoordinatorEntity, SwitchEntity, OctopusEnergyIntelligentSensor):
  """Switch for turning intelligent smart charge on and off."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, device, account_id: str):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)

    self._state = False
    self._last_updated = None
    self._client = client
    self._account_id = account_id
    self._attributes = {}
    self.entity_id = generate_entity_id("switch.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_intelligent_smart_charge"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Intelligent Smart Charge"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:ev-station"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    """Determines if smart charge is currently on."""
    if (self.coordinator.data is None) or (self._last_updated is not None and "last_updated" in self.coordinator.data and self._last_updated > self.coordinator.data["last_updated"]):
      return self._state

    self._state = self.coordinator.data["smart_charge"]
    
    return self._state

  async def async_turn_on(self):
    """Turn on the switch."""
    await self._client.async_turn_on_intelligent_smart_charge(
      self._account_id
    )
    self._state = True
    self._last_updated = utcnow()
    self.async_write_ha_state()

  async def async_turn_off(self):
    """Turn off the switch."""
    await self._client.async_turn_off_intelligent_smart_charge(
      self._account_id
    )
    self._state = False
    self._last_updated = utcnow()
    self.async_write_ha_state()