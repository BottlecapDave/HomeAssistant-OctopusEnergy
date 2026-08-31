from datetime import timedelta
import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN
)
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import (
  RestoreSensor,
)

from .base import (BaseOctopusEnergyChargePointSensor)
from ..api_client import OctopusEnergyApiClient
from ..api_client.charge_point import OnboardedChargePoint
from ..const import REFRESH_RATE_IN_MINUTES_CHARGE_POINT

_LOGGER = logging.getLogger(__name__)

# No existing coordinator precedent covers this shape (a multi-period weekly
# schedule, not a single target-time/SoC concept like IOG's), so this entity
# fetches on its own regular polling interval rather than being backed by
# the shared charge point configuration/status coordinator.
class OctopusEnergyChargePointSchedule(BaseOctopusEnergyChargePointSensor, RestoreSensor):
  """Read-only sensor for a charge point's weekly charging schedule."""

  _attr_should_poll = True
  SCAN_INTERVAL = timedelta(minutes=REFRESH_RATE_IN_MINUTES_CHARGE_POINT)

  def __init__(self, hass: HomeAssistant, client: OctopusEnergyApiClient, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint):
    """Init sensor."""
    BaseOctopusEnergyChargePointSensor.__init__(self, hass, charge_point_id, charge_point)

    self._client = client
    self._account_id = account_id
    self._state = None
    self._attributes = { "schedule": {} }

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_charge_point_{self._charge_point_id}_schedule"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Schedule Charge Point ({self._charge_point_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:calendar-clock"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self):
    return self._state

  async def async_update(self):
    """Fetch the latest schedule for the charge point."""
    try:
      schedules = await self._client.async_get_charge_point_schedules(self._account_id, self._charge_point_id)
    except Exception as e:
      _LOGGER.debug(f"Failed to retrieve schedule for charge point '{self._charge_point_id}': {e}")
      return

    if schedules is None:
      return

    schedule_by_day = {}
    today_period_count = 0
    for day_schedule in schedules:
      day = day_schedule.get("day")
      settings = day_schedule.get("chargePointScheduleSettings", []) or []
      schedule_by_day[day] = [
        { "start": setting.get("start"), "end": setting.get("end"), "action": setting.get("action") }
        for setting in settings
      ]

    self._attributes["schedule"] = schedule_by_day

    # Summarise as the number of scheduled periods across the week; a
    # richer "next ON window" summary needs knowing which day is "today"
    # in the charge point's own timezone, which isn't exposed by this query.
    total_periods = sum(len(periods) for periods in schedule_by_day.values())
    self._state = f"{total_periods} period{'s' if total_periods != 1 else ''}"

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()

    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict(state.attributes)

      _LOGGER.debug(f'Restored OctopusEnergyChargePointSchedule state: {self._state}')
