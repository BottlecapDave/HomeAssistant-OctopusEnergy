import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.switch import SwitchEntity
from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import OctopusEnergyIntelligentSensor
from ..api_client import OctopusEnergyApiClient
from . import is_in_bump_charge
from ..coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentBumpCharge(CoordinatorEntity, SwitchEntity, OctopusEnergyIntelligentSensor, RestoreEntity):
  """Switch for turning intelligent bump charge on and off."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, device, account_id: str, is_mocked: bool):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)

    self._state = False
    self._last_updated = None
    self._client = client
    self._account_id = account_id
    self._attributes = {}
    self._is_mocked = is_mocked
    self.entity_id = generate_entity_id("switch.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_intelligent_bump_charge"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Intelligent Bump Charge ({self._account_id})"

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
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine if the bump charge is on."""
    result: IntelligentDispatchesCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    if result is None or (self._last_updated is not None and self._last_updated > result.last_retrieved):
      return self._state

    current_date = utcnow()
    self._state = is_in_bump_charge(current_date, result.dispatches.planned if result.dispatches is not None else [])

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_turn_on(self):
    """Turn on the switch."""
    try:
      await self._client.async_turn_on_intelligent_bump_charge(
        self._account_id
      )
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_turn_on error due to mocking mode: {e}')
      else:
        raise

    self._state = True
    self._last_updated = utcnow()
    self.async_write_ha_state()

  async def async_turn_off(self):
    """Turn off the switch."""
    try:
      await self._client.async_turn_off_intelligent_bump_charge(
        self._account_id
      )
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_turn_off error due to mocking mode: {e}')
      else:
        raise

    self._state = False
    self._last_updated = utcnow()
    self.async_write_ha_state()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else state.state
      self._attributes = dict_to_typed_dict(state.attributes)
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored OctopusEnergyIntelligentBumpCharge state: {self._state}')