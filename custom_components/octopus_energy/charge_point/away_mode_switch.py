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

from .base import BaseOctopusEnergyChargePointSensor
from ..api_client import OctopusEnergyApiClient
from ..api_client.charge_point import OnboardedChargePoint
from ..coordinators.charge_point_configuration_and_status import ChargePointCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyChargePointAwayModeSwitch(CoordinatorEntity, BaseOctopusEnergyChargePointSensor, SwitchEntity, RestoreEntity):
  """Switch for turning charge point away mode on and off."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint, is_mocked: bool):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyChargePointSensor.__init__(self, hass, charge_point_id, charge_point, "switch")

    self._state = False
    self._last_updated = None
    self._client = client
    self._account_id = account_id
    self._is_mocked = is_mocked
    self.entity_id = generate_entity_id("switch.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_charge_point_{self._charge_point_id}_away_mode_switch"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Away Mode Charge Point ({self._charge_point_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:home-export-outline"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    return self._state

  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine the current away mode state."""
    result: ChargePointCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    if result is None or (self._last_updated is not None and result.last_retrieved is not None and self._last_updated > result.last_retrieved):
      return

    if (result.data is not None
        and result.data.configuration is not None
        and result.data.configuration.isAwayMode is not None):
      self._state = result.data.configuration.isAwayMode

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_turn_on(self, **kwargs):
    """Turn on the switch."""
    try:
      await self._client.async_set_charge_point_away_mode(self._account_id, self._charge_point_id, True)
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_turn_on error due to mocking mode: {e}')
      else:
        raise

    self._state = True
    self._last_updated = utcnow()
    self.async_write_ha_state()

  async def async_turn_off(self, **kwargs):
    """Turn off the switch."""
    try:
      await self._client.async_set_charge_point_away_mode(self._account_id, self._charge_point_id, False)
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
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else state.state == "on"
      self._attributes = dict_to_typed_dict(state.attributes)

    if (self._state is None):
      self._state = False

    _LOGGER.debug(f'Restored OctopusEnergyChargePointAwayModeSwitch state: {self._state}')
