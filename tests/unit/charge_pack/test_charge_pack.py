from datetime import datetime, timedelta

from custom_components.octopus_energy.api_client.charge_pack import ChargePackDevice, ChargePackDispatch, ChargePackTelemetry
from custom_components.octopus_energy.charge_pack import calendar_dispatches, current_activity, current_or_next_dispatch, get_mock_charge_pack_device, mock_charge_pack_dispatches, update_history

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

def test_device_make_and_model_from_the_api_win():
  device = ChargePackDevice("abc", "Sigenergy SigenStor EC 12.0 SP", "SMARTFLEX_CONNECT", "INVERTERS", "LIVE", "Sigenergy", "SigenStor EC 12.0")

  assert device.model == "SigenStor EC 12.0"
  assert ChargePackDevice.from_dict(device.to_dict()).model == "SigenStor EC 12.0"

def test_current_activity():
  charge = _dispatch("2026-10-22T01:00:00Z", "2026-10-22T03:00:00Z", -4.5)
  idle = _dispatch("2026-10-22T03:00:00Z", "2026-10-22T04:00:00Z", 0)
  discharge = _dispatch("2026-10-22T16:00:00Z", "2026-10-22T19:00:00Z", 6)
  planned = [charge, idle, discharge]

  assert current_activity(planned, _at("2026-10-22T02:00:00Z")) == ("charging", charge)
  assert current_activity(planned, _at("2026-10-22T03:30:00Z")) == ("idle", idle)
  assert current_activity(planned, _at("2026-10-22T18:59:00Z")) == ("discharging", discharge)
  assert current_activity(planned, _at("2026-10-22T19:00:00Z")) == ("none", None)

def test_telemetry_from_the_api():
  # As Octopus sent it for a SigenStor during a discharge
  device = {
    "id": "00000000-0011-4000-8020-000000006cc9",
    "telemetry": {
      "inverter": {"connectionStatus": "ONLINE", "powerInKw": "6.01"},
      "battery": {"connectionStatus": "ONLINE", "powerInKw": "4.504", "stateOfCharge": "43.900"},
      "solar": {"powerInKw": "1.528"},
      "grid": {"powerInKw": "5.775"},
      "site": {"consumptionInKw": "0.257", "exportInKw": "5.775"},
    },
    "details": {"solar": {"peakSolarPowerInKw": "0"}},
  }

  telemetry = ChargePackTelemetry.from_api(device)

  assert telemetry.battery_state_of_charge == 43.9
  assert telemetry.battery_power_kw == 4.504 and telemetry.battery_connection_status == "ONLINE"
  assert telemetry.inverter_power_kw == 6.01 and telemetry.inverter_connection_status == "ONLINE"
  assert telemetry.solar_power_kw == 1.528 and telemetry.peak_solar_power_kw == 0
  assert telemetry.grid_power_kw == -5.775  # exporting: negative, like the meter's current demand
  assert telemetry.site_consumption_kw == 0.257 and telemetry.site_export_kw == 5.775

def test_telemetry_missing_or_partial():
  assert ChargePackTelemetry.from_api({"id": "x"}) is None
  telemetry = ChargePackTelemetry.from_api({"id": "x", "telemetry": {"battery": {"stateOfCharge": None}, "solar": None}})
  assert telemetry.battery_state_of_charge is None and telemetry.solar_power_kw is None

def test_mock_charge_pack():
  # (the account debug override mock_charge_pack: a battery and a plan to test with)
  device = get_mock_charge_pack_device()
  assert device.device_type == "INVERTERS" and device.make == "Sigenergy"

  now = _at("2026-10-22T14:10:00Z")
  read = mock_charge_pack_dispatches(now)
  assert current_activity(read.planned, now)[0] == "charging"
  assert [d.kind for d in read.planned] == ["charge", "idle", "discharge", "charge"]
  assert read.status.current_state == "SMART_CONTROL_CAPABLE"
  assert read.telemetry.battery_power_kw < 0 and read.telemetry.grid_power_kw > 0  # charging from the grid
