from datetime import datetime, timedelta
import pytest
import mock

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, AuthenticationException, ApiException
from custom_components.octopus_energy.coordinators.account import AccountCoordinatorResult, async_refresh_account

current = datetime.strptime("2025-08-30T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
expected_next_refresh = datetime.strptime("2025-08-30T16:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
account_id = "A-123-456-789"

electricity_mpan = "1234567890"
electricity_serial_number = "abc"

gas_mprn = "1234567890"
gas_serial_number = "def"

def get_account_info(is_electricity_active = True, is_gas_active = True):
  return {
    "electricity_meter_points": [
      {
        "mpan": electricity_mpan,
        "meters": [
          {
            "serial_number": electricity_serial_number,
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
            "start": (current - timedelta(days=1)).isoformat() if is_electricity_active else (current - timedelta(days=1)).isoformat(),
            "end": (current + timedelta(seconds=1)).isoformat() if is_electricity_active else (current - timedelta(seconds=1)).isoformat(),
            "tariff_code": "E-1R-SUPER-GREEN-24M-21-07-30-A",
            "product_code": "SUPER-GREEN-24M-21-07-30"
          }
        ]
      }
    ],
    "gas_meter_points": [
      {
        "mprn": gas_mprn,
        "meters": [
          {
            "serial_number": gas_serial_number,
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
            "start": (current - timedelta(days=1)).isoformat() if is_gas_active else (current - timedelta(days=1)).isoformat(),
            "end": (current + timedelta(seconds=1)).isoformat() if is_gas_active else (current - timedelta(seconds=1)).isoformat(),
            "tariff_code": "G-1R-SUPER-GREEN-24M-21-07-30-A",
            "product_code": "SUPER-GREEN-24M-21-07-30"
          }
        ]
      }
    ]
  }

def assert_successful_result(result: AccountCoordinatorResult, expected_account):
  assert result is not None
  assert result.last_evaluated == current
  assert result.account == expected_account
  assert result.next_refresh == expected_next_refresh
  assert result.request_attempts == 1
  assert result.last_error is None

def assert_unsuccessful_result(result: AccountCoordinatorResult, previous_result: AccountCoordinatorResult):
  assert result is not None
  assert result.last_evaluated == previous_result.last_evaluated
  assert result.account == previous_result.account
  assert result.next_refresh == previous_result.next_refresh + timedelta(minutes=1)
  assert result.request_attempts == previous_result.request_attempts + 1
  assert result.last_error is not None

@pytest.mark.asyncio
async def test_when_gas_meter_is_missing_then_event_raised():
  # Arrange
  current_account = get_account_info(is_electricity_active=True, is_gas_active=True)
  previous_result = AccountCoordinatorResult(current - timedelta(days=1), 1, current_account)
  expected_account = get_account_info(is_electricity_active=True, is_gas_active=False)

  mocked_get_account_called = False
  async def mocked_async_get_account(*args, **kwargs):
    nonlocal mocked_get_account_called
    mocked_get_account_called = True
    return expected_account
  
  times_mocked_get_product_called = 0
  async def mocked_async_get_product(*args, **kwargs):
    nonlocal times_mocked_get_product_called
    times_mocked_get_product_called += 1
    return {}
  
  raise_account_not_found_called = False
  def raise_account_not_found(*args, **kwargs):
    nonlocal raise_account_not_found_called
    raise_account_not_found_called = True
    return None
  
  raise_invalid_api_key_called = False
  def raise_invalid_api_key(*args, **kwargs):
    nonlocal raise_invalid_api_key_called
    raise_invalid_api_key_called = True
    return None
  
  times_raise_product_not_found_called = 0
  def raise_product_not_found(*args, **kwargs):
    nonlocal times_raise_product_not_found_called
    times_raise_product_not_found_called += 1
    return None
  
  times_raise_meter_removed_called = 0
  def raise_meter_removed(*args, **kwargs):
    nonlocal times_raise_meter_removed_called
    times_raise_meter_removed_called += 1
    return None
  
  times_raise_meter_added_called = 0
  def raise_meter_added(*args, **kwargs):
    nonlocal times_raise_meter_added_called
    times_raise_meter_added_called += 1
    return None
  
  times_clear_issue_called = 0
  def clear_issue(*args, **kwargs):
    nonlocal times_clear_issue_called
    times_clear_issue_called += 1
    return None

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=mocked_async_get_account, async_get_product=mocked_async_get_product):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_refresh_account(
      current,
      client,
      account_id,
      previous_result,
      raise_account_not_found,
      raise_invalid_api_key,
      raise_product_not_found,
      raise_meter_removed,
      raise_meter_added,
      clear_issue
    )

  # Assert
  assert_successful_result(result, expected_account)

  assert mocked_get_account_called == True
  assert times_mocked_get_product_called == 1
  assert raise_account_not_found_called == False
  assert raise_invalid_api_key_called == False
  assert times_raise_product_not_found_called == 0
  assert times_raise_meter_removed_called == 1
  assert times_raise_meter_added_called == 0
  assert times_clear_issue_called == 2 + 5 # 2 expected, 5 legacy
  
@pytest.mark.asyncio
async def test_when_electricity_meter_is_missing_then_event_raised():
  # Arrange
  current_account = get_account_info(is_electricity_active=True, is_gas_active=True)
  previous_result = AccountCoordinatorResult(current - timedelta(days=1), 1, current_account)
  expected_account = get_account_info(is_electricity_active=False, is_gas_active=True)

  mocked_get_account_called = False
  async def mocked_async_get_account(*args, **kwargs):
    nonlocal mocked_get_account_called
    mocked_get_account_called = True
    return expected_account
  
  times_mocked_get_product_called = 0
  async def mocked_async_get_product(*args, **kwargs):
    nonlocal times_mocked_get_product_called
    times_mocked_get_product_called += 1
    return {}
  
  raise_account_not_found_called = False
  def raise_account_not_found(*args, **kwargs):
    nonlocal raise_account_not_found_called
    raise_account_not_found_called = True
    return None
  
  raise_invalid_api_key_called = False
  def raise_invalid_api_key(*args, **kwargs):
    nonlocal raise_invalid_api_key_called
    raise_invalid_api_key_called = True
    return None
  
  times_raise_product_not_found_called = 0
  def raise_product_not_found(*args, **kwargs):
    nonlocal times_raise_product_not_found_called
    times_raise_product_not_found_called += 1
    return None
  
  times_raise_meter_removed_called = 0
  def raise_meter_removed(*args, **kwargs):
    nonlocal times_raise_meter_removed_called
    times_raise_meter_removed_called += 1
    return None
  
  times_raise_meter_added_called = 0
  def raise_meter_added(*args, **kwargs):
    nonlocal times_raise_meter_added_called
    times_raise_meter_added_called += 1
    return None
  
  times_clear_issue_called = 0
  def clear_issue(*args, **kwargs):
    nonlocal times_clear_issue_called
    times_clear_issue_called += 1
    return None

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=mocked_async_get_account, async_get_product=mocked_async_get_product):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_refresh_account(
      current,
      client,
      account_id,
      previous_result,
      raise_account_not_found,
      raise_invalid_api_key,
      raise_product_not_found,
      raise_meter_removed,
      raise_meter_added,
      clear_issue
    )

  # Assert
  assert_successful_result(result, expected_account)

  assert mocked_get_account_called == True
  assert times_mocked_get_product_called == 1
  assert raise_account_not_found_called == False
  assert raise_invalid_api_key_called == False
  assert times_raise_product_not_found_called == 0
  assert times_raise_meter_removed_called == 1
  assert times_raise_meter_added_called == 0
  assert times_clear_issue_called == 2 + 5 # 2 expected, 5 legacy

@pytest.mark.asyncio
async def test_when_electricity_meter_is_added_then_event_raised():
  # Arrange
  current_account = get_account_info(is_electricity_active=False, is_gas_active=True)
  previous_result = AccountCoordinatorResult(current - timedelta(days=1), 1, current_account)
  expected_account = get_account_info(is_electricity_active=True, is_gas_active=True)

  mocked_get_account_called = False
  async def mocked_async_get_account(*args, **kwargs):
    nonlocal mocked_get_account_called
    mocked_get_account_called = True
    return expected_account
  
  times_mocked_get_product_called = 0
  async def mocked_async_get_product(*args, **kwargs):
    nonlocal times_mocked_get_product_called
    times_mocked_get_product_called += 1
    return {}
  
  raise_account_not_found_called = False
  def raise_account_not_found(*args, **kwargs):
    nonlocal raise_account_not_found_called
    raise_account_not_found_called = True
    return None
  
  raise_invalid_api_key_called = False
  def raise_invalid_api_key(*args, **kwargs):
    nonlocal raise_invalid_api_key_called
    raise_invalid_api_key_called = True
    return None
  
  times_raise_product_not_found_called = 0
  def raise_product_not_found(*args, **kwargs):
    nonlocal times_raise_product_not_found_called
    times_raise_product_not_found_called += 1
    return None
  
  times_raise_meter_removed_called = 0
  def raise_meter_removed(*args, **kwargs):
    nonlocal times_raise_meter_removed_called
    times_raise_meter_removed_called += 1
    return None
  
  times_raise_meter_added_called = 0
  def raise_meter_added(*args, **kwargs):
    nonlocal times_raise_meter_added_called
    times_raise_meter_added_called += 1
    return None
  
  times_clear_issue_called = 0
  def clear_issue(*args, **kwargs):
    nonlocal times_clear_issue_called
    times_clear_issue_called += 1
    return None

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=mocked_async_get_account, async_get_product=mocked_async_get_product):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_refresh_account(
      current,
      client,
      account_id,
      previous_result,
      raise_account_not_found,
      raise_invalid_api_key,
      raise_product_not_found,
      raise_meter_removed,
      raise_meter_added,
      clear_issue
    )

  # Assert
  assert_successful_result(result, expected_account)

  assert mocked_get_account_called == True
  assert times_mocked_get_product_called == 2
  assert raise_account_not_found_called == False
  assert raise_invalid_api_key_called == False
  assert times_raise_product_not_found_called == 0
  assert times_raise_meter_removed_called == 0
  assert times_raise_meter_added_called == 1
  assert times_clear_issue_called == 2 + 5 # 2 expected, 5 legacy

@pytest.mark.asyncio
async def test_when_gas_meter_is_added_then_event_raised():
  # Arrange
  current_account = get_account_info(is_electricity_active=True, is_gas_active=False)
  previous_result = AccountCoordinatorResult(current - timedelta(days=1), 1, current_account)
  expected_account = get_account_info(is_electricity_active=True, is_gas_active=True)

  mocked_get_account_called = False
  async def mocked_async_get_account(*args, **kwargs):
    nonlocal mocked_get_account_called
    mocked_get_account_called = True
    return expected_account
  
  times_mocked_get_product_called = 0
  async def mocked_async_get_product(*args, **kwargs):
    nonlocal times_mocked_get_product_called
    times_mocked_get_product_called += 1
    return {}
  
  raise_account_not_found_called = False
  def raise_account_not_found(*args, **kwargs):
    nonlocal raise_account_not_found_called
    raise_account_not_found_called = True
    return None
  
  raise_invalid_api_key_called = False
  def raise_invalid_api_key(*args, **kwargs):
    nonlocal raise_invalid_api_key_called
    raise_invalid_api_key_called = True
    return None
  
  times_raise_product_not_found_called = 0
  def raise_product_not_found(*args, **kwargs):
    nonlocal times_raise_product_not_found_called
    times_raise_product_not_found_called += 1
    return None
  
  times_raise_meter_removed_called = 0
  def raise_meter_removed(*args, **kwargs):
    nonlocal times_raise_meter_removed_called
    times_raise_meter_removed_called += 1
    return None
  
  times_raise_meter_added_called = 0
  def raise_meter_added(*args, **kwargs):
    nonlocal times_raise_meter_added_called
    times_raise_meter_added_called += 1
    return None
  
  times_clear_issue_called = 0
  def clear_issue(*args, **kwargs):
    nonlocal times_clear_issue_called
    times_clear_issue_called += 1
    return None

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=mocked_async_get_account, async_get_product=mocked_async_get_product):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_refresh_account(
      current,
      client,
      account_id,
      previous_result,
      raise_account_not_found,
      raise_invalid_api_key,
      raise_product_not_found,
      raise_meter_removed,
      raise_meter_added,
      clear_issue
    )

  # Assert
  assert_successful_result(result, expected_account)

  assert mocked_get_account_called == True
  assert times_mocked_get_product_called == 2
  assert raise_account_not_found_called == False
  assert raise_invalid_api_key_called == False
  assert times_raise_product_not_found_called == 0
  assert times_raise_meter_removed_called == 0
  assert times_raise_meter_added_called == 1
  assert times_clear_issue_called == 2 + 5 # 2 expected, 5 legacy
  
@pytest.mark.asyncio
async def test_when_account_info_is_none_then_account_not_found_raised():
  # Arrange
  current_account = get_account_info(is_electricity_active=True, is_gas_active=True)
  previous_result = AccountCoordinatorResult(current - timedelta(days=1), 1, current_account)

  mocked_get_account_called = False
  async def mocked_async_get_account(*args, **kwargs):
    nonlocal mocked_get_account_called
    mocked_get_account_called = True
    return None
  
  times_mocked_get_product_called = 0
  async def mocked_async_get_product(*args, **kwargs):
    nonlocal times_mocked_get_product_called
    times_mocked_get_product_called += 1
    return {}
  
  raise_account_not_found_called = False
  def raise_account_not_found(*args, **kwargs):
    nonlocal raise_account_not_found_called
    raise_account_not_found_called = True
    return None
  
  raise_invalid_api_key_called = False
  def raise_invalid_api_key(*args, **kwargs):
    nonlocal raise_invalid_api_key_called
    raise_invalid_api_key_called = True
    return None
  
  times_raise_product_not_found_called = 0
  def raise_product_not_found(*args, **kwargs):
    nonlocal times_raise_product_not_found_called
    times_raise_product_not_found_called += 1
    return None
  
  times_raise_meter_removed_called = 0
  def raise_meter_removed(*args, **kwargs):
    nonlocal times_raise_meter_removed_called
    times_raise_meter_removed_called += 1
    return None
  
  times_raise_meter_added_called = 0
  def raise_meter_added(*args, **kwargs):
    nonlocal times_raise_meter_added_called
    times_raise_meter_added_called += 1
    return None
  
  times_clear_issue_called = 0
  def clear_issue(*args, **kwargs):
    nonlocal times_clear_issue_called
    times_clear_issue_called += 1
    return None

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=mocked_async_get_account, async_get_product=mocked_async_get_product):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_refresh_account(
      current,
      client,
      account_id,
      previous_result,
      raise_account_not_found,
      raise_invalid_api_key,
      raise_product_not_found,
      raise_meter_removed,
      raise_meter_added,
      clear_issue
    )

  # Assert
  assert result == previous_result
  assert raise_account_not_found_called == True
  assert mocked_get_account_called == True
  assert times_mocked_get_product_called == 0
  assert raise_invalid_api_key_called == False
  assert times_raise_product_not_found_called == 0
  assert times_raise_meter_removed_called == 0
  assert times_raise_meter_added_called == 0
  assert times_clear_issue_called == 0

@pytest.mark.asyncio
async def test_when_authentication_exception_raised_then_invalid_api_key_raised():
  # Arrange
  current_account = get_account_info(is_electricity_active=True, is_gas_active=True)
  previous_result = AccountCoordinatorResult(current - timedelta(days=1), 1, current_account)

  mocked_get_account_called = False
  async def mocked_async_get_account(*args, **kwargs):
    nonlocal mocked_get_account_called
    mocked_get_account_called = True
    raise AuthenticationException("Invalid API key", [])
  
  times_mocked_get_product_called = 0
  async def mocked_async_get_product(*args, **kwargs):
    nonlocal times_mocked_get_product_called
    times_mocked_get_product_called += 1
    return {}
  
  raise_account_not_found_called = False
  def raise_account_not_found(*args, **kwargs):
    nonlocal raise_account_not_found_called
    raise_account_not_found_called = True
    return None
  
  raise_invalid_api_key_called = False
  def raise_invalid_api_key(*args, **kwargs):
    nonlocal raise_invalid_api_key_called
    raise_invalid_api_key_called = True
    return None
  
  times_raise_product_not_found_called = 0
  def raise_product_not_found(*args, **kwargs):
    nonlocal times_raise_product_not_found_called
    times_raise_product_not_found_called += 1
    return None
  
  times_raise_meter_removed_called = 0
  def raise_meter_removed(*args, **kwargs):
    nonlocal times_raise_meter_removed_called
    times_raise_meter_removed_called += 1
    return None
  
  times_raise_meter_added_called = 0
  def raise_meter_added(*args, **kwargs):
    nonlocal times_raise_meter_added_called
    times_raise_meter_added_called += 1
    return None
  
  times_clear_issue_called = 0
  def clear_issue(*args, **kwargs):
    nonlocal times_clear_issue_called
    times_clear_issue_called += 1
    return None

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=mocked_async_get_account, async_get_product=mocked_async_get_product):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_refresh_account(
      current,
      client,
      account_id,
      previous_result,
      raise_account_not_found,
      raise_invalid_api_key,
      raise_product_not_found,
      raise_meter_removed,
      raise_meter_added,
      clear_issue
    )

  # Assert
  assert_unsuccessful_result(result, previous_result)

  assert mocked_get_account_called == True
  assert times_mocked_get_product_called == 0
  assert raise_account_not_found_called == False
  assert raise_invalid_api_key_called == True
  assert times_raise_product_not_found_called == 0
  assert times_raise_meter_removed_called == 0
  assert times_raise_meter_added_called == 0
  assert times_clear_issue_called == 0

@pytest.mark.asyncio
async def test_when_api_exception_raised_then_previous_account_returned_with_error():
  # Arrange
  current_account = get_account_info(is_electricity_active=True, is_gas_active=True)
  previous_result = AccountCoordinatorResult(current - timedelta(days=1), 1, current_account)

  mocked_get_account_called = False
  async def mocked_async_get_account(*args, **kwargs):
    nonlocal mocked_get_account_called
    mocked_get_account_called = True
    raise ApiException("API Error")
  
  times_mocked_get_product_called = 0
  async def mocked_async_get_product(*args, **kwargs):
    nonlocal times_mocked_get_product_called
    times_mocked_get_product_called += 1
    return {}
  
  raise_account_not_found_called = False
  def raise_account_not_found(*args, **kwargs):
    nonlocal raise_account_not_found_called
    raise_account_not_found_called = True
    return None
  
  raise_invalid_api_key_called = False
  def raise_invalid_api_key(*args, **kwargs):
    nonlocal raise_invalid_api_key_called
    raise_invalid_api_key_called = True
    return None
  
  times_raise_product_not_found_called = 0
  def raise_product_not_found(*args, **kwargs):
    nonlocal times_raise_product_not_found_called
    times_raise_product_not_found_called += 1
    return None
  
  times_raise_meter_removed_called = 0
  def raise_meter_removed(*args, **kwargs):
    nonlocal times_raise_meter_removed_called
    times_raise_meter_removed_called += 1
    return None
  
  times_raise_meter_added_called = 0
  def raise_meter_added(*args, **kwargs):
    nonlocal times_raise_meter_added_called
    times_raise_meter_added_called += 1
    return None
  
  times_clear_issue_called = 0
  def clear_issue(*args, **kwargs):
    nonlocal times_clear_issue_called
    times_clear_issue_called += 1
    return None

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=mocked_async_get_account, async_get_product=mocked_async_get_product):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_refresh_account(
      current,
      client,
      account_id,
      previous_result,
      raise_account_not_found,
      raise_invalid_api_key,
      raise_product_not_found,
      raise_meter_removed,
      raise_meter_added,
      clear_issue
    )

  # Assert
  assert_unsuccessful_result(result, previous_result)

  assert mocked_get_account_called == True
  assert times_mocked_get_product_called == 0
  assert raise_account_not_found_called == False
  assert raise_invalid_api_key_called == False
  assert times_raise_product_not_found_called == 0
  assert times_raise_meter_removed_called == 0
  assert times_raise_meter_added_called == 0
  assert times_clear_issue_called == 0

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_future_then_existing_account_returned():
  # Arrange
  current_account = get_account_info(is_electricity_active=True, is_gas_active=True)
  # Set next_refresh to a future time
  previous_result = AccountCoordinatorResult(current, 1, current_account)
  
  mocked_get_account_called = False
  async def mocked_async_get_account(*args, **kwargs):
    nonlocal mocked_get_account_called
    mocked_get_account_called = True
    return current_account
  
  times_mocked_get_product_called = 0
  async def mocked_async_get_product(*args, **kwargs):
    nonlocal times_mocked_get_product_called
    times_mocked_get_product_called += 1
    return {}
  
  raise_account_not_found_called = False
  def raise_account_not_found(*args, **kwargs):
    nonlocal raise_account_not_found_called
    raise_account_not_found_called = True
    return None
  
  raise_invalid_api_key_called = False
  def raise_invalid_api_key(*args, **kwargs):
    nonlocal raise_invalid_api_key_called
    raise_invalid_api_key_called = True
    return None
  
  times_raise_product_not_found_called = 0
  def raise_product_not_found(*args, **kwargs):
    nonlocal times_raise_product_not_found_called
    times_raise_product_not_found_called += 1
    return None
  
  times_raise_meter_removed_called = 0
  def raise_meter_removed(*args, **kwargs):
    nonlocal times_raise_meter_removed_called
    times_raise_meter_removed_called += 1
    return None
  
  times_raise_meter_added_called = 0
  def raise_meter_added(*args, **kwargs):
    nonlocal times_raise_meter_added_called
    times_raise_meter_added_called += 1
    return None
  
  times_clear_issue_called = 0
  def clear_issue(*args, **kwargs):
    nonlocal times_clear_issue_called
    times_clear_issue_called += 1
    return None

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=mocked_async_get_account, async_get_product=mocked_async_get_product):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_refresh_account(
      current,
      client,
      account_id,
      previous_result,
      raise_account_not_found,
      raise_invalid_api_key,
      raise_product_not_found,
      raise_meter_removed,
      raise_meter_added,
      clear_issue
    )

  # Assert
  assert result == previous_result
  
  assert mocked_get_account_called == False
  assert times_mocked_get_product_called == 0
  assert raise_account_not_found_called == False
  assert raise_invalid_api_key_called == False
  assert times_raise_product_not_found_called == 0
  assert times_raise_meter_removed_called == 0
  assert times_raise_meter_added_called == 0
  assert times_clear_issue_called == 0

@pytest.mark.asyncio
async def test_when_product_not_found_then_event_raised():
  # Arrange
  current_account = get_account_info(is_electricity_active=True, is_gas_active=True)
  previous_result = AccountCoordinatorResult(current - timedelta(days=1), 1, current_account)
  expected_account = get_account_info(is_electricity_active=True, is_gas_active=True)

  mocked_get_account_called = False
  async def mocked_async_get_account(*args, **kwargs):
    nonlocal mocked_get_account_called
    mocked_get_account_called = True
    return expected_account
  
  times_mocked_get_product_called = 0
  async def mocked_async_get_product(*args, **kwargs):
    nonlocal times_mocked_get_product_called
    times_mocked_get_product_called += 1
    return None  # Return None to indicate product not found
  
  raise_account_not_found_called = False
  def raise_account_not_found(*args, **kwargs):
    nonlocal raise_account_not_found_called
    raise_account_not_found_called = True
    return None
  
  raise_invalid_api_key_called = False
  def raise_invalid_api_key(*args, **kwargs):
    nonlocal raise_invalid_api_key_called
    raise_invalid_api_key_called = True
    return None
  
  times_raise_product_not_found_called = 0
  def raise_product_not_found(*args, **kwargs):
    nonlocal times_raise_product_not_found_called
    times_raise_product_not_found_called += 1
    return None
  
  times_raise_meter_removed_called = 0
  def raise_meter_removed(*args, **kwargs):
    nonlocal times_raise_meter_removed_called
    times_raise_meter_removed_called += 1
    return None
  
  times_raise_meter_added_called = 0
  def raise_meter_added(*args, **kwargs):
    nonlocal times_raise_meter_added_called
    times_raise_meter_added_called += 1
    return None
  
  times_clear_issue_called = 0
  def clear_issue(*args, **kwargs):
    nonlocal times_clear_issue_called
    times_clear_issue_called += 1
    return None

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=mocked_async_get_account, async_get_product=mocked_async_get_product):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_refresh_account(
      current,
      client,
      account_id,
      previous_result,
      raise_account_not_found,
      raise_invalid_api_key,
      raise_product_not_found,
      raise_meter_removed,
      raise_meter_added,
      clear_issue
    )

  # Assert
  assert_successful_result(result, expected_account)

  assert mocked_get_account_called == True
  assert times_mocked_get_product_called == 2 # One for electricity, one for gas
  assert raise_account_not_found_called == False
  assert raise_invalid_api_key_called == False
  assert times_raise_product_not_found_called == 2 # One for electricity, one for gas
  assert times_raise_meter_removed_called == 0
  assert times_raise_meter_added_called == 0
  assert times_clear_issue_called == 2 + 6 # 2 expected, 6 legacy