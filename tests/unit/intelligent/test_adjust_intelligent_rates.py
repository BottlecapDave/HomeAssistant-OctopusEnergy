
import pytest
from datetime import timedelta

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.octopus_energy.intelligent import adjust_intelligent_rates
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatchItem, SimpleIntelligentDispatchItem
from tests.integration import create_rate_data
from custom_components.octopus_energy.const import CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY, CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

off_peak_rate = 9.11

def create_rates():
  rates = []
  rates.extend(create_rate_data(
    parse_datetime("2022-10-09T12:00:00Z"),
    parse_datetime("2022-10-09T23:30:00Z"),
    [30.1]
  ))
  rates.extend(create_rate_data(
    parse_datetime("2022-10-09T23:30:00Z"),
    parse_datetime("2022-10-10T05:30:00Z"),
    [off_peak_rate]
  ))
  rates.extend(create_rate_data(
    parse_datetime("2022-10-10T05:30:00Z"),
    parse_datetime("2022-10-10T12:00:00Z"),
    [30.1]
  ))
  return rates

@pytest.mark.asyncio
async def test_when_rates_empty_then_empty_rates_returned():
  # Arrange
  rates = []
  planned_dispatches = []
  started_dispatches = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode)

  # Assert
  assert rates == adjusted_rates

@pytest.mark.asyncio
async def test_when_no_planned_or_completed_dispatches_then_rates_not_adjusted():
  # Arrange
  rates = create_rates()
  planned_dispatches = []
  started_dispatches = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode)

  # Assert
  assert rates == adjusted_rates

@pytest.mark.asyncio
@pytest.mark.parametrize("intelligent_start,intelligent_end,expected_adjusted_rate_start",[
  (as_utc(parse_datetime("2022-10-10T05:30:00Z")), as_utc(parse_datetime("2022-10-10T06:00:00Z")), as_utc(parse_datetime("2022-10-10T05:30:00Z"))),
  (as_utc(parse_datetime("2022-10-10T05:30:01Z")), as_utc(parse_datetime("2022-10-10T06:00:00Z")), as_utc(parse_datetime("2022-10-10T05:30:00Z"))),
  (as_utc(parse_datetime("2022-10-10T05:30:00Z")), as_utc(parse_datetime("2022-10-10T05:59:59Z")), as_utc(parse_datetime("2022-10-10T05:30:00Z")))
])
async def test_when_planned_smart_charge_dispatch_present_in_rate_then_rates_adjusted(intelligent_start, intelligent_end, expected_adjusted_rate_start):
  # Arrange
  rates = create_rates()
  planned_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      intelligent_start,
      intelligent_end,
      1,
      "smart-charge",
      "home"
  )]
  started_dispatches: list[SimpleIntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if rate["start"] == expected_adjusted_rate_start:
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak_rate == adjusted_rates[index]["value_inc_vat"]
      assert "is_intelligent_adjusted" in adjusted_rates[index]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]

    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_planned_smart_charge_dispatch_spans_multiple_rates_then_rates_adjusted():
  # Arrange
  rates = create_rates()
  planned_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T06:00:00Z")),
      as_utc(parse_datetime("2022-10-10T07:00:00Z")),
      1,
      "smart-charge",
      "home"
  )]
  started_dispatches: list[SimpleIntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if rate["start"] >= as_utc(parse_datetime("2022-10-10T06:00:00Z")) and rate["end"] <= as_utc(parse_datetime("2022-10-10T07:00:00Z")):
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak_rate == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]

    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_planned_smart_charge_dispatch_spans_two_parts_then_rates_adjusted():
  # Arrange
  rates = (
    create_rate_data(as_utc(parse_datetime("2022-10-10T20:00:00Z")), as_utc(parse_datetime("2022-10-10T23:30:00Z")), [30.1]) +
    create_rate_data(as_utc(parse_datetime("2022-10-10T23:30:00Z")), as_utc(parse_datetime("2022-10-11T04:30:00Z")), [off_peak_rate]) +
    create_rate_data(as_utc(parse_datetime("2022-10-11T04:30:00Z")), as_utc(parse_datetime("2022-10-11T05:30:00Z")), [30.1])
  )
  planned_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T21:30:00Z")),
      as_utc(parse_datetime("2022-10-10T22:00:00Z")),
      1,
      "smart-charge",
      "home"
    ),
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T22:00:00Z")),
      as_utc(parse_datetime("2022-10-11T04:00:00Z")),
      1,
      None,
      "home"
    )
  ]
  started_dispatches: list[SimpleIntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode)
  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if rate["start"] >= as_utc(parse_datetime("2022-10-10T21:30:00Z")) and rate["end"] <= as_utc(parse_datetime("2022-10-10T23:30:00Z")):
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak_rate == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]

    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_planned_smart_charge_dispatch_spans_two_parts_and_started_only_mode_then_rates_not_adjusted():
  # Arrange
  rates = (
    create_rate_data(as_utc(parse_datetime("2022-10-10T20:00:00Z")), as_utc(parse_datetime("2022-10-10T23:30:00Z")), [30.1]) +
    create_rate_data(as_utc(parse_datetime("2022-10-10T23:30:00Z")), as_utc(parse_datetime("2022-10-11T04:30:00Z")), [9.12]) +
    create_rate_data(as_utc(parse_datetime("2022-10-11T04:30:00Z")), as_utc(parse_datetime("2022-10-11T05:30:00Z")), [30.1])
  )
  off_peak = 9.12
  planned_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T21:30:00Z")),
      as_utc(parse_datetime("2022-10-10T22:00:00Z")),
      1,
      "smart-charge",
      "home"
    ),
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T22:00:00Z")),
      as_utc(parse_datetime("2022-10-11T04:00:00Z")),
      1,
      None,
      "home"
    )
  ]
  started_dispatches: list[SimpleIntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_planned_non_smart_charge_dispatch_present_in_rate_then_rates_not_adjusted():
  # Arrange
  rates = create_rates()
  planned_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      as_utc(parse_datetime("2022-10-10T06:00:00Z")),
      1,
      "non-smart-charge",
      "home"
  )]
  started_dispatches: list[SimpleIntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode)

  # Assert
  assert rates == adjusted_rates

@pytest.mark.asyncio
@pytest.mark.parametrize("intelligent_start,intelligent_end,expected_adjusted_rate_start",[
  (as_utc(parse_datetime("2022-10-10T05:00:00Z")), as_utc(parse_datetime("2022-10-10T06:00:00Z")), as_utc(parse_datetime("2022-10-10T05:30:00Z"))),
  (as_utc(parse_datetime("2022-10-10T05:00:01Z")), as_utc(parse_datetime("2022-10-10T06:00:00Z")), as_utc(parse_datetime("2022-10-10T05:30:00Z"))), # Start is during rate
  # Dispatch stays within the already off-peak period (23:30 - 05:30), so nothing needs adjusting
  (as_utc(parse_datetime("2022-10-10T05:30:00Z")), as_utc(parse_datetime("2022-10-10T05:59:59Z")), as_utc(parse_datetime("2022-10-10T05:30:00Z"))) # End is during rate
])
async def test_when_complete_smart_charge_dispatch_present_in_rate_then_rates_adjusted(intelligent_start, intelligent_end, expected_adjusted_rate_start):
  # Arrange
  rates = create_rates()
  started_dispatches: list[SimpleIntelligentDispatchItem] = [
    SimpleIntelligentDispatchItem(
      intelligent_start,
      intelligent_end
  )]
  planned_dispatches: list[IntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if rate["start"] == expected_adjusted_rate_start:
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak_rate == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]

    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_complete_non_smart_charge_dispatch_present_in_rate_then_rates_adjusted():
  # Arrange
  rates = create_rates()
  started_dispatches: list[SimpleIntelligentDispatchItem] = [
    SimpleIntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      as_utc(parse_datetime("2022-10-10T06:00:00Z"))
  )]
  planned_dispatches: list[IntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if rate["start"] == as_utc(parse_datetime("2022-10-10T05:30:00Z")):
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak_rate == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]

    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_complete_non_smart_charge_dispatch_present_in_rate_but_below_minimum_dispatch_period_then_rates_not_adjusted():
  # Arrange
  rates = create_rates()
  started_dispatches: list[SimpleIntelligentDispatchItem] = [
    SimpleIntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      as_utc(parse_datetime("2022-10-10T05:02:59Z"))
  )]
  planned_dispatches: list[IntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES
  minimum_dispatch_in_minutes = 3

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode, minimum_dispatch_in_minutes)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    assert rate == adjusted_rates[index]
    assert "is_intelligent_adjusted" not in adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_enforce_cap_is_true_and_dispatch_hours_are_within_cap_then_rates_adjusted():
  # Arrange
  rates = create_rates()
  planned_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      as_utc(parse_datetime("2022-10-10T06:00:00Z")),
      1,
      "smart-charge",
      "home"
  )]
  started_dispatches: list[SimpleIntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode, 0, True)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if rate["start"] == as_utc(parse_datetime("2022-10-10T05:30:00Z")):
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak_rate == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]

    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_enforce_cap_is_true_and_dispatch_hours_exceed_cap_then_only_rates_within_cap_are_adjusted():
  # Arrange
  rates = create_rates()
  # A started dispatch and a planned dispatch totalling 8 hours, more than the 6 hour daily cap
  planned_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      as_utc(parse_datetime("2022-10-10T08:00:00Z")),
      1,
      "smart-charge",
      "home"
    )
  ]
  started_dispatches: list[SimpleIntelligentDispatchItem] = [
    SimpleIntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-09T23:00:00Z")),
      as_utc(parse_datetime("2022-10-10T04:00:00Z"))
    )
  ]
  started_actual_dispatches: list[SimpleIntelligentDispatchItem] = [
    SimpleIntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-09T23:00:00Z")),
      as_utc(parse_datetime("2022-10-10T04:00:00Z"))
    )
  ]
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, started_actual_dispatches, mode, 0, True)

  # Assert
  # Only the 23:00 - 23:30 and 05:30 - 06:00 rate is adjusted;
  # the 23:30 - 05:30 off-peak rate is not adjusted because its already off peak
  # the 06:00 onwards is not adjusted because the cap has already been exceeded
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if rate["start"] == as_utc(parse_datetime("2022-10-09T23:00:00Z")) or rate["start"] == as_utc(parse_datetime("2022-10-10T05:30:00Z")):
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak_rate == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]

    else:
      assert rate == adjusted_rates[index]
      assert "is_intelligent_adjusted" not in adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_enforce_cap_is_false_and_dispatch_hours_exceed_cap_then_rates_still_adjusted():
  # Arrange
  rates = create_rates()
  planned_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-09T22:00:00Z")),
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      1,
      "smart-charge",
      "home"
  )]
  started_dispatches: list[SimpleIntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, [], mode, 0, False)

  # Assert
  # The cap is ignored entirely when enforce_cap is false (the default), so the peak rates the dispatch
  # covers before the off-peak period starts (22:00 - 23:30) are adjusted as normal
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if rate["start"] >= as_utc(parse_datetime("2022-10-09T22:00:00Z")) and rate["end"] <= as_utc(parse_datetime("2022-10-09T23:30:00Z")):
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak_rate == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]

    else:
      assert rate == adjusted_rates[index]
@pytest.mark.asyncio
@pytest.mark.parametrize("is_actual_dispatch_whole_period,expected_last_adjusted_rate_end",[
  # Actual started dispatches total 6.5 hours, so the cap is exceeded for the last period
  (True, as_utc(parse_datetime("2022-10-09T18:00:00Z"))),
  # Actual started dispatches total 4h20m, so the cap is not exceeded even though the rounded started dispatches total 6.5 hours
  (False, as_utc(parse_datetime("2022-10-09T18:30:00Z"))),
])
async def test_when_enforce_cap_is_true_then_cap_is_based_on_actual_started_dispatches(is_actual_dispatch_whole_period: bool, expected_last_adjusted_rate_end):
  # Arrange
  rates = create_rates()
  planned_dispatches: list[IntelligentDispatchItem] = []
  started_dispatches: list[SimpleIntelligentDispatchItem] = [
    SimpleIntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-09T12:00:00Z")),
      as_utc(parse_datetime("2022-10-09T18:30:00Z"))
    )
  ]

  # Either the whole period, or 20 minutes of dispatching within each of the rounded 30 minute periods
  started_actual_dispatches: list[SimpleIntelligentDispatchItem] = started_dispatches.copy() if is_actual_dispatch_whole_period else []
  for index in range(0 if is_actual_dispatch_whole_period else 13):
    period_start = as_utc(parse_datetime("2022-10-09T12:00:00Z")) + timedelta(minutes=30 * index)
    started_actual_dispatches.append(SimpleIntelligentDispatchItem(
      period_start + timedelta(minutes=5),
      period_start + timedelta(minutes=25)
    ))
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates,
                                            planned_dispatches,
                                            started_dispatches,
                                            started_actual_dispatches,
                                            mode,
                                            0,
                                            True)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if rate["end"] <= expected_last_adjusted_rate_end:
      assert off_peak_rate == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]
    elif rate["value_inc_vat"] != off_peak_rate:
      assert rate == adjusted_rates[index]
      assert "is_intelligent_adjusted" not in adjusted_rates[index]
