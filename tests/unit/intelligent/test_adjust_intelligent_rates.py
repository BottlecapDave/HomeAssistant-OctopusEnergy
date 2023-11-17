import pytest

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.octopus_energy.intelligent import adjust_intelligent_rates
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatchItem

def create_rates():
  return [
    {
      "value_exc_vat": 9.111,
      "value_inc_vat": 9.11,
      "start": as_utc(parse_datetime("2022-10-10T03:30:00Z")),
      "end": as_utc(parse_datetime("2022-10-10T04:00:00Z"))
    },
    {
      "value_exc_vat": 30.1,
      "value_inc_vat": 30.1,
      "start": as_utc(parse_datetime("2022-10-10T04:00:00Z")),
      "end": as_utc(parse_datetime("2022-10-10T04:30:00Z"))
    },
    {
      "value_exc_vat": 30.1,
      "value_inc_vat": 30.1,
      "start": as_utc(parse_datetime("2022-10-10T04:30:00Z")),
      "end": as_utc(parse_datetime("2022-10-10T05:00:00Z"))
    },
    {
      "value_exc_vat": 30.1,
      "value_inc_vat": 30.1,
      "start": as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      "end": as_utc(parse_datetime("2022-10-10T05:30:00Z"))
    },
  ]

@pytest.mark.asyncio
async def test_when_no_planned_or_completed_dispatches_then_rates_not_adjusted():
  # Arrange
  rates = create_rates()
  planned_dispatches = []
  complete_dispatches = []

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, complete_dispatches)

  # Assert
  assert rates == adjusted_rates

@pytest.mark.asyncio
async def test_when_planned_smart_charge_dispatch_present_in_rate_then_rates_adjusted():
  # Arrange
  rates = create_rates()
  off_peak = rates[0]["value_inc_vat"]
  planned_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      as_utc(parse_datetime("2022-10-10T06:00:00Z")),
      1,
      "smart-charge",
      "home"
  )]
  complete_dispatches: list[IntelligentDispatchItem] = []

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, complete_dispatches)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if index == 3:
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert off_peak == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]
      
    else:
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
  complete_dispatches: list[IntelligentDispatchItem] = []

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, complete_dispatches)

  # Assert
  assert rates == adjusted_rates

@pytest.mark.asyncio
async def test_when_complete_smart_charge_dispatch_present_in_rate_then_rates_adjusted():
  # Arrange
  rates = create_rates()
  off_peak = rates[0]["value_inc_vat"]
  complete_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      as_utc(parse_datetime("2022-10-10T06:00:00Z")),
      1,
      "smart-charge",
      "home"
  )]
  planned_dispatches: list[IntelligentDispatchItem] = []

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, complete_dispatches)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if index == 3:
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert off_peak == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]
      
    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_complete_non_smart_charge_dispatch_present_in_rate_then_rates_adjusted():
  # Arrange
  rates = create_rates()
  off_peak = rates[0]["value_inc_vat"]
  complete_dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      as_utc(parse_datetime("2022-10-10T06:00:00Z")),
      1,
      "smart-charge",
      "home"
  )]
  planned_dispatches: list[IntelligentDispatchItem] = []

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, complete_dispatches)

  # Assert
  assert len(rates) == len(adjusted_rates)
  for index, rate in enumerate(rates):
    if index == 3:
      assert rate["start"] == adjusted_rates[index]["start"]
      assert rate["end"] == adjusted_rates[index]["end"]
      assert off_peak == adjusted_rates[index]["value_inc_vat"]
      assert True == adjusted_rates[index]["is_intelligent_adjusted"]
      
    else:
      assert rate == adjusted_rates[index]