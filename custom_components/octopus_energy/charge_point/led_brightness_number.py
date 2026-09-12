import logging

from homeassistant.const import (
    PERCENTAGE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.number import RestoreNumber, NumberMode
from homeassistant.util.dt import (utcnow)

from .base import BaseOctopusEnergyChargePointSensor
from ..api_client import OctopusEnergyApiClient
from ..api_client.charge_point import OnboardedChargePoint
from ..coordinators.charge_point_configuration_and_status import ChargePointCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyChargePointLedBrightnessNumber(CoordinatorEntity, RestoreNumber, BaseOctopusEnergyChargePointSensor):
  """Number for setting the LED brightness percentage of a charge point."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint, is_mocked: bool):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyChargePointSensor.__init__(self, hass, charge_point_id, charge_point, "number")

    self._state = None
    self._last_updated = None
    self._client = client
    self._account_id = account_id
    self._is_mocked = is_mocked
    self.entity_id = generate_entity_id("number.{}", self.unique_id, hass=hass)

    self._attr_native_min_value = 0
    self._attr_native_max_value = 100
    self._attr_native_step = 1
    self._attr_mode = NumberMode.SLIDER

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_charge_point_{self._charge_point_id}_led_brightness_number"

  @property
  def name(self):
    """Name of the sensor."""
    return f"LED Brightness Charge Point ({self._charge_point_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:brightness-percent"

  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return PERCENTAGE

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self) -> float:
    return self._state

  @callback
  def _handle_coordinator_update(self) -> None:
    """The current LED brightness of the charge point."""
    result: ChargePointCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    if result is None or (self._last_updated is not None and result.last_retrieved is not None and self._last_updated > result.last_retrieved):
      return

    if (result.data is not None
        and result.data.configuration is not None
        and result.data.configuration.LEDBrightnessPercentage is not None):
      self._state = result.data.configuration.LEDBrightnessPercentage

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_set_native_value(self, value: float) -> None:
    """Set new value."""
    if value is None or value < self._attr_native_min_value or value > self._attr_native_max_value:
      raise ValueError(f"Value must be between {self._attr_native_min_value} and {self._attr_native_max_value}")

    try:
      await self._client.async_set_charge_point_led_brightness(self._account_id, self._charge_point_id, int(value))
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_set_native_value error due to mocking mode: {e}')
      else:
        raise

    self._state = value
    self._last_updated = utcnow()
    self.async_write_ha_state()

  async def async_added_to_hass(self) -> None:
    """Restore last state."""
    await super().async_added_to_hass()

    if ((last_state := await self.async_get_last_state()) and
        (last_number_data := await self.async_get_last_number_data())
      ):

      self._attributes = dict_to_typed_dict(last_state.attributes, ["min", "max", "step", "mode"])
      if last_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
        self._state = last_number_data.native_value

    _LOGGER.debug(f'Restored OctopusEnergyChargePointLedBrightnessNumber state: {self._state}')
