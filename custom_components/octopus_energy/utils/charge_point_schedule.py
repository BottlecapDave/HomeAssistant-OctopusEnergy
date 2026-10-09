from datetime import datetime, timedelta

# datetime.weekday() is 0=Monday..6=Sunday - matches the day names the API
# itself uses for schedule entries.
_day_names = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

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
