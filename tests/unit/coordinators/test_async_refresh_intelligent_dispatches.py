from datetime import datetime, timedelta
from custom_components.octopus_energy.storage.intelligent_dispatches_history import IntelligentDispatchesHistory, IntelligentDispatchesHistoryItem
import pytest
import mock

from custom_components.octopus_energy.const import INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS, REFRESH_RATE_IN_MINUTES_INTELLIGENT
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatchItem, IntelligentDispatches, SimpleIntelligentDispatchItem
from custom_components.octopus_energy.api_client.intelligent_device import IntelligentDevice
from custom_components.octopus_energy.intelligent import mock_intelligent_devices, mock_intelligent_dispatches
from custom_components.octopus_energy.coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult, async_refresh_intelligent_dispatches

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
last_retrieved = datetime.strptime("2023-07-14T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

product_code = "INTELLI-VAR-22-10-14"
tariff_code = "E-1R-INTELLI-VAR-22-10-14-C"
mpan = "1234567890"
serial_number = "abcdefgh"

intelligent_device = mock_intelligent_devices()[0]

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
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = None
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved, 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches == existing_dispatches
    assert mock_api_called == False

    assert save_dispatches_called == False
    assert save_dispatches_dispatches == None

    assert save_dispatches_history_called == False
    assert save_dispatches_history_history == None

@pytest.mark.asyncio
async def test_when_intelligent_device_is_none_then_none_returned():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert mock_api_called == False
    assert retrieved_dispatches is not None
    assert retrieved_dispatches.dispatches is None

    assert save_dispatches_called == False
    assert save_dispatches_dispatches == None

    assert save_dispatches_history_called == False
    assert save_dispatches_history_history == None

@pytest.mark.asyncio
async def test_when_not_on_intelligent_tariff_then_none_returned():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert mock_api_called == False
    assert retrieved_dispatches is not None
    assert retrieved_dispatches.dispatches is None

    assert save_dispatches_called == False
    assert save_dispatches_dispatches == None

    assert save_dispatches_history_called == False
    assert save_dispatches_history_history == None

@pytest.mark.asyncio
async def test_when_mock_is_true_then_none_returned():
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
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
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 1
    assert save_dispatches_history_history.history[0].timestamp == current
    assert save_dispatches_history_history.history[0].dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_then_existing_dispatches_returned():
  current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert mock_api_called == False
    assert retrieved_dispatches == existing_dispatches

    assert save_dispatches_called == False
    assert save_dispatches_dispatches == None

    assert save_dispatches_history_called == False
    assert save_dispatches_history_history == None

@pytest.mark.asyncio
async def test_when_existing_dispatches_returned_and_planned_dispatch_started_and_refreshed_recently_then_started_dispatches_not_updated():
  current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(current - timedelta(minutes=2), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 1, last_retrieved)
  existing_dispatches.dispatches.current_state = "SMART_CONTROL_IN_PROGRESS"
  existing_dispatches.dispatches.planned = [
    IntelligentDispatchItem(
      current - timedelta(minutes=1),
      current + timedelta(minutes=45),
      1.1,
      None,
      "home"
    )
  ]
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert mock_api_called == False
    assert retrieved_dispatches == existing_dispatches

    assert len(retrieved_dispatches.dispatches.started) == 0

    assert save_dispatches_called == False
    assert save_dispatches_dispatches == None

    assert save_dispatches_history_called == False
    assert save_dispatches_history_history == None

@pytest.mark.asyncio
@pytest.mark.parametrize("existing_dispatches",[
  (None),
  (IntelligentDispatchesCoordinatorResult(last_retrieved, 1, IntelligentDispatches(None, None, None), IntelligentDispatchesHistory([]), 1, last_retrieved)),
  (IntelligentDispatchesCoordinatorResult(last_retrieved, 1, None, IntelligentDispatchesHistory([]), 1, last_retrieved)),
])
async def test_when_existing_dispatches_is_none_then_dispatches_retrieved(existing_dispatches):
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called, expected_dispatches
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert save_dispatches_called == True
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 1
    assert save_dispatches_history_history.history[0].timestamp == current
    assert save_dispatches_history_history.history[0].dispatches == retrieved_dispatches.dispatches
    
@pytest.mark.asyncio
async def test_when_existing_dispatches_is_old_then_dispatches_retrieved():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  expected_history: list[IntelligentDispatchesHistoryItem] = [
    IntelligentDispatchesHistoryItem(current - timedelta(hours=1), IntelligentDispatches("SMART_CONTROL_OFF", [], []))
  ]
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory(expected_history), 1, last_retrieved)
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert save_dispatches_called == True
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 2

    assert save_dispatches_history_history.history[0].timestamp == expected_history[0].timestamp
    assert save_dispatches_history_history.history[0].dispatches == expected_history[0].dispatches

    assert save_dispatches_history_history.history[1].timestamp == current
    assert save_dispatches_history_history.history[1].dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_existing_dispatches_history_is_old_then_not_included_in_new_history():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  expected_history: list[IntelligentDispatchesHistoryItem] = [
    IntelligentDispatchesHistoryItem(current - timedelta(days=3, seconds=1), IntelligentDispatches("SMART_CONTROL_OFF", [], [])),
    IntelligentDispatchesHistoryItem(current - timedelta(days=2, seconds=1), IntelligentDispatches("SMART_CONTROL_OFF", [], []))
  ]
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory(expected_history), 1, last_retrieved)
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert save_dispatches_called == True
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 2

    assert save_dispatches_history_history.history[0].timestamp == expected_history[1].timestamp
    assert save_dispatches_history_history.history[0].dispatches == expected_history[1].dispatches

    assert save_dispatches_history_history.history[1].timestamp == current
    assert save_dispatches_history_history.history[1].dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_settings_not_retrieved_then_existing_dispatches_returned():
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == existing_dispatches.next_refresh + timedelta(minutes=1)
    assert retrieved_dispatches.last_evaluated == existing_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == existing_dispatches.dispatches
    assert retrieved_dispatches.request_attempts == existing_dispatches.request_attempts + 1

    assert mock_api_called == True

    assert save_dispatches_called == False
    assert save_dispatches_dispatches == None

    assert save_dispatches_history_called == False
    assert save_dispatches_history_history == None

@pytest.mark.asyncio
async def test_when_exception_raised_then_existing_dispatches_returned_and_exception_captured():
  mock_api_called = False
  raised_exception = RequestException("foo", [])
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    raise raised_exception
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved, 1, IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], []), IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == existing_dispatches.next_refresh + timedelta(minutes=1)
    assert retrieved_dispatches.last_evaluated == existing_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == existing_dispatches.dispatches
    assert retrieved_dispatches.request_attempts == existing_dispatches.request_attempts + 1
    assert retrieved_dispatches.last_error == raised_exception

    assert mock_api_called == True

    assert save_dispatches_called == False
    assert save_dispatches_dispatches == None

    assert save_dispatches_history_called == False
    assert save_dispatches_history_history == None

@pytest.mark.asyncio
async def test_when_requests_reached_for_hour_and_due_to_be_reset_then_dispatches_retrieved():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 20, current - timedelta(hours=1))
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert save_dispatches_called == True
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 1
    assert save_dispatches_history_history.history[0].timestamp == current
    assert save_dispatches_history_history.history[0].dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_requests_reached_for_hour_and_not_due_to_be_reset_then_existing_dispatches_returned_with_error():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 20, current)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
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
    assert save_dispatches_dispatches == None

    assert save_dispatches_history_called == False
    assert save_dispatches_history_history == None

@pytest.mark.asyncio
async def test_when_manual_refresh_is_called_within_one_minute_then_existing_dispatches_returned_with_error():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(current - timedelta(seconds=1), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 1, current)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
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
    assert save_dispatches_dispatches == None

    assert save_dispatches_history_called == False
    assert save_dispatches_history_history == None

@pytest.mark.asyncio
async def test_when_manual_refresh_is_called_after_one_minute_then_dispatches_retrieved():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(current - timedelta(minutes=1), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 1, current - timedelta(hours=1))
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert mock_api_called == True
    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == current
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches

    assert save_dispatches_called == True
    assert save_dispatches_dispatches == retrieved_dispatches.dispatches

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 1
    assert save_dispatches_history_history.history[0].timestamp == current
    assert save_dispatches_history_history.history[0].dispatches == retrieved_dispatches.dispatches

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
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(current - timedelta(minutes=1), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 1, current - timedelta(hours=1))
  if planned_is_empty:
    existing_dispatches.dispatches.planned = []
  elif completed_is_empty:
    existing_dispatches.dispatches.completed = []

  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert mock_api_called == True
    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == current
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches

    assert save_dispatches_called == False
    assert save_dispatches_dispatches == None

    assert save_dispatches_history_called == False
    assert save_dispatches_history_history == None

@pytest.mark.asyncio
async def test_when_retrieved_planned_dispatch_started_and_in_boosting_mode_then_started_dispatches_not_added_to():
  expected_dispatches = IntelligentDispatches("BOOSTING", [
    IntelligentDispatchItem(
      current - timedelta(minutes=1),
      current + timedelta(minutes=30),
      1.1,
      None,
      "home"
    )
  ], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 1, last_retrieved)
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert len(retrieved_dispatches.dispatches.started) == 0
    assert mock_api_called == True

    assert save_dispatches_called == True

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 1
    assert save_dispatches_history_history.history[0].timestamp == current
    assert save_dispatches_history_history.history[0].dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_retrieved_planned_dispatch_started_and_not_in_boosting_mode_then_started_dispatches_added_to():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [
    IntelligentDispatchItem(
      current - timedelta(minutes=1),
      current + timedelta(minutes=30),
      1.1,
      None,
      "home"
    )
  ], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 1, last_retrieved)
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert len(retrieved_dispatches.dispatches.started) == 1
    assert retrieved_dispatches.dispatches.started[0].start == current.replace(second=0, microsecond=0)
    assert retrieved_dispatches.dispatches.started[0].end == current.replace(second=0, microsecond=0) + timedelta(minutes=30)

    assert save_dispatches_called == True

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 1
    assert save_dispatches_history_history.history[0].timestamp == current
    assert save_dispatches_history_history.history[0].dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_retrieved_planned_dispatch_started_and_existing_started_dispatch_exists_in_previous_period_then_existing_started_dispatch_extended():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [
    IntelligentDispatchItem(
      current - timedelta(minutes=1),
      current + timedelta(minutes=30),
      1.1,
      None,
      "home"
    )
  ], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(expected_dispatches.current_state), IntelligentDispatchesHistory([]), 1, last_retrieved)
  existing_dispatches.dispatches.planned = expected_dispatches.planned.copy()
  existing_dispatches.dispatches.completed = expected_dispatches.completed.copy()
  existing_dispatches.dispatches.started = [
    SimpleIntelligentDispatchItem(
      current.replace(second=0, microsecond=0) - timedelta(minutes=30),
      current.replace(second=0, microsecond=0)
    )
  ]
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert len(retrieved_dispatches.dispatches.started) == 1
    assert retrieved_dispatches.dispatches.started[0].start == current.replace(second=0, microsecond=0) - timedelta(minutes=30)
    assert retrieved_dispatches.dispatches.started[0].end == current.replace(second=0, microsecond=0) + timedelta(minutes=30)

    assert save_dispatches_called == True

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 1
    assert save_dispatches_history_history.history[0].timestamp == current
    assert save_dispatches_history_history.history[0].dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_retrieved_planned_dispatch_started_and_existing_started_dispatch_exists_not_in_previous_period_then_existing_started_dispatch_not_extended():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [
    IntelligentDispatchItem(
      current - timedelta(minutes=1),
      current + timedelta(minutes=30),
      1.1,
      None,
      "home"
    )
  ], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 1, last_retrieved)
  existing_dispatches.dispatches.started = [
    SimpleIntelligentDispatchItem(
      current.replace(second=0, microsecond=0) - timedelta(hours=2),
      current.replace(second=0, microsecond=0) - timedelta(hours=1)
    )
  ]
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert len(retrieved_dispatches.dispatches.started) == 2
    assert retrieved_dispatches.dispatches.started[0].start == current.replace(second=0, microsecond=0) - timedelta(hours=2)
    assert retrieved_dispatches.dispatches.started[0].end == current.replace(second=0, microsecond=0) - timedelta(hours=1)

    assert retrieved_dispatches.dispatches.started[1].start == current.replace(second=0, microsecond=0)
    assert retrieved_dispatches.dispatches.started[1].end == current.replace(second=0, microsecond=0) + timedelta(minutes=30)

    assert save_dispatches_called == True

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 1
    assert save_dispatches_history_history.history[0].timestamp == current
    assert save_dispatches_history_history.history[0].dispatches == retrieved_dispatches.dispatches

@pytest.mark.asyncio
async def test_when_existing_started_dispatches_more_than_three_days_old_then_old_started_dispatches_removed():
  expected_dispatches = IntelligentDispatches("SMART_CONTROL_IN_PROGRESS", [
    IntelligentDispatchItem(
      current - timedelta(minutes=1),
      current + timedelta(minutes=30),
      1.1,
      None,
      "home"
    )
  ], [])
  mock_api_called = False
  async def async_mock_get_intelligent_dispatches(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_dispatches
  
  save_dispatches_called = False
  save_dispatches_dispatches = None
  async def async_save_dispatches(*args, **kwargs):
    nonlocal save_dispatches_called, save_dispatches_dispatches
    save_dispatches_called = True
    dispatches, = args
    save_dispatches_dispatches = dispatches

  save_dispatches_history_called = False
  save_dispatches_history_history = None
  async def async_save_dispatches_history(*args, **kwargs):
    nonlocal save_dispatches_history_called, save_dispatches_history_history
    save_dispatches_history_called = True
    history, = args
    save_dispatches_history_history = history
  
  account_info = get_account_info()
  existing_dispatches = IntelligentDispatchesCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_dispatches(), IntelligentDispatchesHistory([]), 1, last_retrieved)
  existing_dispatches.dispatches.started = [
    SimpleIntelligentDispatchItem(
      current.replace(second=0, microsecond=0) - timedelta(days=3, hours=1),
      current.replace(second=0, microsecond=0) - timedelta(days=3)
    )
  ]
  expected_retrieved_dispatches = IntelligentDispatchesCoordinatorResult(current, 1, expected_dispatches, IntelligentDispatchesHistory([]), 1, last_retrieved)
  
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
      True,
      async_save_dispatches,
      async_save_dispatches_history
    )

    assert retrieved_dispatches is not None
    assert retrieved_dispatches.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_dispatches.last_evaluated == expected_retrieved_dispatches.last_evaluated
    assert retrieved_dispatches.dispatches == expected_retrieved_dispatches.dispatches
    assert mock_api_called == True

    assert len(retrieved_dispatches.dispatches.started) == 1
    assert retrieved_dispatches.dispatches.started[0].start == current.replace(second=0, microsecond=0)
    assert retrieved_dispatches.dispatches.started[0].end == current.replace(second=0, microsecond=0) + timedelta(minutes=30)

    assert save_dispatches_called == True

    assert save_dispatches_history_called == True
    assert save_dispatches_history_history is not None
    assert len(save_dispatches_history_history.history) == 1
    assert save_dispatches_history_history.history[0].timestamp == current
    assert save_dispatches_history_history.history[0].dispatches == retrieved_dispatches.dispatches