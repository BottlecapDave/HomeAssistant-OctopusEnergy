from custom_components.octopus_energy.const import EVENT_TARGET_TIMEFRAME_UPDATE_DATA_SOURCE


def assert_raised_target_timeframe_update_event(raised_events: dict, expected_rates: list, expected_serial_number: str, expected_mpan_or_mprn: str):
  assert EVENT_TARGET_TIMEFRAME_UPDATE_DATA_SOURCE in raised_events
  assert "data_source_id" in raised_events[EVENT_TARGET_TIMEFRAME_UPDATE_DATA_SOURCE]
  assert raised_events[EVENT_TARGET_TIMEFRAME_UPDATE_DATA_SOURCE]["data_source_id"] == f"octopus_energy_{expected_mpan_or_mprn}_{expected_serial_number}"
  assert "data" in raised_events[EVENT_TARGET_TIMEFRAME_UPDATE_DATA_SOURCE]
  assert len(raised_events[EVENT_TARGET_TIMEFRAME_UPDATE_DATA_SOURCE]["data"]) == len(expected_rates)

  for (index, rate) in enumerate(expected_rates):
    assert raised_events[EVENT_TARGET_TIMEFRAME_UPDATE_DATA_SOURCE]["data"][index]["start"] == rate["start"]
    assert raised_events[EVENT_TARGET_TIMEFRAME_UPDATE_DATA_SOURCE]["data"][index]["end"] == rate["end"]
    assert raised_events[EVENT_TARGET_TIMEFRAME_UPDATE_DATA_SOURCE]["data"][index]["value"] == round(rate["value_inc_vat"] / 100, 6)