import logging

from homeassistant.const import (
    PERCENTAGE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorStateClass,
)

from .base import (BaseOctopusEnergyChargePointSensor)
from ..utils.attributes import dict_to_typed_dict
from ..api_client.charge_point import OnboardedChargePoint
from ..coordinators.charge_point_configuration_and_status import ChargePointCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyChargePointLedBrightness(CoordinatorEntity, BaseOctopusEnergyChargePointSensor, RestoreSensor):
  """Sensor for displaying the LED brightness percentage of a charge point."""

  def __init__(self, hass: HomeAssistant, coordinator, charge_point_id: str, charge_point: OnboardedChargePoint):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyChargePointSensor.__init__(self, hass, charge_point_id, charge_point)

    self._state = None
    self._last_updated = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_charge_point_{self._charge_point_id}_led_brightness"

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
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.MEASUREMENT

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self):
    return self._state

  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the LED brightness for the charge point."""
    current = now()
    result: ChargePointCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None

    if (result is not None
        and result.data is not None
        and result.data.configuration is not None
        and result.data.configuration.LEDBrightnessPercentage is not None):
      _LOGGER.debug(f"Updating OctopusEnergyChargePointLedBrightness for '{self._charge_point_id}'")

      self._state = result.data.configuration.LEDBrightnessPercentage
      self._last_updated = current

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()

    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes, [])

      _LOGGER.debug(f'Restored OctopusEnergyChargePointLedBrightness state: {self._state}')
