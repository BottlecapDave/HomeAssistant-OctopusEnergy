import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import (BaseOctopusEnergyChargePointSensor)
from ..utils.attributes import dict_to_typed_dict
from ..api_client.charge_point import OnboardedChargePoint
from ..coordinators.charge_point_configuration_and_status import ChargePointCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyChargePointEcoMode(CoordinatorEntity, BaseOctopusEnergyChargePointSensor, BinarySensorEntity, RestoreEntity):
  """Sensor for displaying if eco mode is enabled for a charge point."""

  def __init__(self, hass: HomeAssistant, coordinator, charge_point_id: str, charge_point: OnboardedChargePoint):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyChargePointSensor.__init__(self, hass, charge_point_id, charge_point, "binary_sensor")

    self._state = None
    self._last_updated = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_charge_point_{self._charge_point_id}_eco_mode"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Eco Mode Charge Point ({self._charge_point_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:leaf"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    return self._state

  @callback
  def _handle_coordinator_update(self) -> None:
    current = now()
    result: ChargePointCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None

    if (result is not None
        and result.data is not None
        and result.data.configuration is not None
        and result.data.configuration.isEcoModeEnabled is not None):
      _LOGGER.debug(f"Updating OctopusEnergyChargePointEcoMode for '{self._charge_point_id}'")

      self._state = result.data.configuration.isEcoModeEnabled
      self._last_updated = current

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or state.state is None else state.state.lower() == 'on'

    if (self._state is None):
      self._state = False

    _LOGGER.debug(f'Restored OctopusEnergyChargePointEcoMode state: {self._state}')
