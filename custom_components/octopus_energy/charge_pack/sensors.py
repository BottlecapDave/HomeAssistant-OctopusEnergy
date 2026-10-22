import logging

from homeassistant.const import (
  STATE_UNAVAILABLE,
  STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
)

from . import current_activity
from .base import OctopusEnergyChargePackSensor
from ..api_client.charge_pack import ChargePackDevice
from ..coordinators.charge_pack import ChargePackDispatchesCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class _ChargePackSensorBase(CoordinatorEntity, OctopusEnergyChargePackSensor, RestoreSensor):

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str, device: ChargePackDevice):
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyChargePackSensor.__init__(self, device)
    self._account_id = account_id
    self._state = None
    self._attributes = {}
    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def extra_state_attributes(self):
    return self._attributes

  @property
  def native_value(self):
    return self._state

  def _result(self) -> ChargePackDispatchesCoordinatorResult | None:
    return self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None

  async def async_added_to_hass(self):
    """Restore the last state (until the first read), then show the coordinator's data if it has any."""
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes, [])
    if self._result() is not None:
      self._handle_coordinator_update()

class OctopusEnergyChargePackState(_ChargePackSensorBase):
  """Octopus's state for the battery, e.g. SMART_CONTROL_CAPABLE."""

  @property
  def unique_id(self):
    return f"octopus_energy_{self._account_id}_{self._device.id}_charge_pack_state"

  @property
  def name(self):
    return f"Charge Pack State ({self._account_id})"

  @property
  def icon(self):
    return "mdi:home-battery"

  @callback
  def _handle_coordinator_update(self) -> None:
    result = self._result()
    status = result.status if result is not None else None
    if status is not None:
      self._state = status.current_state
      self._attributes = {
        "status": status.current,
        "is_suspended": status.is_suspended,
        "data_last_retrieved": result.last_retrieved,
      }
    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

class OctopusEnergyChargePackActivity(_ChargePackSensorBase):
  """What Octopus has the battery doing now: charging, discharging, idle or none."""

  @property
  def unique_id(self):
    return f"octopus_energy_{self._account_id}_{self._device.id}_charge_pack_activity"

  @property
  def name(self):
    return f"Charge Pack Activity ({self._account_id})"

  @property
  def device_class(self):
    return SensorDeviceClass.ENUM

  @property
  def options(self):
    return ["charging", "discharging", "idle", "none"]

  @property
  def icon(self):
    return {"charging": "mdi:battery-arrow-up", "discharging": "mdi:battery-arrow-down",
            "idle": "mdi:battery-clock"}.get(self._state, "mdi:battery")

  @callback
  def _handle_coordinator_update(self) -> None:
    result = self._result()
    if result is not None:
      current = utcnow()
      activity, dispatch = current_activity(result.planned, current)
      self._state = activity
      self._attributes = {
        "start": dispatch.start if dispatch else None,
        "end": dispatch.end if dispatch else None,
        "energy_kwh": dispatch.kwh if dispatch else None,
        "minutes_left": int((dispatch.end - current).total_seconds() // 60) if dispatch else None,
        "data_last_retrieved": result.last_retrieved,
      }
    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()
