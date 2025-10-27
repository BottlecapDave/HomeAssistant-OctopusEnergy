from datetime import datetime, timedelta
from custom_components.octopus_energy.storage.intelligent_dispatches_history import IntelligentDispatchesHistory
import pytest
import mock

from unit import (create_rate_data)

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.coordinators.electricity_rates import ElectricityRatesCoordinatorResult, async_refresh_electricity_rates_data
from custom_components.octopus_energy.const import EVENT_ELECTRICITY_CURRENT_DAY_RATES, EVENT_ELECTRICITY_NEXT_DAY_RATES, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, REFRESH_RATE_IN_MINUTES_RATES
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatchItem, IntelligentDispatches, SimpleIntelligentDispatchItem
from custom_components.octopus_energy.api_client.intelligent_device import IntelligentDevice
from custom_components.octopus_energy.coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult
from zoneinfo import ZoneInfo

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
period_from = datetime.strptime("2023-07-14T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
period_to = datetime.strptime("2023-07-15T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
dispatches_last_retrieved = datetime.strptime("2023-07-14T10:00:01+01:00", "%Y-%m-%dT%H:%M:%S%z")

mpan = "1234567890"
serial_number = "abcdefgh"
default_tariff_code = "E-1R-SUPER-GREEN-24M-21-07-30-A"
default_product_code = "SUPER-GREEN-24M-21-07-30"

def get_account_info(is_active_agreement = True, tariff_code = default_tariff_code, product_code = "SUPER-GREEN-24M-21-07-30"):
  return {
    "electricity_meter_points": [
      {
        "mpan": mpan,
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
            "start": "2023-07-01T00:00:00+01:00" if is_active_agreement else "2023-08-01T00:00:00+01:00",
            "end": "2025-08-01T00:00:00+01:00" if is_active_agreement else "2023-09-01T00:00:00+01:00",
            "tariff_code": tariff_code,
            "product_code": product_code
          }
        ]
      }
    ]
  }

def assert_raised_events(raised_events: dict, expected_event_name: str, expected_valid_from: datetime, expected_valid_to: datetime):
  assert expected_event_name in raised_events
  assert "mpan" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["mpan"] == mpan
  assert "serial_number" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["serial_number"] == serial_number
  assert "rates" in raised_events[expected_event_name]
  assert len(raised_events[expected_event_name]["rates"]) > 2
  assert "start" in raised_events[expected_event_name]["rates"][0]
  assert raised_events[expected_event_name]["rates"][0]["start"] == expected_valid_from
  assert "end" in raised_events[expected_event_name]["rates"][-1]
  assert raised_events[expected_event_name]["rates"][-1]["end"] == expected_valid_to

  # Make sure all rates are in order
  expected_start = expected_valid_from
  for rate in raised_events[expected_event_name]["rates"]:
    assert rate["start"] == expected_start

    expected_end = expected_start + timedelta(minutes=30)
    assert rate["end"] == expected_end
    expected_start = expected_end

  rates: list = raised_events[expected_event_name]["rates"]
  rates.sort(key=lambda rate: rate["value_inc_vat"])
  expected_min_rate = rates[0]["value_inc_vat"]
  rates.sort(key=lambda rate: rate["value_inc_vat"], reverse=True)
  expected_max_rate = rates[0]["value_inc_vat"]
  expected_average = sum(map(lambda rate: rate["value_inc_vat"], rates)) / len(rates)
  
  assert "min_rate" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["min_rate"] == expected_min_rate
  assert "max_rate" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["max_rate"] == expected_max_rate
  assert "average_rate" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["average_rate"] == round(expected_average, 8)

@pytest.mark.asyncio
async def test_when_account_info_is_none_then_existing_rates_returned():
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = None
  existing_rates = ElectricityRatesCoordinatorResult(period_from, 1, create_rate_data(period_from, period_to, [2, 4]))
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates == existing_rates
    assert mock_api_called == False
    assert raise_no_active_tariff_called == False
    assert len(actual_fired_events.keys()) == 0
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
async def test_when_no_active_rates_then_none_returned():
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info(False)
  existing_rates = ElectricityRatesCoordinatorResult(period_from, 1, create_rate_data(period_from, period_to, [2, 4]))
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is None
    assert mock_api_called == False
    assert raise_no_active_tariff_called == True
    raise_no_active_tariff_called == True
    assert len(actual_fired_events.keys()) == 0
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_then_existing_rates_returned():
  current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(current - timedelta(minutes=4, seconds=59), 1, create_rate_data(period_from, period_to, [2, 4]))
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates == existing_rates
    assert mock_api_called == False
    assert raise_no_active_tariff_called == False
    assert len(actual_fired_events.keys()) == 0
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
@pytest.mark.parametrize("existing_rates",[
  (None),
  (ElectricityRatesCoordinatorResult(period_from, 1, [])),
  (ElectricityRatesCoordinatorResult(period_from, 1, None)),
])
async def test_when_existing_rates_is_none_then_rates_retrieved(existing_rates):
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2])
  expected_rates_unsorted = expected_rates.copy()
  
  # Put rates into reverse order to make sure sorting works
  expected_rates.sort(key=lambda rate: (rate["start"].timestamp(), rate["start"].fold), reverse=True)

  assert expected_rates[-1]["start"] == expected_period_from
  assert expected_rates[0]["end"] == expected_period_to
  
  mock_api_called = False
  requested_period_from = None
  requested_period_to = None
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal requested_period_from, requested_period_to, mock_api_called, expected_rates

    requested_client, requested_product_code, requested_tariff_code, is_smart_meter, requested_period_from, requested_period_to = args
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, expected_rates_unsorted)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.rates == expected_retrieved_rates.rates
    assert retrieved_rates.original_rates == expected_retrieved_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted
    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    assert requested_period_from == expected_period_from
    assert requested_period_to == expected_period_to
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, requested_period_from, requested_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, requested_period_from + timedelta(days=1), requested_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, requested_period_from + timedelta(days=2), requested_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True
  
@pytest.mark.asyncio
@pytest.mark.parametrize("dispatches_result",[
  (None),
  (IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, None, IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved)),
  (IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", None, []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved)),
  (IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], None), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved)),
])
async def test_when_dispatches_is_not_defined_and_existing_rates_is_none_then_rates_retrieved(dispatches_result):
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2])
  expected_rates_unsorted = expected_rates.copy()
  
  # Put rates into reverse order to make sure sorting works
  expected_rates.sort(key=lambda rate: (rate["start"].timestamp(), rate["start"].fold), reverse=True)

  assert expected_rates[-1]["start"] == expected_period_from
  assert expected_rates[0]["end"] == expected_period_to
  
  mock_api_called = False
  requested_period_from = None
  requested_period_to = None
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal requested_period_from, requested_period_to, mock_api_called, expected_rates

    requested_client, requested_product_code, requested_tariff_code, is_smart_meter, requested_period_from, requested_period_to = args
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, expected_rates_unsorted)
  existing_rates = None

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      { "1": dispatches_result },
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.rates == expected_retrieved_rates.rates
    assert retrieved_rates.original_rates == expected_retrieved_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted
    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    assert requested_period_from == expected_period_from
    assert requested_period_to == expected_period_to
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, requested_period_from, requested_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, requested_period_from + timedelta(days=1), requested_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, requested_period_from + timedelta(days=2), requested_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True

@pytest.mark.asyncio
async def test_when_existing_rates_is_old_then_rates_retrieved():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2])
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(period_to - timedelta(days=60), 1, create_rate_data(period_from - timedelta(days=60), period_to - timedelta(days=60), [2, 4]))
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, expected_rates)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES)
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.rates == expected_retrieved_rates.rates
    assert retrieved_rates.original_rates == expected_retrieved_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted
    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True

@pytest.mark.asyncio
async def test_when_existing_rates_are_requested_period_and_same_tariff_then_existing_rates_used():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return []
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(period_to - timedelta(days=1), 1, create_rate_data(expected_period_from, expected_period_to, [2, 4], default_tariff_code))
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, existing_rates.rates)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES)
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.rates == expected_retrieved_rates.rates
    assert retrieved_rates.original_rates == expected_retrieved_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted
    assert mock_api_called == False
    assert raise_no_active_tariff_called == False
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True

@pytest.mark.asyncio
async def test_when_existing_rates_are_requested_period_and_different_tariff_then_existing_rates_not_used():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  mock_api_called = False
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [2], default_tariff_code)
  requested_period_from = None
  requested_period_to = None
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called, requested_period_from, requested_period_to

    requested_client, requested_product_code, requested_tariff_code, is_smart_meter, requested_period_from, requested_period_to = args

    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(period_to - timedelta(days=1), 1, create_rate_data(expected_period_from, expected_period_to, [2, 4], f"{default_tariff_code}-diff"))
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, existing_rates.rates)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES)
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.rates == expected_rates
    assert retrieved_rates.original_rates == expected_rates
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted
    assert mock_api_called == True
    assert raise_no_active_tariff_called == False

    assert requested_period_from == expected_period_from
    assert requested_period_to == expected_period_to
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True

@pytest.mark.asyncio
async def test_when_existing_rates_contains_some_of_period_and_same_tariff_then_partial_rates_retrieved():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from + timedelta(hours=20), expected_period_to, [2])
  mock_api_called = False
  requested_period_from = None
  requested_period_to = None
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called, requested_period_from, requested_period_to

    requested_client, requested_product_code, requested_tariff_code, is_smart_meter, requested_period_from, requested_period_to = args

    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(period_to - timedelta(days=60), 1, create_rate_data(expected_period_from, expected_rates[0]["start"], [1], default_tariff_code))
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, expected_rates)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES)
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted
    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True

    assert requested_period_from == existing_rates.rates[-1]["end"]
    assert requested_period_to == expected_period_to

    current_period_from = expected_period_from
    for rate in retrieved_rates.rates:
      assert rate["start"] == current_period_from
      current_period_from = current_period_from + timedelta(minutes=30)
      assert rate["end"] == current_period_from

      if rate["start"] < existing_rates.rates[-1]["end"]:
        assert rate["value_inc_vat"] == existing_rates.rates[-1]["value_inc_vat"]
      else:
        assert rate["value_inc_vat"] == expected_retrieved_rates.rates[-1]["value_inc_vat"]

    current_period_from = expected_period_from
    for rate in retrieved_rates.original_rates:
      assert rate["start"] == current_period_from
      current_period_from = current_period_from + timedelta(minutes=30)
      assert rate["end"] == current_period_from

      if rate["start"] < existing_rates.original_rates[-1]["end"]:
        assert rate["value_inc_vat"] == existing_rates.original_rates[-1]["value_inc_vat"]
      else:
        assert rate["value_inc_vat"] == expected_retrieved_rates.original_rates[-1]["value_inc_vat"]

@pytest.mark.asyncio
async def test_when_existing_rates_contains_some_of_period_and_different_tariff_then_full_rates_retrieved():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [2], default_tariff_code)
  mock_api_called = False
  requested_period_from = None
  requested_period_to = None
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called, requested_period_from, requested_period_to

    requested_client, requested_product_code, requested_tariff_code, is_smart_meter, requested_period_from, requested_period_to = args

    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(period_to - timedelta(days=60), 1, create_rate_data(expected_period_from, expected_rates[0]["start"], [1], f"{default_tariff_code}-new"))
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, expected_rates)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES)
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted
    assert retrieved_rates.rates == expected_rates
    assert retrieved_rates.original_rates == expected_rates
    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True

    assert requested_period_from == expected_period_from
    assert requested_period_to == expected_period_to

@pytest.mark.asyncio
@pytest.mark.parametrize("is_export_meter",[
  (True),
  (False),
])
async def test_when_dispatched_rates_provided_then_rates_are_adjusted_if_meter_is_export(is_export_meter: bool):
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2, 3, 4])
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = None
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, expected_rates)

  expected_dispatch_start = (current + timedelta(hours=2)).replace(second=0, microsecond=0)
  expected_dispatch_end = expected_dispatch_start + timedelta(minutes=90)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(
      dispatches_last_retrieved,
      1, 
      IntelligentDispatches(
        "SMART_CONTROL_IN_PROGRESS",
        [
          IntelligentDispatchItem(
            expected_dispatch_start,
            expected_dispatch_end,
            1,
            "smart-charge",
            "home"
          )
        ], 
        []
      ),
      IntelligentDispatchesHistory([]),
      1,
      dispatches_last_retrieved
    )
  }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      is_export_meter,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.original_rates == expected_retrieved_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted

    assert len(retrieved_rates.rates) == len(expected_retrieved_rates.rates)

    number_of_intelligent_rates = 0
    expected_number_of_intelligent_rates = 0 if is_export_meter else 3
    for index in range(len(retrieved_rates.rates)):
      expected_rate = expected_retrieved_rates.rates[index]
      actual_rate = retrieved_rates.rates[index]

      if is_export_meter == False and actual_rate["start"] >= expected_dispatch_start and actual_rate["end"] <= expected_dispatch_end:
        assert "is_intelligent_adjusted" in actual_rate
        assert actual_rate["is_intelligent_adjusted"] == True
        assert actual_rate["value_inc_vat"] == 1
        number_of_intelligent_rates = number_of_intelligent_rates + 1
      else:
        assert "is_intelligent_adjusted" not in actual_rate
        assert expected_rate == actual_rate

    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    assert number_of_intelligent_rates == expected_number_of_intelligent_rates
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True

@pytest.mark.asyncio
@pytest.mark.parametrize("is_export_meter",[
  (True),
  (False),
])
async def test_when_started_dispatched_rates_provided_then_rates_are_adjusted_if_meter_is_export(is_export_meter: bool):
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2, 3, 4])
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = None
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, expected_rates)

  expected_dispatch_start = (current + timedelta(hours=2)).replace(second=0, microsecond=0)
  expected_dispatch_end = expected_dispatch_start + timedelta(minutes=90)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches(
    "SMART_CONTROL_IN_PROGRESS",
    [], 
    [],
    [
      SimpleIntelligentDispatchItem(
        expected_dispatch_start,
        expected_dispatch_end
      )
    ],
  ),
  IntelligentDispatchesHistory([]),
  1,
  dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      is_export_meter,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.original_rates == expected_retrieved_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted

    assert len(retrieved_rates.rates) == len(expected_retrieved_rates.rates)

    number_of_intelligent_rates = 0
    expected_number_of_intelligent_rates = 0 if is_export_meter else 3
    for index in range(len(retrieved_rates.rates)):
      expected_rate = expected_retrieved_rates.rates[index]
      actual_rate = retrieved_rates.rates[index]

      if is_export_meter == False and actual_rate["start"] >= expected_dispatch_start and actual_rate["end"] <= expected_dispatch_end:
        assert "is_intelligent_adjusted" in actual_rate
        assert actual_rate["is_intelligent_adjusted"] == True
        assert actual_rate["value_inc_vat"] == 1
        number_of_intelligent_rates = number_of_intelligent_rates + 1
      else:
        assert "is_intelligent_adjusted" not in actual_rate
        assert expected_rate == actual_rate

    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    assert number_of_intelligent_rates == expected_number_of_intelligent_rates
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True

@pytest.mark.asyncio
async def test_when_dispatched_rates_provided_then_rates_are_adjusted():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2, 3, 4])
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = None
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, expected_rates)

  expected_dispatch_start = (current + timedelta(hours=2)).replace(second=0, microsecond=0)
  expected_dispatch_end = expected_dispatch_start + timedelta(minutes=90)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches(
    "SMART_CONTROL_IN_PROGRESS",
    [
      IntelligentDispatchItem(
        expected_dispatch_start,
        expected_dispatch_end,
        1,
        "smart-charge",
        "home"
      )
    ], 
    []
  ), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.original_rates == expected_retrieved_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted

    assert len(retrieved_rates.rates) == len(expected_retrieved_rates.rates)

    number_of_intelligent_rates = 0
    expected_number_of_intelligent_rates = 3
    for index in range(len(retrieved_rates.rates)):
      expected_rate = expected_retrieved_rates.rates[index]
      actual_rate = retrieved_rates.rates[index]

      if actual_rate["start"] >= expected_dispatch_start and actual_rate["end"] <= expected_dispatch_end:
        assert "is_intelligent_adjusted" in actual_rate
        assert actual_rate["is_intelligent_adjusted"] == True
        assert actual_rate["value_inc_vat"] == 1
        number_of_intelligent_rates = number_of_intelligent_rates + 1
      else:
        assert "is_intelligent_adjusted" not in actual_rate
        assert expected_rate == actual_rate

    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    assert number_of_intelligent_rates == expected_number_of_intelligent_rates
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True

@pytest.mark.asyncio
async def test_when_rates_not_retrieved_then_existing_rates_returned():
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(period_from, 1, create_rate_data(period_from, period_to, [1, 2, 3, 4]))
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.next_refresh == existing_rates.next_refresh + timedelta(minutes=1)
    assert retrieved_rates.last_evaluated == existing_rates.last_evaluated
    assert retrieved_rates.rates == existing_rates.rates
    assert retrieved_rates.original_rates == existing_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == existing_rates.rates_last_adjusted
    assert retrieved_rates.request_attempts == existing_rates.request_attempts + 1

    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    assert len(actual_fired_events.keys()) == 0
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
async def test_when_exception_is_raised_then_existing_rates_returned_and_exception_captured():
  mock_api_called = False
  raised_exception = RequestException("My exception", [])
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    raise raised_exception
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(period_from, 1, create_rate_data(period_from, period_to, [1, 2, 3, 4]))
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.next_refresh == existing_rates.next_refresh + timedelta(minutes=1)
    assert retrieved_rates.last_evaluated == existing_rates.last_evaluated
    assert retrieved_rates.rates == existing_rates.rates
    assert retrieved_rates.original_rates == existing_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == existing_rates.rates_last_adjusted
    assert retrieved_rates.request_attempts == existing_rates.request_attempts + 1
    assert retrieved_rates.last_error == raised_exception

    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    assert len(actual_fired_events.keys()) == 0
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
async def test_when_rates_next_refresh_is_in_the_future_dispatches_retrieved_after_rates_then_original_rates_adjusted():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  expected_original_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2, 3, 4])
  existing_rates = ElectricityRatesCoordinatorResult(current - timedelta(minutes=4, seconds=59), 1, expected_original_rates.copy())
  expected_dispatch_start = (current + timedelta(hours=2)).replace(second=0, microsecond=0)
  expected_dispatch_end = expected_dispatch_start + timedelta(minutes=90)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(existing_rates.last_evaluated + timedelta(seconds=1), 1, IntelligentDispatches(
    "SMART_CONTROL_IN_PROGRESS",
    [
      IntelligentDispatchItem(
        expected_dispatch_start,
        expected_dispatch_end,
        1,
        "smart-charge",
        "home"
      )
    ], 
    []
  ), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_evaluated == existing_rates.last_evaluated
    assert retrieved_rates.original_rates == expected_original_rates
    assert retrieved_rates.rates_last_adjusted == current

    assert len(retrieved_rates.rates) == len(existing_rates.rates)

    number_of_intelligent_rates = 0
    expected_number_of_intelligent_rates = 3
    for index in range(len(retrieved_rates.rates)):
      expected_rate = existing_rates.rates[index]
      actual_rate = retrieved_rates.rates[index]

      if actual_rate["start"] >= expected_dispatch_start and actual_rate["end"] <= expected_dispatch_end:
        assert "is_intelligent_adjusted" in actual_rate
        assert actual_rate["is_intelligent_adjusted"] == True
        assert actual_rate["value_inc_vat"] == 1
        number_of_intelligent_rates = number_of_intelligent_rates + 1
      else:
        assert "is_intelligent_adjusted" not in actual_rate
        assert expected_rate == actual_rate

    assert mock_api_called == False
    assert raise_no_active_tariff_called == False
    assert number_of_intelligent_rates == expected_number_of_intelligent_rates
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
async def test_when_rates_next_refresh_is_in_the_future_started_dispatches_retrieved_after_rates_then_original_rates_adjusted():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  expected_original_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2, 3, 4])
  existing_rates = ElectricityRatesCoordinatorResult(current - timedelta(minutes=4, seconds=59), 1, expected_original_rates.copy())
  expected_dispatch_start = (current + timedelta(hours=2)).replace(second=0, microsecond=0)
  expected_dispatch_end = expected_dispatch_start + timedelta(minutes=90)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(existing_rates.last_evaluated + timedelta(seconds=1), 1, IntelligentDispatches(
    "SMART_CONTROL_IN_PROGRESS",
    [], 
    [],
    [
      SimpleIntelligentDispatchItem(
        expected_dispatch_start,
        expected_dispatch_end
      )
    ],
  ), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_evaluated == existing_rates.last_evaluated
    assert retrieved_rates.original_rates == expected_original_rates
    assert retrieved_rates.rates_last_adjusted == current

    assert len(retrieved_rates.rates) == len(existing_rates.rates)

    number_of_intelligent_rates = 0
    expected_number_of_intelligent_rates = 3
    for index in range(len(retrieved_rates.rates)):
      expected_rate = existing_rates.rates[index]
      actual_rate = retrieved_rates.rates[index]

      if actual_rate["start"] >= expected_dispatch_start and actual_rate["end"] <= expected_dispatch_end:
        assert "is_intelligent_adjusted" in actual_rate
        assert actual_rate["is_intelligent_adjusted"] == True
        assert actual_rate["value_inc_vat"] == 1
        number_of_intelligent_rates = number_of_intelligent_rates + 1
      else:
        assert "is_intelligent_adjusted" not in actual_rate
        assert expected_rate == actual_rate

    assert mock_api_called == False
    assert raise_no_active_tariff_called == False
    assert number_of_intelligent_rates == expected_number_of_intelligent_rates
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
async def test_when_rates_next_refresh_is_in_the_future_dispatches_retrieved_before_rates_and_dispatches_not_valid_then_existing_rates_returned():
  current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(current - timedelta(minutes=4, seconds=59), 1, create_rate_data(period_from, period_to, [2, 4]))
  expected_dispatch_start = (current + timedelta(hours=2)).replace(second=0, microsecond=0)
  expected_dispatch_end = expected_dispatch_start + timedelta(minutes=90)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(existing_rates.last_evaluated + timedelta(seconds=1), 1, IntelligentDispatches(
    "SMART_CONTROL_IN_PROGRESS",
    [
      IntelligentDispatchItem(
        expected_dispatch_start,
        expected_dispatch_end,
        1,
        "smart-charge",
        "home"
      )
    ], 
    []
  ), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      True,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates == existing_rates
    assert mock_api_called == False
    assert raise_no_active_tariff_called == False
    assert len(actual_fired_events.keys()) == 0
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
async def test_when_rates_next_refresh_is_in_the_future_dispatches_retrieved_before_rates_and_dispatches_valid_then_existing_rates_returned():
  current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(current - timedelta(minutes=4, seconds=59), 1, create_rate_data(period_from, period_to, [2, 4]))
  expected_dispatch_start = (current + timedelta(hours=2)).replace(second=0, microsecond=0)
  expected_dispatch_end = expected_dispatch_start + timedelta(minutes=90)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(existing_rates.last_evaluated - timedelta(seconds=1), 1, IntelligentDispatches(
    "SMART_CONTROL_IN_PROGRESS",
    [
      IntelligentDispatchItem(
        expected_dispatch_start,
        expected_dispatch_end,
        1,
        "smart-charge",
        "home"
      )
    ], 
    []
  ), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates == existing_rates
    assert mock_api_called == False
    assert raise_no_active_tariff_called == False
    assert len(actual_fired_events.keys()) == 0
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
async def test_when_rate_is_intelligent_and_dispatches_not_available_then_existing_rates_returned():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2])
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info(product_code="INTELLI-VAR-22-10-14")
  existing_rates = ElectricityRatesCoordinatorResult(period_to - timedelta(days=60), 1, create_rate_data(period_from - timedelta(days=60), period_to - timedelta(days=60), [2, 4]))
  dispatches_result = { "1": None }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates == existing_rates
    assert mock_api_called == False
    assert raise_no_active_tariff_called == False
    assert len(actual_fired_events.keys()) == 0
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
async def test_when_rate_is_intelligent_and_dispatches_available_and_rates_not_retrieved_then_existing_rates_updated():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  expected_original_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2, 3, 4])
  existing_rates = ElectricityRatesCoordinatorResult(current - timedelta(minutes=4, seconds=59), 1, expected_original_rates.copy())
  expected_dispatch_start = (current + timedelta(hours=2)).replace(second=0, microsecond=0)
  expected_dispatch_end = expected_dispatch_start + timedelta(minutes=90)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(existing_rates.last_evaluated + timedelta(seconds=1), 1, IntelligentDispatches(
    "SMART_CONTROL_IN_PROGRESS",
    [
      IntelligentDispatchItem(
        expected_dispatch_start,
        expected_dispatch_end,
        1,
        "smart-charge",
        "home"
      )
    ], 
    []
  ), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_evaluated == existing_rates.last_evaluated
    assert retrieved_rates.original_rates == expected_original_rates
    assert retrieved_rates.rates_last_adjusted == current

    assert len(retrieved_rates.rates) == len(existing_rates.rates)

    number_of_intelligent_rates = 0
    expected_number_of_intelligent_rates = 3
    for index in range(len(retrieved_rates.rates)):
      expected_rate = existing_rates.rates[index]
      actual_rate = retrieved_rates.rates[index]

      if actual_rate["start"] >= expected_dispatch_start and actual_rate["end"] <= expected_dispatch_end:
        assert "is_intelligent_adjusted" in actual_rate
        assert actual_rate["is_intelligent_adjusted"] == True
        assert actual_rate["value_inc_vat"] == 1
        number_of_intelligent_rates = number_of_intelligent_rates + 1
      else:
        assert "is_intelligent_adjusted" not in actual_rate
        assert expected_rate == actual_rate

    assert mock_api_called == False
    assert raise_no_active_tariff_called == False
    assert number_of_intelligent_rates == expected_number_of_intelligent_rates
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
async def test_when_rate_is_intelligent_and_one_intelligent_device_dispatches_available_and_one_intelligent_device_dispatches_not_available_and_rates_not_retrieved_then_existing_rates_updated():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  expected_original_rates = create_rate_data(expected_period_from, expected_period_to, [1, 2, 3, 4])
  existing_rates = ElectricityRatesCoordinatorResult(current - timedelta(minutes=4, seconds=59), 1, expected_original_rates.copy())
  expected_dispatch_one_start = (current + timedelta(hours=2)).replace(second=0, microsecond=0)
  expected_dispatch_one_end = expected_dispatch_one_start + timedelta(minutes=90)

  expected_dispatch_two_start = (current - timedelta(hours=4)).replace(second=0, microsecond=0)
  expected_dispatch_two_end = expected_dispatch_two_start + timedelta(minutes=90)
  dispatches_result = { 
    "1": IntelligentDispatchesCoordinatorResult(existing_rates.last_evaluated - timedelta(seconds=1),
                                                1,
                                                IntelligentDispatches(
                                                  "SMART_CONTROL_IN_PROGRESS",
                                                  [
                                                    IntelligentDispatchItem(
                                                      expected_dispatch_one_start,
                                                      expected_dispatch_one_end,
                                                      1,
                                                      "smart-charge",
                                                      "home"
                                                    )
                                                  ], 
                                                  []
                                                ),
                                                IntelligentDispatchesHistory([]), 
                                                1,
                                                dispatches_last_retrieved),
    "2": IntelligentDispatchesCoordinatorResult(existing_rates.last_evaluated + timedelta(seconds=1),
                                                1,
                                                IntelligentDispatches(
                                                  "SMART_CONTROL_IN_PROGRESS",
                                                  [
                                                    IntelligentDispatchItem(
                                                      expected_dispatch_two_start,
                                                      expected_dispatch_two_end,
                                                      1,
                                                      "smart-charge",
                                                      "home"
                                                    )
                                                  ], 
                                                  []
                                                ),
                                                IntelligentDispatchesHistory([]),
                                                1,
                                                dispatches_last_retrieved),                                 
  }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_evaluated == existing_rates.last_evaluated
    assert retrieved_rates.original_rates == expected_original_rates
    assert retrieved_rates.rates_last_adjusted == current

    assert len(retrieved_rates.rates) == len(existing_rates.rates)

    number_of_intelligent_rates = 0
    expected_number_of_intelligent_rates = 6
    for index in range(len(retrieved_rates.rates)):
      expected_rate = existing_rates.rates[index]
      actual_rate = retrieved_rates.rates[index]

      if ((actual_rate["start"] >= expected_dispatch_one_start and actual_rate["end"] <= expected_dispatch_one_end) or
          (actual_rate["start"] >= expected_dispatch_two_start and actual_rate["end"] <= expected_dispatch_two_end)):
        assert "is_intelligent_adjusted" in actual_rate
        assert actual_rate["is_intelligent_adjusted"] == True
        assert actual_rate["value_inc_vat"] == 1
        number_of_intelligent_rates = number_of_intelligent_rates + 1
      else:
        assert "is_intelligent_adjusted" not in actual_rate
        assert expected_rate == actual_rate

    assert mock_api_called == False
    assert raise_no_active_tariff_called == False
    assert number_of_intelligent_rates == expected_number_of_intelligent_rates
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, expected_period_from, expected_period_from + timedelta(days=1))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, expected_period_from + timedelta(days=1), expected_period_from + timedelta(days=2))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, expected_period_from + timedelta(days=2), expected_period_from + timedelta(days=3))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == False

@pytest.mark.asyncio
@pytest.mark.parametrize("current_unique_rates,previous_unique_rates,expected_unique_rates_changed_event_fired",[
  ([1, 2, 3], [1, 2, 3], False),
  ([1, 2], [1, 2], False),
  ([1], [1, 2, 3, 4], False),
  ([1, 2, 3, 4], [1], False),
  ([1], [1, 2, 3], True),
  ([1, 2], [1, 2, 3], True),
  ([1, 2, 3], [1, 2], True),
  ([1, 2, 3], [1], True),
])
async def test_when_rates_change_correctly_then_unique_rates_changed_event_fired(current_unique_rates: list, previous_unique_rates: list, expected_unique_rates_changed_event_fired: bool):
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = create_rate_data(expected_period_from, expected_period_to, current_unique_rates)
  
  # Put rates into reverse order to make sure sorting works
  expected_rates.sort(key=lambda rate: (rate["start"].timestamp(), rate["start"].fold), reverse=True)

  assert expected_rates[-1]["start"] == expected_period_from
  assert expected_rates[0]["end"] == expected_period_to
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    mock_api_called = True
    return expected_rates
  
  def fire_event(name, metadata):
    return None
  
  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  unique_rates_changed_called = False
  async def unique_rates_changed(name, metadata):
    nonlocal unique_rates_changed_called
    unique_rates_changed_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(period_from, 1, create_rate_data(period_from, period_to, previous_unique_rates))

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      {},
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty,
      unique_rates_changed=unique_rates_changed
    )

  assert unique_rates_changed_called == expected_unique_rates_changed_event_fired
  assert raise_rates_empty_called == False
  assert clear_rates_empty_called == True

@pytest.mark.asyncio
@pytest.mark.parametrize("existing_rates",[
  (None),
  (ElectricityRatesCoordinatorResult(period_from, 1, [])),
  (ElectricityRatesCoordinatorResult(period_from, 1, None)),
])
async def test_when_clocks_change_then_rates_are_correct(existing_rates):
  current = datetime(2024, 10, 27, 10, 30, tzinfo=ZoneInfo(key='Europe/London'))
  expected_period_from = datetime.strptime("2024-10-26T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_period_to = datetime.strptime("2024-10-29T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = create_rate_data(datetime(2024, 10, 26, 0, 0, tzinfo=ZoneInfo(key='Europe/London')), datetime(2024, 10, 27, 1, 30, tzinfo=ZoneInfo(key='Europe/London')), [1])
  expected_rates.append({
    "start": datetime(2024, 10, 27, 1, 30, tzinfo=ZoneInfo(key='Europe/London')),
    "end": datetime(2024, 10, 27, 1, 0, fold=1, tzinfo=ZoneInfo(key='Europe/London')),
    "value_inc_vat": 1,
    "tariff_code": "E-1R-Test-L",
    "is_capped": False
  })
  expected_rates.append({
    "start": datetime(2024, 10, 27, 1, 0, fold=1, tzinfo=ZoneInfo(key='Europe/London')),
    "end": datetime(2024, 10, 27, 1, 30, fold=1, tzinfo=ZoneInfo(key='Europe/London')),
    "value_inc_vat": 1,
    "tariff_code": "E-1R-Test-L",
    "is_capped": False
  })
  expected_rates.append({
    "start": datetime(2024, 10, 27, 1, 30, fold=1, tzinfo=ZoneInfo(key='Europe/London')),
    "end": datetime(2024, 10, 27, 2, 0, tzinfo=ZoneInfo(key='Europe/London')),
    "value_inc_vat": 1,
    "tariff_code": "E-1R-Test-L",
    "is_capped": False
  })
  expected_rates.extend(create_rate_data(datetime(2024, 10, 27, 2, 0, tzinfo=ZoneInfo(key='Europe/London')), datetime(2024, 10, 29, 0, 0, tzinfo=ZoneInfo(key='Europe/London')), [1]))
  
  expected_rates_unsorted = expected_rates.copy()
  
  # Put rates into reverse order to make sure sorting works
  expected_rates.sort(key=lambda rate: (rate["start"].timestamp(), rate["start"].fold), reverse=True)

  assert expected_rates[-1]["start"] == expected_period_from
  assert expected_rates[0]["end"] == expected_period_to
  
  mock_api_called = False
  requested_period_from = None
  requested_period_to = None
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal requested_period_from, requested_period_to, mock_api_called, expected_rates

    requested_client, requested_product_code, requested_tariff_code, is_smart_meter, requested_period_from, requested_period_to = args
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, expected_rates_unsorted)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.rates == expected_retrieved_rates.rates
    assert retrieved_rates.original_rates == expected_retrieved_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted
    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    # assert requested_period_from == expected_period_from
    # assert requested_period_to == expected_period_to
    
    assert len(actual_fired_events.keys()) == 3
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES, datetime.strptime("2024-10-26T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-10-27T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_CURRENT_DAY_RATES, datetime.strptime("2024-10-27T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-10-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"))
    assert_raised_events(actual_fired_events, EVENT_ELECTRICITY_NEXT_DAY_RATES, datetime.strptime("2024-10-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-10-29T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"))
    assert raise_rates_empty_called == False
    assert clear_rates_empty_called == True

@pytest.mark.asyncio
async def test_when_existing_rates_is_old_but_no_rates_returned_then_rates_retrieved():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_rates = []
  mock_api_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_rates
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  raise_no_active_tariff_called = False
  async def raise_no_active_tariff(*args, **kwargs):
    nonlocal raise_no_active_tariff_called
    raise_no_active_tariff_called = True
    return None

  raise_rates_empty_called = False
  def raise_rates_empty(*args, **kwargs):
    nonlocal raise_rates_empty_called
    raise_rates_empty_called = True
    return None
  
  clear_rates_empty_called = False
  def clear_rates_empty(*args, **kwargs):
    nonlocal clear_rates_empty_called
    clear_rates_empty_called = True
    return None
  
  account_info = get_account_info()
  existing_rates = ElectricityRatesCoordinatorResult(period_to - timedelta(days=60), 1, create_rate_data(period_from - timedelta(days=60), period_to - timedelta(days=60), [2, 4]))
  expected_retrieved_rates = ElectricityRatesCoordinatorResult(current, 1, expected_rates)
  dispatches_result = { "1": IntelligentDispatchesCoordinatorResult(dispatches_last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, dispatches_last_retrieved) }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates: ElectricityRatesCoordinatorResult = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      True,
      False,
      existing_rates,
      dispatches_result,
      fire_event,
      raise_no_active_rate=raise_no_active_tariff,
      raise_rates_empty=raise_rates_empty,
      clear_rates_empty=clear_rates_empty
    )

    assert retrieved_rates is not None
    assert retrieved_rates.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES)
    assert retrieved_rates.last_evaluated == expected_retrieved_rates.last_evaluated
    assert retrieved_rates.rates == expected_retrieved_rates.rates
    assert retrieved_rates.original_rates == expected_retrieved_rates.original_rates
    assert retrieved_rates.rates_last_adjusted == expected_retrieved_rates.rates_last_adjusted
    assert mock_api_called == True
    assert raise_no_active_tariff_called == False
    
    assert len(actual_fired_events.keys()) == 3
    assert raise_rates_empty_called == True
    assert clear_rates_empty_called == False