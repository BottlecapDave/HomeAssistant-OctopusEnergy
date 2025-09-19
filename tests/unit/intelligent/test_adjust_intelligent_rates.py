import pytest

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.octopus_energy.intelligent import adjust_intelligent_rates
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatchItem, SimpleIntelligentDispatchItem
from tests.integration import create_rate_data
from custom_components.octopus_energy.const import CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY, CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

def create_rates():
  return [
    {
      "value_exc_vat": 9.111,
      "value_inc_vat": 9.11,
      "start": as_utc(parse_datetime("2022-10-10T03:30:00Z")),
      "end": as_utc(parse_datetime("2022-10-10T04:00:00Z")),
      "tariff_code": "E-1R-TARIFF-L"
    },
    {
      "value_exc_vat": 30.1,
      "value_inc_vat": 30.1,
      "start": as_utc(parse_datetime("2022-10-10T04:00:00Z")),
      "end": as_utc(parse_datetime("2022-10-10T04:30:00Z")),
      "tariff_code": "E-1R-TARIFF-L"
    },
    {
      "value_exc_vat": 30.1,
      "value_inc_vat": 30.1,
      "start": as_utc(parse_datetime("2022-10-10T04:30:00Z")),
      "end": as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      "tariff_code": "E-1R-TARIFF-L"
    },
    {
      "value_exc_vat": 30.1,
      "value_inc_vat": 30.1,
      "start": as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      "end": as_utc(parse_datetime("2022-10-10T05:30:00Z")),
      "tariff_code": "E-1R-TARIFF-L"
    },
  ]

@pytest.mark.asyncio
async def test_when_rates_empty_then_empty_rates_returned():
  # Arrange
  rates = []
  planned_dispatches = []
  started_dispatches = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates, planned_dispatches, started_dispatches, mode)

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
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, started_dispatches, mode)

  # Assert
  assert rates == adjusted_rates

@pytest.mark.asyncio
@pytest.mark.parametrize("intelligent_start,intelligent_end",[
  (as_utc(parse_datetime("2022-10-10T05:00:00Z")), as_utc(parse_datetime("2022-10-10T06:00:00Z"))),
  (as_utc(parse_datetime("2022-10-10T05:00:01Z")), as_utc(parse_datetime("2022-10-10T06:00:00Z"))),
  (as_utc(parse_datetime("2022-10-10T05:00:00Z")), as_utc(parse_datetime("2022-10-10T05:29:59Z")))
])
async def test_when_planned_smart_charge_dispatch_present_in_rate_then_rates_adjusted(intelligent_start, intelligent_end):
  # Arrange
  rates = create_rates()
  off_peak = rates[0]["value_inc_vat"]
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
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if index == 3:
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]
      
    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_planned_smart_charge_dispatch_spans_multiple_rates_then_rates_adjusted():
  # Arrange
  rates = create_rates()
  off_peak = rates[0]["value_inc_vat"]
  planned_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T04:00:00Z")),
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      1,
      "smart-charge",
      "home"
  )]
  started_dispatches: list[SimpleIntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if index == 1 or index == 2:
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]
      
    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_planned_smart_charge_dispatch_spans_two_parts_then_rates_adjusted():
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
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(rates.copy(), planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if rate["start"] >= as_utc(parse_datetime("2022-10-10T21:30:00Z")) and rate["end"] <= as_utc(parse_datetime("2022-10-10T23:30:00Z")):
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak == adjusted_rates[index]["value_inc_vat"]
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
  adjusted_rates = adjust_intelligent_rates(rates.copy(), planned_dispatches, started_dispatches, mode)

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
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, started_dispatches, mode)

  # Assert
  assert rates == adjusted_rates

@pytest.mark.asyncio
@pytest.mark.parametrize("intelligent_start,intelligent_end",[
  (as_utc(parse_datetime("2022-10-10T05:00:00Z")), as_utc(parse_datetime("2022-10-10T06:00:00Z"))),
  (as_utc(parse_datetime("2022-10-10T05:00:01Z")), as_utc(parse_datetime("2022-10-10T06:00:00Z"))), # Start is during rate
  (as_utc(parse_datetime("2022-10-10T05:00:00Z")), as_utc(parse_datetime("2022-10-10T05:29:59Z"))) # End is during rate
])
async def test_when_complete_smart_charge_dispatch_present_in_rate_then_rates_adjusted(intelligent_start, intelligent_end):
  # Arrange
  rates = create_rates()
  off_peak = rates[0]["value_inc_vat"]
  started_dispatches: list[SimpleIntelligentDispatchItem] = [
    SimpleIntelligentDispatchItem(
      intelligent_start,
      intelligent_end
  )]
  planned_dispatches: list[IntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if index == 3:
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]
      
    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_complete_non_smart_charge_dispatch_present_in_rate_then_rates_adjusted():
  # Arrange
  rates = create_rates()
  off_peak = rates[0]["value_inc_vat"]
  started_dispatches: list[SimpleIntelligentDispatchItem] = [
    SimpleIntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      as_utc(parse_datetime("2022-10-10T06:00:00Z"))
  )]
  planned_dispatches: list[IntelligentDispatchItem] = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if index == 3:
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert rate["tariff_code"] == adjusted_rates[index]["tariff_code"]
      assert off_peak == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]
      
    else:
      assert rate == adjusted_rates[index]