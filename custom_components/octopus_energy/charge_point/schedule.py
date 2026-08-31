from datetime import datetime, timedelta
import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.sensor import (
  RestoreSensor,
)
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.util.dt import (now as dt_now)

from .base import (BaseOctopusEnergyChargePointSensor)
from ..api_client import OctopusEnergyApiClient
from ..api_client.charge_point import OnboardedChargePoint
from ..const import REFRESH_RATE_IN_MINUTES_CHARGE_POINT

_LOGGER = logging.getLogger(__name__)

# datetime.weekday() is 0=Monday..6=Sunday - matches the day names the API
# itself uses for schedule entries.
_day_names = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

# Start the burst a little ahead of the scheduled boundary itself, so the
# window is already open and forcing fresh polls right as the transition
# actually happens, rather than starting to poll only after the fact.
schedule_burst_lead_seconds = 5

def compute_next_schedule_transition(schedule_by_day: dict, now: datetime) -> datetime | None:
  """Find the next start or end time across the whole weekly schedule,
  strictly after `now`. A pure function so it can be unit tested without a
  real hass instance.

  Checks a full week ahead (not just today/tomorrow) so a schedule with
  periods on only one day of the week is still found correctly. Returns
  None if the schedule has no periods at all.
  """
  candidates = []
  for day_offset in range(8):  # today plus a full week, to catch "next week" wraparound
    day = now + timedelta(days=day_offset)
    day_name = _day_names[day.weekday()]
    periods = schedule_by_day.get(day_name, [])
    for period in periods:
      for key in ("start", "end"):
        time_str = period.get(key)
        if not time_str:
          continue
        try:
          hour, minute = (int(part) for part in time_str.split(":")[:2])
        except (ValueError, AttributeError):
          continue

        candidate = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate > now:
          candidates.append(candidate)

  return min(candidates) if candidates else None

# No existing coordinator precedent covers this shape (a multi-period weekly
# schedule, not a single target-time/SoC concept like IOG's), so this entity
# fetches on its own regular polling interval rather than being backed by
# the shared charge point configuration/status coordinator.
class OctopusEnergyChargePointSchedule(BaseOctopusEnergyChargePointSensor, RestoreSensor):
  """Read-only sensor for a charge point's weekly charging schedule."""

  _attr_should_poll = True
  SCAN_INTERVAL = timedelta(minutes=REFRESH_RATE_IN_MINUTES_CHARGE_POINT)

  def __init__(self, hass: HomeAssistant, client: OctopusEnergyApiClient, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint, coordinator):
    """Init sensor."""
    BaseOctopusEnergyChargePointSensor.__init__(self, hass, charge_point_id, charge_point)

    self._client = client
    self._account_id = account_id
    # The charge point configuration/status coordinator - not used for this
    # entity's own data (see the module docstring above), only so a
    # scheduled charging boundary can trigger its burst-refresh, the same
    # way boost start/stop does.
    self._coordinator = coordinator
    self._state = None
    self._attributes = { "schedule": {} }
    self._cancel_next_transition_timer = None

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

    self._schedule_next_transition_timer(schedule_by_day)

  def _schedule_next_transition_timer(self, schedule_by_day: dict) -> None:
    """(Re)arm a timer for the next scheduled start/end boundary, so the
    charge point coordinator can burst-refresh right as it happens - the
    same reasoning as boost_switch's burst-refresh trigger, just for
    scheduled transitions instead of a manual boost."""
    if self._cancel_next_transition_timer is not None:
      self._cancel_next_transition_timer()
      self._cancel_next_transition_timer = None

    if self._coordinator is None:
      return

    next_transition = compute_next_schedule_transition(schedule_by_day, dt_now())
    if next_transition is None:
      return

    fire_at = next_transition - timedelta(seconds=schedule_burst_lead_seconds)

    @callback
    def _on_transition_time(_now) -> None:
      self._coordinator.async_start_burst_refresh()
      # The schedule itself hasn't changed, so the next boundary can be
      # armed straight away rather than waiting for the next polled update.
      self._schedule_next_transition_timer(schedule_by_day)

    self._cancel_next_transition_timer = async_track_point_in_time(self.hass, _on_transition_time, fire_at)

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()

    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict(state.attributes)

      _LOGGER.debug(f'Restored OctopusEnergyChargePointSchedule state: {self._state}')

      schedule_by_day = self._attributes.get("schedule")
      if schedule_by_day:
        self._schedule_next_transition_timer(schedule_by_day)

  async def async_will_remove_from_hass(self) -> None:
    """Ensure the transition timer is cleaned up when the entity is removed."""
    if self._cancel_next_transition_timer is not None:
      self._cancel_next_transition_timer()
      self._cancel_next_transition_timer = None

    await super().async_will_remove_from_hass()
