import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.switch import SwitchEntity
from homeassistant.util.dt import (utcnow)

from .base import OctopusEnergyIntelligentSensor
from ..api_client import OctopusEnergyApiClient
from . import is_in_bump_charge
from ..coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult


_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentBumpCharge(CoordinatorEntity, SwitchEntity, OctopusEnergyIntelligentSensor):
  """Switch for turning intelligent bump charge on and off."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, device, account_id: str):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
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
    return f"octopus_energy_{self._account_id}_intelligent_bump_charge"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy {self._account_id} Intelligent Bump Charge"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:ev-plug-type2"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def is_on(self):
    """Determine if the bump charge is on."""
    result: IntelligentDispatchesCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    if result is None or (self._last_updated is not None and self._last_updated > result.last_retrieved):
      return self._state
    
    if result is not None:
      self._attributes["data_last_retrieved"] = result.last_retrieved

    current_date = utcnow()
    self._state = is_in_bump_charge(current_date, result.dispatches.planned)
    self._attributes["last_evaluated"] = current_date
    
    return self._state

  async def async_turn_on(self):
    """Turn on the switch."""
    await self._client.async_turn_on_intelligent_bump_charge(
      self._account_id
    )
    self._state = True
    self._last_updated = utcnow()
    self.async_write_ha_state()

  async def async_turn_off(self):
    """Turn off the switch."""
    await self._client.async_turn_off_intelligent_bump_charge(
      self._account_id
    )
    self._state = False
    self._last_updated = utcnow()
    self.async_write_ha_state()