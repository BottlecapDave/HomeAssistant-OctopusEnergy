"""Charge Pack: the planned charges and discharges of a home battery Octopus
controls (a SmartFlex device of type INVERTERS), as two calendars.

Octopus only lists dispatches that haven't ended, and changes its plan a lot.
So the calendars show the plan as it is now, plus a history of the dispatches
that started (as last listed), kept for HISTORY_KEEP_DAYS. One taken off the
plan before it started didn't happen, so it isn't kept."""
from datetime import datetime, timedelta

from ..api_client.charge_pack import ChargePackDispatch

HISTORY_KEEP_DAYS = 30
KINDS = ("charge", "discharge")

def update_history(history: list[ChargePackDispatch], planned: list[ChargePackDispatch], current: datetime,
                   keep_days: int = HISTORY_KEEP_DAYS) -> list[ChargePackDispatch]:
  """The dispatches that have started, oldest first: those in `history`, with
  any planned one that's started added (or updated, matched by its start, while
  Octopus still lists it). Idle ones aren't kept, nor ones that ended over
  `keep_days` ago."""
  by_start = {d.start: d for d in history or []}
  for d in planned or []:
    if d.start <= current and d.kind != "idle":
      by_start[d.start] = d
  cutoff = current - timedelta(days=keep_days)
  return sorted((d for d in by_start.values() if d.end >= cutoff), key=lambda d: d.start)

def calendar_dispatches(history: list[ChargePackDispatch], planned: list[ChargePackDispatch], kind: str) -> list[ChargePackDispatch]:
  """What a calendar shows (`kind`: "charge" or "discharge"), oldest first: the
  history, then the planned ones (a planned one replaces a kept one with the same start)."""
  by_start = {d.start: d for d in history or [] if d.kind == kind}
  for d in planned or []:
    if d.kind == kind:
      by_start[d.start] = d
  return sorted(by_start.values(), key=lambda d: d.start)

def current_or_next_dispatch(dispatches: list[ChargePackDispatch], current: datetime) -> ChargePackDispatch | None:
  """The dispatch running now, else the next one (None: neither)."""
  upcoming = [d for d in dispatches or [] if d.end > current]
  running = [d for d in upcoming if d.start <= current]
  if running:
    return running[0]
  return min(upcoming, key=lambda d: d.start) if upcoming else None

ACTIVITY = {"charge": "charging", "discharge": "discharging", "idle": "idle"}

def current_activity(planned: list[ChargePackDispatch], current: datetime) -> tuple[str, ChargePackDispatch | None]:
  """What Octopus has the battery doing now: ("charging" | "discharging" | "idle", the
  dispatch running now), or ("none", None) when no dispatch is running."""
  for d in planned or []:
    if d.start <= current < d.end:
      return ACTIVITY[d.kind], d
  return "none", None

def kind_to_friendly_string(kind: str) -> str:
  return "Charge" if kind == "charge" else "Discharge"
