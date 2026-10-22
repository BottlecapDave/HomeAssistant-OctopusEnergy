from datetime import datetime, timedelta

from custom_components.octopus_energy.api_client.charge_pack import ChargePackDevice, ChargePackDispatch
from custom_components.octopus_energy.charge_pack import calendar_dispatches, current_or_next_dispatch, update_history

def _at(text: str) -> datetime:
  return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S%z")

def _dispatch(start: str, end: str, kwh: float) -> ChargePackDispatch:
  return ChargePackDispatch(_at(start), _at(end), kwh, "SMART")

def test_when_dispatches_start_then_they_join_the_history():
  charge = _dispatch("2026-10-22T01:00:00Z", "2026-10-22T03:00:00Z", -4.5)
  discharge = _dispatch("2026-10-22T16:00:00Z", "2026-10-22T19:00:00Z", 6)
  idle = _dispatch("2026-10-22T00:30:00Z", "2026-10-22T01:00:00Z", 0)

  history = update_history([], [idle, charge, discharge], _at("2026-10-22T02:00:00Z"))

  assert history == [charge]  # started, not idle; the discharge hasn't started

def test_when_a_started_dispatch_changes_then_the_history_has_the_latest():
  first = _dispatch("2026-10-22T01:00:00Z", "2026-10-22T03:00:00Z", -4.5)
  longer = _dispatch("2026-10-22T01:00:00Z", "2026-10-22T04:00:00Z", -6)

  history = update_history([first], [longer], _at("2026-10-22T02:00:00Z"))

  assert history == [longer]

def test_when_octopus_stops_listing_a_dispatch_then_it_stays_in_the_history():
  done = _dispatch("2026-10-22T01:00:00Z", "2026-10-22T03:00:00Z", -4.5)

  assert update_history([done], [], _at("2026-10-22T05:00:00Z")) == [done]

def test_when_a_dispatch_is_old_then_it_leaves_the_history():
  old = _dispatch("2026-09-01T01:00:00Z", "2026-09-01T03:00:00Z", -4.5)
  recent = _dispatch("2026-10-20T01:00:00Z", "2026-10-20T03:00:00Z", -4.5)

  assert update_history([old, recent], [], _at("2026-10-22T05:00:00Z")) == [recent]

def test_calendar_dispatches_are_split_by_kind():
  done = _dispatch("2026-10-21T01:00:00Z", "2026-10-21T03:00:00Z", -4.5)
  charge = _dispatch("2026-10-23T01:00:00Z", "2026-10-23T03:00:00Z", -3)
  discharge = _dispatch("2026-10-22T16:00:00Z", "2026-10-22T19:00:00Z", 6)

  assert calendar_dispatches([done], [discharge, charge], "charge") == [done, charge]
  assert calendar_dispatches([done], [discharge, charge], "discharge") == [discharge]

def test_a_planned_dispatch_replaces_the_kept_one_with_the_same_start():
  kept = _dispatch("2026-10-22T01:00:00Z", "2026-10-22T03:00:00Z", -4.5)
  now_planned = _dispatch("2026-10-22T01:00:00Z", "2026-10-22T04:00:00Z", -6)

  assert calendar_dispatches([kept], [now_planned], "charge") == [now_planned]

def test_current_or_next_dispatch():
  a = _dispatch("2026-10-22T01:00:00Z", "2026-10-22T03:00:00Z", -4.5)
  b = _dispatch("2026-10-22T16:00:00Z", "2026-10-22T19:00:00Z", -2)

  assert current_or_next_dispatch([a, b], _at("2026-10-22T02:00:00Z")) == a
  assert current_or_next_dispatch([a, b], _at("2026-10-22T03:00:00Z")) == b
  assert current_or_next_dispatch([a, b], _at("2026-10-22T20:00:00Z")) is None

def test_dispatch_kind_and_round_trip():
  charge = _dispatch("2026-10-22T01:00:00Z", "2026-10-22T03:00:00Z", -4.5)

  assert charge.kind == "charge" and charge.kwh == 4.5
  assert _dispatch("2026-10-22T01:00:00Z", "2026-10-22T03:00:00Z", 2).kind == "discharge"
  assert _dispatch("2026-10-22T01:00:00Z", "2026-10-22T03:00:00Z", 0).kind == "idle"
  assert ChargePackDispatch.from_dict(charge.to_dict()) == charge

def test_device_make_and_model_from_its_name():
  device = ChargePackDevice("abc", "Sigenergy SigenStor EC 12.0 SP", "SMARTFLEX_CONNECT", "INVERTERS", "LIVE")

  assert device.make == "Sigenergy"
  assert device.model == "SigenStor EC 12.0 SP"
  assert ChargePackDevice.from_dict(device.to_dict()).to_dict() == device.to_dict()
