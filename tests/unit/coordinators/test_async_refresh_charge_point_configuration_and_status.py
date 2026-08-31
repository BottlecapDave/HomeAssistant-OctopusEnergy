from datetime import datetime, timedelta
import pytest
import mock

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.charge_point import OnboardedChargePoint
from custom_components.octopus_energy.charge_point import mock_charge_point_status_and_configuration
from custom_components.octopus_energy.coordinators.charge_point_configuration_and_status import (
  ChargePointCoordinatorResult,
  async_refresh_charge_point_configuration_and_status,
)

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
last_retrieved = datetime.strptime("2023-07-14T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

account_id = "A-XXXXXX"
property_id = "12345"
device_uuid = "00000000-0000-0000-0000-000000000000"

def get_account_info():
  return { "id": account_id }

def get_charge_point() -> OnboardedChargePoint:
  return OnboardedChargePoint.model_validate({
    "deviceUUID": device_uuid,
    "model": "Ohme Home Pro",
    "serialNumber": "ABC123456789",
    "controlMode": "SMART",
    "chargingMethod": "SCHEDULED",
    "operationalState": "NOT_CHARGING",
  })

@pytest.mark.asyncio
async def test_when_account_info_is_none_then_existing_result_returned():
  mock_api_called = False
  async def async_mock_get_charge_point_configuration_and_status(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return get_charge_point()

  existing_result = ChargePointCoordinatorResult(last_retrieved, 1, device_uuid, get_charge_point())

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_charge_point_configuration_and_status=async_mock_get_charge_point_configuration_and_status):
    client = OctopusEnergyApiClient("NOT_REAL")
    result = await async_refresh_charge_point_configuration_and_status(
      current,
      client,
      None,
      property_id,
      device_uuid,
      existing_result,
      False
    )

    assert result == existing_result
    assert mock_api_called == False

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_then_existing_result_returned():
  mock_api_called = False
  async def async_mock_get_charge_point_configuration_and_status(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return get_charge_point()

  account_info = get_account_info()
  existing_result = ChargePointCoordinatorResult(current, 1, device_uuid, get_charge_point())

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_charge_point_configuration_and_status=async_mock_get_charge_point_configuration_and_status):
    client = OctopusEnergyApiClient("NOT_REAL")
    result = await async_refresh_charge_point_configuration_and_status(
      current,
      client,
      account_info,
      property_id,
      device_uuid,
      existing_result,
      False
    )

    assert result == existing_result
    assert mock_api_called == False

@pytest.mark.asyncio
async def test_when_due_and_successful_then_new_result_retrieved():
  expected_charge_point = get_charge_point()
  mock_api_called = False
  async def async_mock_get_charge_point_configuration_and_status(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_charge_point

  account_info = get_account_info()
  existing_result = ChargePointCoordinatorResult(last_retrieved - timedelta(days=60), 1, device_uuid, get_charge_point())

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_charge_point_configuration_and_status=async_mock_get_charge_point_configuration_and_status):
    client = OctopusEnergyApiClient("NOT_REAL")
    result = await async_refresh_charge_point_configuration_and_status(
      current,
      client,
      account_info,
      property_id,
      device_uuid,
      existing_result,
      False
    )

    assert result is not None
    assert result.data == expected_charge_point
    assert result.last_evaluated == current
    assert result.request_attempts == 1
    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_mocked_then_mock_data_used_and_client_not_called():
  mock_api_called = False
  async def async_mock_get_charge_point_configuration_and_status(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return get_charge_point()

  account_info = get_account_info()

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_charge_point_configuration_and_status=async_mock_get_charge_point_configuration_and_status):
    client = OctopusEnergyApiClient("NOT_REAL")
    result = await async_refresh_charge_point_configuration_and_status(
      current,
      client,
      account_info,
      property_id,
      device_uuid,
      None,
      True
    )

    mocked_data = mock_charge_point_status_and_configuration()

    assert result is not None
    assert result.data.deviceUUID == mocked_data.deviceUUID
    assert result.data.model == mocked_data.model
    assert mock_api_called == False

@pytest.mark.asyncio
async def test_when_api_failure_and_existing_result_then_existing_data_returned_with_incremented_attempts_and_error():
  raised_exception = RequestException("foo", [])
  mock_api_called = False
  async def async_mock_get_charge_point_configuration_and_status(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    raise raised_exception

  account_info = get_account_info()
  existing_charge_point = get_charge_point()
  existing_result = ChargePointCoordinatorResult(last_retrieved - timedelta(days=60), 1, device_uuid, existing_charge_point)

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_charge_point_configuration_and_status=async_mock_get_charge_point_configuration_and_status):
    client = OctopusEnergyApiClient("NOT_REAL")
    result = await async_refresh_charge_point_configuration_and_status(
      current,
      client,
      account_info,
      property_id,
      device_uuid,
      existing_result,
      False
    )

    assert result is not None
    assert result.data == existing_charge_point
    assert result.request_attempts == existing_result.request_attempts + 1
    assert result.last_evaluated == existing_result.last_evaluated
    assert result.last_error == raised_exception
    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_api_failure_and_no_existing_result_then_cold_start_failure_returned():
  raised_exception = RequestException("foo", [])
  mock_api_called = False
  async def async_mock_get_charge_point_configuration_and_status(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    raise raised_exception

  account_info = get_account_info()

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_charge_point_configuration_and_status=async_mock_get_charge_point_configuration_and_status):
    client = OctopusEnergyApiClient("NOT_REAL")
    result = await async_refresh_charge_point_configuration_and_status(
      current,
      client,
      account_info,
      property_id,
      device_uuid,
      None,
      False
    )

    assert result is not None
    assert result.data is None
    assert result.device_uuid == device_uuid
    assert result.request_attempts == 2
    assert result.last_error == raised_exception
    assert mock_api_called == True
