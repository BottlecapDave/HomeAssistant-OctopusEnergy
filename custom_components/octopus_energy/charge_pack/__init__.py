"""Charge Pack: the planned charges and discharges of a home battery Octopus
controls (a SmartFlex device of type INVERTERS), as two calendars.

Octopus only lists dispatches that haven't ended, and changes its plan a lot.
So the calendars show the plan as it is now, plus a history of the dispatches
that started (as last listed), kept for HISTORY_KEEP_DAYS. One taken off the
plan before it started didn't happen, so it isn't kept."""
from datetime import datetime, timedelta

from ..api_client.charge_pack import ChargePackDevice, ChargePackDispatch, ChargePackDispatches, ChargePackStatus, ChargePackTelemetry

HISTORY_KEEP_DAYS = 30
KINDS = ("charge", "discharge")

def update_history(history: list[ChargePackDispatch], planned: list[ChargePackDispatch], current: datetime) -> list[ChargePackDispatch]:
  """The dispatches that have started, oldest first: those in `history`, with
  any planned one that's started added (or updated, matched by its start, while
  Octopus still lists it). Idle ones aren't kept, nor ones that ended over
  HISTORY_KEEP_DAYS ago."""
  by_start = {d.start: d for d in history}
  for d in planned:
    if d.start <= current and d.kind != "idle":
      by_start[d.start] = d
  cutoff = current - timedelta(days=HISTORY_KEEP_DAYS)
  return sorted((d for d in by_start.values() if d.end >= cutoff), key=lambda d: d.start)

def calendar_dispatches(history: list[ChargePackDispatch], planned: list[ChargePackDispatch], kind: str) -> list[ChargePackDispatch]:
  """What a calendar shows (`kind`: "charge" or "discharge"), oldest first: the
  history, then the planned ones (a planned one replaces a kept one with the same start)."""
  by_start = {d.start: d for d in history if d.kind == kind}
  for d in planned:
    if d.kind == kind:
      by_start[d.start] = d
  return sorted(by_start.values(), key=lambda d: d.start)

def current_or_next_dispatch(dispatches: list[ChargePackDispatch], current: datetime) -> ChargePackDispatch | None:
  """The dispatch running now, else the next one (None: neither)."""
  upcoming = [d for d in dispatches if d.end > current]
  running = [d for d in upcoming if d.start <= current]
  if running:
    return running[0]
  return min(upcoming, key=lambda d: d.start) if upcoming else None

ACTIVITY = {"charge": "charging", "discharge": "discharging", "idle": "idle"}

def current_activity(planned: list[ChargePackDispatch], current: datetime) -> tuple[str, ChargePackDispatch | None]:
  """What Octopus has the battery doing now: ("charging" | "discharging" | "idle", the
  dispatch running now), or ("none", None) when no dispatch is running."""
  for d in planned:
    if d.start <= current < d.end:
      return ACTIVITY[d.kind], d
  return "none", None

def kind_to_friendly_string(kind: str) -> str:
  return "Charge" if kind == "charge" else "Discharge"

# --- Mock data (account debug override "mock_charge_pack"), for testing without a battery ---

def get_mock_charge_pack_device():
  return ChargePackDevice("00000000-0000-4000-8000-000000000001", "Sigenergy SigenStor EC 12.0 SP", "SMARTFLEX_CONNECT",
                          "INVERTERS", "LIVE", "Sigenergy", "SigenStor EC 12.0 SP")

def mock_charge_pack_dispatches(current: datetime):
  """A plan around now (a charge running now, an idle gap, a discharge later and a charge
  overnight), the status, and readings that follow the charge (as Octopus sends them)."""
  half_hour = current.replace(minute=0 if current.minute < 30 else 30, second=0, microsecond=0)
  at = lambda minutes: half_hour + timedelta(minutes=minutes)
  planned = [
    ChargePackDispatch(at(-30), at(60), -3.3, "SMART"),
    ChargePackDispatch(at(60), at(180), 0.0, "SMART"),
    ChargePackDispatch(at(180), at(240), 4.4, "SMART"),
    ChargePackDispatch(at(600), at(720), -6.6, "SMART"),
  ]
  soc = 40 + (current.minute % 30)  # (moves, so the sensors visibly update)
  telemetry = ChargePackTelemetry(
    battery_state_of_charge=float(soc), battery_power_kw=-4.4, battery_connection_status="ONLINE",
    inverter_power_kw=-3.7, inverter_connection_status="ONLINE", solar_power_kw=0.7,
    grid_power_kw=4.6, site_consumption_kw=5.3, site_export_kw=0.0, peak_solar_power_kw=0.0)
  return ChargePackDispatches(planned, ChargePackStatus("LIVE", "SMART_CONTROL_CAPABLE", False), telemetry)
