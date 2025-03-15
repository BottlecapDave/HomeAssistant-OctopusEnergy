from datetime import datetime, timedelta
import pytest
import mock

from custom_components.octopus_energy.const import REFRESH_RATE_IN_MINUTES_INTELLIGENT
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatches
from custom_components.octopus_energy.api_client.intelligent_device import IntelligentDevice
from custom_components.octopus_energy.intelligent import mock_intelligent_dispatches
from custom_components.octopus_energy.coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult, async_refresh_intelligent_dispatches

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
last_retrieved = datetime.strptime("2023-07-14T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

product_code = "INTELLI-VAR-22-10-14"
tariff_code = "E-1R-INTELLI-VAR-22-10-14-C"
mpan = "1234567890"
serial_number = "abcdefgh"

intelligent_device = IntelligentDevice("1", "2", "3", "4", 1, 2, True)

def get_account_info(is_active_agreement = True, active_product_code = product_code, active_tariff_code = tariff_code):
  return {
    "id": "A-XXXXXX",
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
            "end": "2023-08-01T00:00:00+01:00" if is_active_agreement else "2023-09-01T00:00:00+01:00",
            "tariff_code": active_tariff_code,
            "product_code": active_product_code
          }
        ]
      }
    ]
  }

@pytest.mark.asyncio
async def test_when_account_info_is_none_then_existing_dispatches_returned():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = None
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved, 1, mock_intelligent_dispatches(), 1, last_retrieved)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert retrieved_dispatches == existing_dispatches
    assert mock_api_called == False

    assert save_dispatches_called == False
    assert save_dispatches_account_id == None
    assert save_dispatches_dispatches == None

@pytest.mark.asyncio
async def test_when_intelligent_device_is_none_then_none_returned():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info(True, active_product_code="GO-18-06-12")
  existing_dispatches = None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      None,
      existing_dispatches,
      False,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert mock_api_called == False
    assert retrieved_dispatches is not None
    assert retrieved_dispatches.dispatches is None

    assert save_dispatches_called == False
    assert save_dispatches_account_id == None
    assert save_dispatches_dispatches == None

@pytest.mark.asyncio
async def test_when_not_on_intelligent_tariff_then_none_returned():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info(True, active_product_code="GO-18-06-12")
  existing_dispatches = None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert mock_api_called == False
    assert retrieved_dispatches is not None
    assert retrieved_dispatches.dispatches is None

    assert save_dispatches_called == False
    assert save_dispatches_account_id == None
    assert save_dispatches_dispatches == None

@pytest.mark.asyncio
async def test_when_mock_is_true_then_none_returned():
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  existing_dispatches = None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      True,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    mocked_data = mock_intelligent_dispatches()

    assert mock_api_called == True
    assert retrieved_dispatches is not None

    assert len(retrieved_dispatches.dispatches.completed) == len(mocked_data.completed)
    for index in range(len(retrieved_dispatches.dispatches.completed)):
      assert retrieved_dispatches.dispatches.completed[index].charge_in_kwh == mocked_data.completed[index].charge_in_kwh
      assert retrieved_dispatches.dispatches.completed[index].end == mocked_data.completed[index].end
      assert retrieved_dispatches.dispatches.completed[index].location == mocked_data.completed[index].location
      assert retrieved_dispatches.dispatches.completed[index].source == mocked_data.completed[index].source
      assert retrieved_dispatches.dispatches.completed[index].start == mocked_data.completed[index].start
    
    assert len(retrieved_dispatches.dispatches.planned) == len(mocked_data.planned)
    for index in range(len(retrieved_dispatches.dispatches.planned)):
      assert retrieved_dispatches.dispatches.planned[index].charge_in_kwh == mocked_data.planned[index].charge_in_kwh
      assert retrieved_dispatches.dispatches.planned[index].end == mocked_data.planned[index].end
      assert retrieved_dispatches.dispatches.planned[index].location == mocked_data.planned[index].location
      assert retrieved_dispatches.dispatches.planned[index].source == mocked_data.planned[index].source
      assert retrieved_dispatches.dispatches.planned[index].start == mocked_data.planned[index].start

    assert save_dispatches_called == True
    assert save_dispatches_account_id == account_info["id"]
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_then_existing_dispatches_returned():
  current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, mock_intelligent_dispatches(), 1, last_retrieved)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert mock_api_called == False
    assert retrieved_dispatches == existing_dispatches

    assert save_dispatches_called == False
    assert save_dispatches_account_id == None
    assert save_dispatches_dispatches == None

@pytest.mark.asyncio
@pytest.mark.parametrize("existing_dispatches",[
  (None),
  (IntelligentDispatchesCoordinatorResult(last_retrieved, 1, IntelligentDispatches(None, None, None), 1, last_retrieved)),
  (IntelligentDispatchesCoordinatorResult(last_retrieved, 1, None, 1, last_retrieved)),
])
async def test_when_existing_dispatches_is_none_then_dispatches_retrieved(existing_dispatches):
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called, expected_dispatches
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, 1, last_retrieved)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert save_dispatches_called == True
    assert save_dispatches_account_id == account_info["id"]
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches
    
@pytest.mark.asyncio
async def test_when_existing_dispatches_is_old_then_dispatches_retrieved():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), 1, last_retrieved)
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, 1, last_retrieved)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert save_dispatches_called == True
    assert save_dispatches_account_id == account_info["id"]
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_settings_not_retrieved_then_existing_dispatches_returned():
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), 1, last_retrieved)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == existing_dispatches.next_refresh + timedelta(minutes=1)
    assert retrieved_dispatches.last_evaluated == existing_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == existing_dispatches.dispatches
    assert retrieved_dispatches.request_attempts == existing_dispatches.request_attempts + 1

    assert mock_api_called == True

    assert save_dispatches_called == False
    assert save_dispatches_account_id == None
    assert save_dispatches_dispatches == None

@pytest.mark.asyncio
async def test_when_exception_raised_then_existing_dispatches_returned_and_exception_captured():
  mock_api_called = False
  raised_exception = RequestException("foo", [])
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    raise raised_exception
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), 1, last_retrieved)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == existing_dispatches.next_refresh + timedelta(minutes=1)
    assert retrieved_dispatches.last_evaluated == existing_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == existing_dispatches.dispatches
    assert retrieved_dispatches.request_attempts == existing_dispatches.request_attempts + 1
    assert retrieved_dispatches.last_error == raised_exception

    assert mock_api_called == True

    assert save_dispatches_called == False
    assert save_dispatches_account_id == None
    assert save_dispatches_dispatches == None

@pytest.mark.asyncio
async def test_when_requests_reached_for_hour_and_due_to_be_reset_then_dispatches_retrieved():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), 20, current - timedelta(hours=1))
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, 1, last_retrieved)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert save_dispatches_called == True
    assert save_dispatches_account_id == account_info["id"]
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_requests_reached_for_hour_and_not_due_to_be_reset_then_existing_dispatches_returned_with_error():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), 20, current)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      False,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == existing_dispatches.next_refresh
    assert retrieved_dispatches.last_evaluated == existing_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == existing_dispatches.dispatches
    assert retrieved_dispatches.request_attempts == existing_dispatches.request_attempts
    assert retrieved_dispatches.requests_current_hour == existing_dispatches.requests_current_hour
    assert retrieved_dispatches.requests_current_hour_last_reset == existing_dispatches.requests_current_hour_last_reset
    assert retrieved_dispatches.last_error == f"Maximum requests of 20/hour reached. Will reset after {current + timedelta(hours=1)}"
    assert mock_api_called == False

    assert save_dispatches_called == False
    assert save_dispatches_account_id == None
    assert save_dispatches_dispatches == None

@pytest.mark.asyncio
async def test_when_manual_refresh_is_called_within_one_minute_then_existing_dispatches_returned_with_error():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(current - timedelta(seconds=1), 1, mock_intelligent_dispatches(), 1, current)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      True,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == existing_dispatches.next_refresh
    assert retrieved_dispatches.last_evaluated == existing_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == existing_dispatches.dispatches
    assert retrieved_dispatches.request_attempts == existing_dispatches.request_attempts
    assert retrieved_dispatches.requests_current_hour == existing_dispatches.requests_current_hour
    assert retrieved_dispatches.requests_current_hour_last_reset == existing_dispatches.requests_current_hour_last_reset
    assert retrieved_dispatches.last_error == f"Manual refreshing of dispatches cannot be be called again until {existing_dispatches.last_retrieved + timedelta(minutes=1)}"
    assert mock_api_called == False

    assert save_dispatches_called == False
    assert save_dispatches_account_id == None
    assert save_dispatches_dispatches == None

@pytest.mark.asyncio
async def test_when_manual_refresh_is_called_after_one_minute_then_dispatches_retrieved():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(current - timedelta(minutes=1), 1, mock_intelligent_dispatches(), 1, current - timedelta(hours=1))
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, 1, last_retrieved)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      True,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert mock_api_called == True
    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == current
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches

    assert save_dispatches_called == True
    assert save_dispatches_account_id == account_info["id"]
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
@pytest.mark.parametrize("planned_is_empty,completed_is_empty",[
  (True, False),
  (False, True),
])
async def test_when_no_dispatches_are_retrieved_and_none_exist_then_dispatches_retrieved(planned_is_empty: bool, completed_is_empty: bool):
  expected_dispatches = mock_intelligent_dispatches()
  if planned_is_empty:
    expected_dispatches.planned = []
  elif completed_is_empty:
    expected_dispatches.completed = []
  
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  save_dispatches_called = False
  save_dispatches_account_id = None
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_account_id, save_dispatches_dispatches
    save_dispatches_called = True
    account_id, dispatches = args
    save_dispatches_account_id = account_id
    save_dispatches_dispatches = dispatches
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(current - timedelta(minutes=1), 1, mock_intelligent_dispatches(), 1, current - timedelta(hours=1))
  if planned_is_empty:
    existing_dispatches.dispatches.planned = []
  elif completed_is_empty:
    existing_dispatches.dispatches.completed = []

  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, 1, last_retrieved)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      intelligent_device,
      existing_dispatches,
      False,
      True,
      async_merge_dispatch_data,
      async_save_dispatches
    )

    assert mock_api_called == True
    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == current
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches

    assert save_dispatches_called == False
    assert save_dispatches_account_id == None
    assert save_dispatches_dispatches == None