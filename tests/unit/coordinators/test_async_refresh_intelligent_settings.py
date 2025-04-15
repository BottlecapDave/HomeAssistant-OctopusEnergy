from datetime import datetime, timedelta, time
import pytest
import mock

from custom_components.octopus_energy.const import REFRESH_RATE_IN_MINUTES_INTELLIGENT
from custom_components.octopus_energy.intelligent import mock_intelligent_settings
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.intelligent_settings import IntelligentSettings
from custom_components.octopus_energy.coordinators.intelligent_settings import IntelligentCoordinatorResult, async_refresh_intelligent_settings

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
last_retrieved = datetime.strptime("2023-07-14T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

product_code = "INTELLI-VAR-22-10-14"
tariff_code = "E-1R-INTELLI-VAR-22-10-14-C"
mpan = "1234567890"
serial_number = "abcdefgh"
device_id = "123ABC"

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
async def test_when_account_info_is_none_then_existing_settings_returned():
  expected_settings = IntelligentSettings(
    False,
    50,
    60,
    time(6,30),
    time(10,10),
  )
  mock_api_called = False
  async def async_mock_get_intelligent_settings(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_settings
  
  account_info = None
  existing_settings = IntelligentCoordinatorResult(last_retrieved, 1, mock_intelligent_settings())
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_settings=async_mock_get_intelligent_settings):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_settings: IntelligentCoordinatorResult = await async_refresh_intelligent_settings(
      current,
      client,
      account_info,
      device_id,
      existing_settings,
      False
    )

    assert retrieved_settings == existing_settings
    assert mock_api_called == False

@pytest.mark.asyncio
async def test_when_not_on_intelligent_tariff_then_none_returned():
  expected_settings = IntelligentSettings(
    False,
    50,
    60,
    time(6,30),
    time(10,10),
  )
  mock_api_called = False
  async def async_mock_get_intelligent_settings(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_settings
  
  account_info = get_account_info(True, active_product_code="GO-18-06-12")
  existing_settings = None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_settings=async_mock_get_intelligent_settings):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_settings: IntelligentCoordinatorResult = await async_refresh_intelligent_settings(
      current,
      client,
      account_info,
      device_id,
      existing_settings,
      False
    )

    assert mock_api_called == False
    assert retrieved_settings is not None
    assert retrieved_settings.settings is None

@pytest.mark.asyncio
async def test_when_device_id_is_none_then_none_returned():
  expected_settings = IntelligentSettings(
    False,
    50,
    60,
    time(6,30),
    time(10,10),
  )
  mock_api_called = False
  async def async_mock_get_intelligent_settings(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_settings
  
  account_info = get_account_info(True)
  existing_settings = None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_settings=async_mock_get_intelligent_settings):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_settings: IntelligentCoordinatorResult = await async_refresh_intelligent_settings(
      current,
      client,
      account_info,
      None,
      existing_settings,
      False
    )

    assert mock_api_called == False
    assert retrieved_settings is not None
    assert retrieved_settings.settings is None

@pytest.mark.asyncio
async def test_when_mock_is_true_then_none_returned():
  mock_api_called = False
  async def async_mock_get_intelligent_settings(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  account_info = get_account_info()
  existing_settings = None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_settings=async_mock_get_intelligent_settings):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_settings: IntelligentCoordinatorResult = await async_refresh_intelligent_settings(
      current,
      client,
      account_info,
      device_id,
      existing_settings,
      True
    )

    assert mock_api_called == True
    assert retrieved_settings is not None
    assert retrieved_settings.settings.charge_limit_weekday == mock_intelligent_settings().charge_limit_weekday
    assert retrieved_settings.settings.charge_limit_weekend == mock_intelligent_settings().charge_limit_weekend
    assert retrieved_settings.settings.ready_time_weekday == mock_intelligent_settings().ready_time_weekday
    assert retrieved_settings.settings.ready_time_weekend == mock_intelligent_settings().ready_time_weekend
    assert retrieved_settings.settings.smart_charge == mock_intelligent_settings().smart_charge

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_then_existing_settings_returned():
  current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_settings = IntelligentSettings(
    False,
    50,
    60,
    time(6,30),
    time(10,10),
  )
  mock_api_called = False
  async def async_mock_get_intelligent_settings(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_settings
  
  account_info = get_account_info()
  existing_settings = IntelligentCoordinatorResult(current, 1, mock_intelligent_settings())
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_settings=async_mock_get_intelligent_settings):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_settings: IntelligentCoordinatorResult = await async_refresh_intelligent_settings(
      current,
      client,
      account_info,
      device_id,
      existing_settings,
      False
    )

    assert retrieved_settings == existing_settings
    assert mock_api_called == False


@pytest.mark.asyncio
@pytest.mark.parametrize("existing_settings",[
  (None),
  (IntelligentCoordinatorResult(last_retrieved, 1, [])),
  (IntelligentCoordinatorResult(last_retrieved, 1, None)),
])
async def test_when_existing_settings_is_none_then_settings_retrieved(existing_settings):
  expected_settings = IntelligentSettings(
    False,
    50,
    60,
    time(6,30),
    time(10,10),
  )
  mock_api_called = False
  async def async_mock_get_intelligent_settings(*args, **kwargs):
    nonlocal mock_api_called, expected_settings
    mock_api_called = True
    return expected_settings
  
  account_info = get_account_info()
  expected_retrieved_settings = IntelligentCoordinatorResult(current, 1, expected_settings)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_settings=async_mock_get_intelligent_settings):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_settings: IntelligentCoordinatorResult = await async_refresh_intelligent_settings(
      current,
      client,
      account_info,
      device_id,
      existing_settings,
      False
    )

    assert retrieved_settings is not None
    assert retrieved_settings.last_evaluated == expected_retrieved_settings.last_evaluated
    assert retrieved_settings.settings == expected_retrieved_settings.settings
    assert mock_api_called == True
    
@pytest.mark.asyncio
async def test_when_existing_settings_is_old_then_settings_retrieved():
  expected_settings = IntelligentSettings(
    False,
    50,
    60,
    time(6,30),
    time(10,10),
  )
  mock_api_called = False
  async def async_mock_get_intelligent_settings(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_settings
  
  account_info = get_account_info()
  existing_settings = IntelligentCoordinatorResult(last_retrieved - timedelta(days=60), 1, mock_intelligent_settings())
  expected_retrieved_settings = IntelligentCoordinatorResult(current, 1, expected_settings)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_settings=async_mock_get_intelligent_settings):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_settings: IntelligentCoordinatorResult = await async_refresh_intelligent_settings(
      current,
      client,
      account_info,
      device_id,
      existing_settings,
      False
    )

    assert retrieved_settings is not None
    assert retrieved_settings.next_refresh == current.replace(second=0, microsecond=0).replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)
    assert retrieved_settings.last_evaluated == expected_retrieved_settings.last_evaluated
    assert retrieved_settings.settings == expected_retrieved_settings.settings
    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_settings_not_retrieved_then_existing_settings_returned():
  mock_api_called = False
  async def async_mock_get_intelligent_settings(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  account_info = get_account_info()
  existing_settings = IntelligentCoordinatorResult(last_retrieved, 1, IntelligentSettings(
    False,
    50,
    60,
    time(6,30),
    time(10,10),
  ))
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_settings=async_mock_get_intelligent_settings):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_settings: IntelligentCoordinatorResult = await async_refresh_intelligent_settings(
      current,
      client,
      account_info,
      device_id,
      existing_settings,
      False
    )

    assert retrieved_settings is not None
    assert retrieved_settings.next_refresh == existing_settings.next_refresh + timedelta(minutes=1)
    assert retrieved_settings.last_evaluated == existing_settings.last_evaluated
    assert retrieved_settings.settings == existing_settings.settings
    assert retrieved_settings.request_attempts == existing_settings.request_attempts + 1

    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_exception_raised_then_existing_settings_returned_and_exception_captured():
  mock_api_called = False
  raised_exception = RequestException("my error", [])
  async def async_mock_get_intelligent_settings(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    raise raised_exception
  
  account_info = get_account_info()
  existing_settings = IntelligentCoordinatorResult(last_retrieved, 1, IntelligentSettings(
    False,
    50,
    60,
    time(6,30),
    time(10,10),
  ))
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_settings=async_mock_get_intelligent_settings):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_settings: IntelligentCoordinatorResult = await async_refresh_intelligent_settings(
      current,
      client,
      account_info,
      device_id,
      existing_settings,
      False
    )

    assert retrieved_settings is not None
    assert retrieved_settings.next_refresh == existing_settings.next_refresh + timedelta(minutes=1)
    assert retrieved_settings.last_evaluated == existing_settings.last_evaluated
    assert retrieved_settings.settings == existing_settings.settings
    assert retrieved_settings.request_attempts == existing_settings.request_attempts + 1
    assert retrieved_settings.last_error == raised_exception

    assert mock_api_called == True