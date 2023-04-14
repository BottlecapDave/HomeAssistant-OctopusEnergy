import pytest

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.octopus_energy.intelligent import adjust_intelligent_rates

def create_rates():
  return [
    {
      "value_exc_vat": 9.111,
      "value_inc_vat": 9.11,
      "valid_from": as_utc(parse_datetime("2022-10-10T03:30:00Z")),
      "valid_to": as_utc(parse_datetime("2022-10-10T04:00:00Z"))
    },
    {
      "value_exc_vat": 30.1,
      "value_inc_vat": 30.1,
      "valid_from": as_utc(parse_datetime("2022-10-10T04:00:00Z")),
      "valid_to": as_utc(parse_datetime("2022-10-10T04:30:00Z"))
    },
    {
      "value_exc_vat": 30.1,
      "value_inc_vat": 30.1,
      "valid_from": as_utc(parse_datetime("2022-10-10T04:30:00Z")),
      "valid_to": as_utc(parse_datetime("2022-10-10T05:00:00Z"))
    },
    {
      "value_exc_vat": 30.1,
      "value_inc_vat": 30.1,
      "valid_from": as_utc(parse_datetime("2022-10-10T05:00:00Z")),
      "valid_to": as_utc(parse_datetime("2022-10-10T05:30:00Z"))
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
  planned_dispatches = [{
    "start": as_utc(parse_datetime("2022-10-10T05:00:00Z")),
    "end": as_utc(parse_datetime("2022-10-10T05:30:00Z")),
    "source": "smart-charge"
  }]
  complete_dispatches = []

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, complete_dispatches)

  # Assert
  for index, rate in enumerate(rates):
    if index == 3:
      assert rate["valid_from"] == adjusted_rates[index]["valid_from"]
      assert rate["valid_to"] == adjusted_rates[index]["valid_to"]
      assert off_peak == adjusted_rates[index]["value_inc_vat"]
      
    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_planned_non_smart_charge_dispatch_present_in_rate_then_rates_not_adjusted():
  # Arrange
  rates = create_rates()
  planned_dispatches = [{
    "start": as_utc(parse_datetime("2022-10-10T05:00:00Z")),
    "end": as_utc(parse_datetime("2022-10-10T05:30:00Z")),
    "source": "not-mart-charge"
  }]
  complete_dispatches = []

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, complete_dispatches)

  # Assert
  assert rates == adjusted_rates

@pytest.mark.asyncio
async def test_when_complete_smart_charge_dispatch_present_in_rate_then_rates_adjusted():
  # Arrange
  rates = create_rates()
  off_peak = rates[0]["value_inc_vat"]
  complete_dispatches = [{
    "start": as_utc(parse_datetime("2022-10-10T05:00:00Z")),
    "end": as_utc(parse_datetime("2022-10-10T05:30:00Z")),
    "source": "smart-charge"
  }]
  planned_dispatches = []

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, complete_dispatches)

  # Assert
  for index, rate in enumerate(rates):
    if index == 3:
      assert rate["valid_from"] == adjusted_rates[index]["valid_from"]
      assert rate["valid_to"] == adjusted_rates[index]["valid_to"]
      assert off_peak == adjusted_rates[index]["value_inc_vat"]
      
    else:
      assert rate == adjusted_rates[index]

@pytest.mark.asyncio
async def test_when_complete_non_smart_charge_dispatch_present_in_rate_then_rates_not_adjusted():
  # Arrange
  rates = create_rates()
  complete_dispatches = [{
    "start": as_utc(parse_datetime("2022-10-10T05:00:00Z")),
    "end": as_utc(parse_datetime("2022-10-10T05:30:00Z")),
    "source": "not-mart-charge"
  }]
  planned_dispatches = []

  # Act
  adjusted_rates = adjust_intelligent_rates(create_rates(), planned_dispatches, complete_dispatches)

  # Assert
  assert rates == adjusted_rates