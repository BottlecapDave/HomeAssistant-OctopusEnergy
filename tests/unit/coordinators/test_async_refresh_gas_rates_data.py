from datetime import datetime, timedelta
import pytest
import mock

from unit import (create_rate_data)

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.coordinators.gas_rates import GasRatesCoordinatorResult, async_refresh_gas_rates_data
from custom_components.octopus_energy.const import EVENT_GAS_CURRENT_DAY_RATES, EVENT_GAS_NEXT_DAY_RATES, EVENT_GAS_PREVIOUS_DAY_RATES

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
period_from = datetime.strptime("2023-07-14T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
period_to = datetime.strptime("2023-07-15T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"
mprn = "1234567890"
serial_number = "abcdefgh"

def get_account_info(is_active_agreement = True):
  return {
    "gas_meter_points": [
      {
        "mprn": mprn,
        "meters": [
          {
            "serial_number": serial_number,
            "is_export": False,
            "is_smart_meter": True,
            "device_id": "",
            "manufacturer": "",
            "model": "",
            "firmware": ""
          }
        ],
        "agreements": [
          {
            "valid_from": "2023-07-01T00:00:00+01:00" if is_active_agreement else "2023-08-01T00:00:00+01:00",
            "valid_to": "2023-08-01T00:00:00+01:00" if is_active_agreement else "2023-09-01T00:00:00+01:00",
            "tariff_code": tariff_code,
            "product": "SUPER-GREEN-24M-21-07-30"
          }
        ]
      }
    ]
  }

def assert_raised_events(raised_events: dict, expected_event_name: str, expected_valid_from: datetime, expected_valid_to: datetime):
  assert expected_event_name in raised_events
  assert "mprn" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["mprn"] == mprn
  assert "serial_number" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["serial_number"] == serial_number
  assert "rates" in raised_events[expected_event_name]
  assert len(raised_events[expected_event_name]["rates"]) > 2
  assert "valid_from" in raised_events[expected_event_name]["rates"][0]
  assert raised_events[expected_event_name]["rates"][0]["valid_from"] == expected_valid_from
  assert "valid_to" in raised_events[expected_event_name]["rates"][-1]
  assert raised_events[expected_event_name]["rates"][-1]["valid_to"] == expected_valid_to

@pytest.mark.asyncio
async def test_when_account_info_is_none_then_existing_rates_returned():
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  rates_returned = False
  async def async_mocked_get_gas_rates(*args, **kwargs):
    nonlocal rates_returned
    rates_returned = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  account_info = None
  existing_rates = GasRatesCoordinatorResult(period_from, create_rate_data(period_from, period_to, [2, 4]))

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_rates=async_mocked_get_gas_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_gas_rates_data(
      current,
      client,
      account_info,
      mprn,
      serial_number,
      existing_rates,
      fire_event
    )

    assert retrieved_rates == existing_rates
    assert rates_returned == False
    assert len(actual_fired_events.keys()) == 0

@pytest.mark.asyncio
async def test_when_no_active_rates_then_none_returned():
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  rates_returned = False
  async def async_mocked_get_gas_rates(*args, **kwargs):
    nonlocal rates_returned
    rates_returned = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  account_info = get_account_info(False)
  existing_rates = GasRatesCoordinatorResult(period_from, create_rate_data(period_from, period_to, [2, 4]))

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_rates=async_mocked_get_gas_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_gas_rates_data(
      current,
      client,
      account_info,
      mprn,
      serial_number,
      existing_rates,
      fire_event
    )

    assert retrieved_rates == None
    assert rates_returned == False
    assert len(actual_fired_events.keys()) == 0

@pytest.mark.asyncio
async def test_when_current_is_not_thirty_minutes_then_existing_rates_returned():
  for minute in range(60):
    if minute == 0 or minute == 30:
      continue

    current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z").replace(minute=minute)
    expected_rates = create_rate_data(period_from, period_to, [1, 2])
    rates_returned = False
    async def async_mocked_get_gas_rates(*args, **kwargs):
      nonlocal rates_returned
      rates_returned = True
      return expected_rates
    
    actual_fired_events = {}
    def fire_event(name, metadata):
      nonlocal actual_fired_events
      actual_fired_events[name] = metadata
      return None
    
    account_info = get_account_info()
    existing_rates = GasRatesCoordinatorResult(period_from, create_rate_data(period_from, period_to, [2, 4]))

    with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_rates=async_mocked_get_gas_rates):
      client = OctopusEnergyApiClient("NOT_REAL")
      retrieved_rates = await async_refresh_gas_rates_data(
        current,
        client,
        account_info,
        mprn,
        serial_number,
        existing_rates,
        fire_event
      )

      assert retrieved_rates == existing_rates
      assert rates_returned == False
      assert len(actual_fired_events.keys()) == 0

@pytest.mark.asyncio
async def test_when_existing_rates_is_none_then_rates_retrieved():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2])
  rates_returned = False
  requested_period_from = None
  requested_period_to = None
  async def async_mocked_get_gas_rates(*args, **kwargs):
    nonlocal requested_period_from, requested_period_to, rates_returned

    requested_client, requested_tariff_code, requested_period_from, requested_period_to = args
    rates_returned = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  account_info = get_account_info()
  existing_rates = None
  expected_retrieved_rates = GasRatesCoordinatorResult(current, expected_rates)

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_rates=async_mocked_get_gas_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_gas_rates_data(
      current,
      client,
      account_info,
      mprn,
      serial_number,
      existing_rates,
      fire_event
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_retrieved == expected_retrieved_rates.last_retrieved
    assert retrieved_rates.rates == expected_retrieved_rates.rates
    assert rates_returned == True
    assert requested_period_from == expected_period_from
    assert requested_period_to == expected_period_to
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_GAS_PREVIOUS_DAY_RATES, requested_period_from, requested_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_GAS_CURRENT_DAY_RATES, requested_period_from + timedelta(days=1), requested_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_GAS_NEXT_DAY_RATES, requested_period_from + timedelta(days=2), requested_period_from + timedelta(days=3))
  

@pytest.mark.asyncio
async def test_when_existing_rates_is_old_then_rates_retrieved():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2])
  rates_returned = False
  async def async_mocked_get_gas_rates(*args, **kwargs):
    nonlocal rates_returned
    rates_returned = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  account_info = get_account_info()
  existing_rates = GasRatesCoordinatorResult(period_from, create_rate_data(period_from - timedelta(days=60), period_to - timedelta(days=60), [2, 4]))
  expected_retrieved_rates = GasRatesCoordinatorResult(current, expected_rates)

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_rates=async_mocked_get_gas_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_gas_rates_data(
      current,
      client,
      account_info,
      mprn,
      serial_number,
      existing_rates,
      fire_event
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_retrieved == expected_retrieved_rates.last_retrieved
    assert retrieved_rates.rates == expected_retrieved_rates.rates
    assert rates_returned == True
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_GAS_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_GAS_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_GAS_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))

@pytest.mark.asyncio
async def test_when_rates_not_retrieved_then_existing_rates_returned():
  expected_rates = create_rate_data(period_from, period_to, [1, 2, 3, 4])
  rates_returned = False
  async def async_mocked_get_gas_rates(*args, **kwargs):
    nonlocal rates_returned
    rates_returned = True
    return None
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  account_info = get_account_info()
  existing_rates = GasRatesCoordinatorResult(period_from, expected_rates)

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_rates=async_mocked_get_gas_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_gas_rates_data(
      current,
      client,
      account_info,
      mprn,
      serial_number,
      existing_rates,
      fire_event
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_retrieved == existing_rates.last_retrieved
    assert retrieved_rates.rates == existing_rates.rates
    assert rates_returned == True
    assert len(actual_fired_events.keys()) == 0