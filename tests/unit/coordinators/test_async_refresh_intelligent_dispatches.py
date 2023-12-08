from datetime import datetime, timedelta, time
import pytest
import mock

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatches
from custom_components.octopus_energy.intelligent import mock_intelligent_dispatches
from custom_components.octopus_energy.coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult, async_refresh_intelligent_dispatches

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
last_retrieved = datetime.strptime("2023-07-14T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

tariff_code = "E-1R-INTELLI-VAR-22-10-14-C"
mpan = "1234567890"
serial_number = "abcdefgh"

def get_account_info(is_active_agreement = True, active_tariff_code = tariff_code):
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
            "product": "SUPER-GREEN-24M-21-07-30"
          }
        ]
      }
    ]
  }

@pytest.mark.asyncio
async def test_when_account_info_is_none_then_existing_settings_returned():
  expected_dispatches = IntelligentDispatches([], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  account_info = None
  existing_settings = IntelligentDispatchesCoordinatorResult(last_retrieved, 1, mock_intelligent_dispatches())
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      existing_settings,
      False,
      async_merge_dispatch_data
    )

    assert retrieved_dispatches == existing_settings
    assert mock_api_called == False

@pytest.mark.asyncio
async def test_when_not_on_intelligent_tariff_then_none_returned():
  expected_dispatches = IntelligentDispatches([], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  account_info = get_account_info(True, "E-1R-GO-18-06-12-A")
  existing_settings = None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      existing_settings,
      False,
      async_merge_dispatch_data
    )

    assert mock_api_called == False
    assert retrieved_dispatches is not None
    assert retrieved_dispatches.dispatches is None

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
  
  account_info = get_account_info()
  existing_settings = None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      existing_settings,
      True,
      async_merge_dispatch_data
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

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_past_then_existing_settings_returned():
  current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_dispatches = IntelligentDispatches([], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  account_info = get_account_info()
  existing_settings = IntelligentDispatchesCoordinatorResult(current - timedelta(minutes=4, seconds=59), 1, mock_intelligent_dispatches())
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      existing_settings,
      False,
      async_merge_dispatch_data
    )

    assert retrieved_dispatches == existing_settings
    assert mock_api_called == False


@pytest.mark.asyncio
@pytest.mark.parametrize("existing_settings",[
  (None),
  (IntelligentDispatchesCoordinatorResult(last_retrieved, 1, [])),
  (IntelligentDispatchesCoordinatorResult(last_retrieved, 1, None)),
])
async def test_when_existing_settings_is_none_then_settings_retrieved(existing_settings):
  expected_dispatches = IntelligentDispatches([], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called, expected_dispatches
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  account_info = get_account_info()
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      existing_settings,
      False,
      async_merge_dispatch_data
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.last_retrieved == expected_retrieved_dispatches.last_retrieved
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True
    
@pytest.mark.asyncio
async def test_when_existing_settings_is_old_then_settings_retrieved():
  expected_dispatches = IntelligentDispatches([], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  account_info = get_account_info()
  existing_settings = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches())
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      existing_settings,
      False,
      async_merge_dispatch_data
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.last_retrieved == expected_retrieved_dispatches.last_retrieved
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_settings_not_retrieved_then_existing_settings_returned():
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  async def async_merge_dispatch_data(*args, **kwargs):
    account_id, completed_dispatches = args
    return completed_dispatches
  
  account_info = get_account_info()
  existing_settings = IntelligentDispatchesCoordinatorResult(last_retrieved, 1, IntelligentDispatches([], []))
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_dispatches=async_mock_get_intelligent_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_dispatches: IntelligentDispatchesCoordinatorResult = await async_refresh_intelligent_dispatches(
      current,
      client,
      account_info,
      existing_settings,
      False,
      async_merge_dispatch_data
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == existing_settings.next_refresh + timedelta(minutes=1)
    assert retrieved_dispatches.last_retrieved == existing_settings.last_retrieved
    assert retrieved_dispatches.dispatches == existing_settings.dispatches
    assert retrieved_dispatches.request_attempts == existing_settings.request_attempts + 1

    assert mock_api_called == True