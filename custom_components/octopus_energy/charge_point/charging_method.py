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
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
)

from .base import (BaseOctopusEnergyChargePointSensor)
from ..utils.attributes import dict_to_typed_dict
from ..api_client.charge_point import OnboardedChargePoint
from ..coordinators.charge_point_configuration_and_status import ChargePointCoordinatorResult

_LOGGER = logging.getLogger(__name__)

# ChargePointChargingMethod enum, confirmed via live GraphQL introspection
charging_method_options = [
  "SCHEDULED",
  "ON_DEMAND",
]

class OctopusEnergyChargePointChargingMethod(CoordinatorEntity, BaseOctopusEnergyChargePointSensor, RestoreSensor):
  """Sensor for displaying the charging method of a charge point."""

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
    return f"octopus_energy_charge_point_{self._charge_point_id}_charging_method"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Charging Method Charge Point ({self._charge_point_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:ev-plug-type2"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.ENUM

  @property
  def options(self):
    """The possible options of the sensor"""
    return charging_method_options

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self):
    return self._state

  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the charging method for the charge point."""
    current = now()
    result: ChargePointCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None

    # chargingMethod: schema says non-null, but treat defensively
    if (result is not None
        and result.data is not None
        and result.data.chargingMethod is not None):
      _LOGGER.debug(f"Updating OctopusEnergyChargePointChargingMethod for '{self._charge_point_id}'")

      self._state = result.data.chargingMethod
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

      _LOGGER.debug(f'Restored OctopusEnergyChargePointChargingMethod state: {self._state}')
