import logging
from datetime import datetime

from homeassistant.const import (
    UnitOfEnergy,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util.dt import (utcnow)
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorStateClass,
)

from .base import BaseOctopusEnergyChargePointSensor
from ..api_client.charge_point import OnboardedChargePoint
from ..utils.attributes import dict_to_typed_dict
from ..utils.charge_point_energy import integrate_energy_kwh

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyChargePointEnergy(BaseOctopusEnergyChargePointSensor, RestoreSensor):
  """Sensor for tracking the charge point's cumulative energy consumption, for the Energy Dashboard.

  Octopus's API doesn't expose a live cumulative energy counter for the
  charger - only a per-session total once a session has fully ended - so
  this integrates the live_power sensor's own readings over time instead,
  the same Riemann-sum approach Home Assistant's built-in "Integration -
  Riemann sum integral" helper uses, just built in rather than requiring
  you to add one yourself.

  Starts from 0 when first added - there's no way to know the charger's
  actual historical lifetime total from the API, so this only reflects
  consumption from when this sensor was first created onward.

  The running integration only lives in memory: a HA restart mid-charge
  resumes from the last-saved (pre-restart) total rather than the true
  total at restart time, silently losing whatever was drawn during the
  gap. There's no live_power history to replay this from after a restart.
  """

  def __init__(self, hass: HomeAssistant, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint, live_power_entity_id: str):
    """Init sensor."""
    BaseOctopusEnergyChargePointSensor.__init__(self, hass, account_id, charge_point_id, charge_point)

    self._state = None
    self._last_reading_at: datetime | None = None
    self._last_power_kw: float | None = None
    # The live power sensor's own real entity_id, passed in by sensor.py
    # rather than reconstructed here - see the comment at that call site.
    self._live_power_entity_id = live_power_entity_id
    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_charge_point_{self._charge_point_id}_energy"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Energy Charge Point ({self._charge_point_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.ENERGY

  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return UnitOfEnergy.KILO_WATT_HOUR

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL_INCREASING

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self) -> float:
    return self._state

  @callback
  def _async_update_from_power(self, event) -> None:
    """Integrate the live power sensor's latest reading into the running energy total."""
    new_state = event.data.get("new_state")
    if new_state is None or new_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
      power_kw = None
    else:
      try:
        power_kw = float(new_state.state)
      except (TypeError, ValueError):
        power_kw = None

    now = utcnow()
    # Integrate using the *previous* reading's power over the window that's
    # just elapsed - that's what was actually being drawn during it, unlike
    # the new reading that just arrived. Using the new value instead (as
    # this used to) means e.g. the step where charging stops (power drops
    # to 0) gets integrated as elapsed_time * 0 - discarding real energy
    # that was actually consumed right up until that reading.
    if self._last_reading_at is not None and self._last_power_kw is not None and self._state is not None:
      elapsed_hours = (now - self._last_reading_at).total_seconds() / 3600
      self._state = integrate_energy_kwh(self._state, self._last_power_kw, elapsed_hours)
      self.async_write_ha_state()

    self._last_reading_at = now
    self._last_power_kw = power_kw

  async def async_added_to_hass(self) -> None:
    """Restore last state and start tracking the live power sensor."""
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()

    if state is not None and last_sensor_state is not None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)

    if self._state is None:
      self._state = 0

    _LOGGER.debug(f'Restored OctopusEnergyChargePointEnergy state: {self._state}')

    self.async_on_remove(
      async_track_state_change_event(
        self.hass, [self._live_power_entity_id], self._async_update_from_power
      )
    )
