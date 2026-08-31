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
from homeassistant.components.select import SelectEntity
from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import BaseOctopusEnergyChargePointSensor
from ..api_client import OctopusEnergyApiClient
from ..api_client.charge_point import OnboardedChargePoint
from ..coordinators.charge_point_configuration_and_status import ChargePointCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

# ControlMode enum, confirmed via live GraphQL introspection
control_mode_options = ["SMART", "MANUAL"]

class OctopusEnergyChargePointControlModeSelect(CoordinatorEntity, BaseOctopusEnergyChargePointSensor, SelectEntity, RestoreEntity):
  """Select for setting the control mode of a charge point (mirrors the ControlMode enum: SMART/MANUAL)."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint, is_mocked: bool):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyChargePointSensor.__init__(self, hass, charge_point_id, charge_point, "select")

    self._state = None
    self._last_updated = None
    self._client = client
    self._account_id = account_id
    self._is_mocked = is_mocked
    self.entity_id = generate_entity_id("select.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_charge_point_{self._charge_point_id}_control_mode_select"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Control Mode Charge Point ({self._charge_point_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:tune"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def options(self) -> list[str]:
    """Return the available control modes."""
    return control_mode_options

  @property
  def current_option(self) -> str:
    return self._state

  @callback
  def _handle_coordinator_update(self) -> None:
    """The current control mode of the charge point."""
    result: ChargePointCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    if result is None or (self._last_updated is not None and result.last_retrieved is not None and self._last_updated > result.last_retrieved):
      return

    if result.data is not None and result.data.controlMode is not None:
      self._state = result.data.controlMode

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_select_option(self, option: str) -> None:
    """Set the control mode."""
    if option not in control_mode_options:
      raise ValueError(f"Invalid control mode '{option}'. Must be one of {control_mode_options}")

    try:
      await self._client.async_set_charge_point_control_mode(self._account_id, self._charge_point_id, option)
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_select_option error due to mocking mode: {e}')
      else:
        raise

    self._state = option
    self._last_updated = utcnow()
    self.async_write_ha_state()

  async def async_added_to_hass(self) -> None:
    """Restore last state."""
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._attributes = dict_to_typed_dict(state.attributes)
      if state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
        self._state = state.state

    _LOGGER.debug(f'Restored OctopusEnergyChargePointControlModeSelect state: {self._state}')
