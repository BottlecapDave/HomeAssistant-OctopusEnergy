from datetime import datetime, timedelta
import pytest
import mock

from custom_components.octopus_energy.const import REFRESH_RATE_IN_MINUTES_STANDING_CHARGE
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.coordinators.electricity_standing_charges import ElectricityStandingChargeCoordinatorResult, async_refresh_electricity_standing_charges_data

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
period_from = datetime.strptime("2023-07-14T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
period_to = datetime.strptime("2023-07-15T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

tariff_code = "E-1R-SUPER-GREEN-24M-21-07-30-A"
mpan = "1234567890"
serial_number = "abcdefgh"

def get_account_info(is_active_agreement = True):
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
            "end": "2023-08-01T00:00:00+01:00" if is_active_agreement else "2023-09-01T00:00:00+01:00",
            "tariff_code": tariff_code,
            "product_code": "SUPER-GREEN-24M-21-07-30"
          }
        ]
      }
    ]
  }

@pytest.mark.asyncio
async def test_when_account_info_is_none_then_existing_standing_charge_returned():
  expected_standing_charge = {
    "start": period_from,
    "end": period_to,
    "value_inc_vat": 0.30,
    "tariff_code": tariff_code
  }
  mock_api_called = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_standing_charge
  
  account_info = None
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_from, 1, { "start": period_from - timedelta(days=60), "end": period_to - timedelta(days=60), "value_inc_vat": 2, "tariff_code": tariff_code })
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_standing_charge: ElectricityStandingChargeCoordinatorResult = await async_refresh_electricity_standing_charges_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      existing_standing_charge
    )

    assert retrieved_standing_charge == existing_standing_charge
    assert mock_api_called == False

@pytest.mark.asyncio
async def test_when_no_active_standing_charge_then_none_returned():
  expected_standing_charge = {
    "start": period_from,
    "end": period_to,
    "value_inc_vat": 0.30,
    "tariff_code": tariff_code
  }
  mock_api_called = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_standing_charge
  
  account_info = get_account_info(False)
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_from, 1, { "start": period_from - timedelta(days=60), "end": period_to - timedelta(days=60), "value_inc_vat": 2, "tariff_code": tariff_code })
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_standing_charge: ElectricityStandingChargeCoordinatorResult = await async_refresh_electricity_standing_charges_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      existing_standing_charge
    )

    assert retrieved_standing_charge is None
    assert mock_api_called == False

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_past_then_existing_standing_charge_returned():
  current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_standing_charge = {
    "start": period_from,
    "end": period_to,
    "value_inc_vat": 0.30,
    "tariff_code": tariff_code
  }
  mock_api_called = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_standing_charge
  
  account_info = get_account_info()
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(current - timedelta(minutes=4, seconds=59), 1, {
    "start": period_from,
    "end": period_to,
    "value_inc_vat": 0.10,
    "tariff_code": tariff_code
  })
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_standing_charge: ElectricityStandingChargeCoordinatorResult = await async_refresh_electricity_standing_charges_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      existing_standing_charge
    )

    assert retrieved_standing_charge == existing_standing_charge
    assert mock_api_called == False


@pytest.mark.asyncio
@pytest.mark.parametrize("existing_standing_charge",[
  (None),
  (ElectricityStandingChargeCoordinatorResult(period_from, 1, None)),
])
async def test_when_existing_standing_charge_is_none_then_standing_charge_retrieved(existing_standing_charge):
  expected_period_from = current.replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = expected_period_from + timedelta(days=1)
  expected_standing_charge = {
    "start": period_from,
    "end": period_to,
    "value_inc_vat": 0.30
  }
  mock_api_called = False
  requested_period_from = None
  requested_period_to = None
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal requested_period_from, requested_period_to, mock_api_called, expected_standing_charge

    requested_client, requested_product_code, requested_tariff_code, requested_period_from, requested_period_to = args
    mock_api_called = True
    return expected_standing_charge
  
  account_info = get_account_info()
  expected_retrieved_standing_charge = ElectricityStandingChargeCoordinatorResult(current, 1, expected_standing_charge)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_standing_charge: ElectricityStandingChargeCoordinatorResult = await async_refresh_electricity_standing_charges_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      existing_standing_charge
    )

    assert retrieved_standing_charge is not None
    assert retrieved_standing_charge.last_evaluated == expected_retrieved_standing_charge.last_evaluated
    assert retrieved_standing_charge.standing_charge == expected_retrieved_standing_charge.standing_charge
    assert mock_api_called == True
    assert requested_period_from == expected_period_from
    assert requested_period_to == expected_period_to
    
@pytest.mark.asyncio
async def test_when_existing_standing_charge_is_old_then_standing_charge_retrieved():
  expected_standing_charge = {
    "start": period_from,
    "end": period_to,
    "value_inc_vat": 0.30
  }
  mock_api_called = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_standing_charge
  
  account_info = get_account_info()
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_to - timedelta(days=60), 1, { "start": period_from - timedelta(days=60), "end": period_to - timedelta(days=60), "value_inc_vat": 2, "tariff_code": tariff_code })
  expected_retrieved_standing_charge = ElectricityStandingChargeCoordinatorResult(current, 1, expected_standing_charge)
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_standing_charge: ElectricityStandingChargeCoordinatorResult = await async_refresh_electricity_standing_charges_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      existing_standing_charge
    )

    assert retrieved_standing_charge is not None
    assert retrieved_standing_charge.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_STANDING_CHARGE)
    assert retrieved_standing_charge.last_evaluated == expected_retrieved_standing_charge.last_evaluated
    assert retrieved_standing_charge.standing_charge == expected_retrieved_standing_charge.standing_charge
    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_standing_charge_not_retrieved_then_existing_standing_charge_returned():
  mock_api_called = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return None
  
  account_info = get_account_info()
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_from, 1, { "start": period_from - timedelta(days=60), "end": period_to - timedelta(days=60), "value_inc_vat": 2, "tariff_code": tariff_code })
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_standing_charge: ElectricityStandingChargeCoordinatorResult = await async_refresh_electricity_standing_charges_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      existing_standing_charge
    )

    assert retrieved_standing_charge is not None
    assert retrieved_standing_charge.next_refresh == existing_standing_charge.next_refresh + timedelta(minutes=1)
    assert retrieved_standing_charge.last_evaluated == existing_standing_charge.last_evaluated
    assert retrieved_standing_charge.standing_charge == existing_standing_charge.standing_charge
    assert retrieved_standing_charge.request_attempts == existing_standing_charge.request_attempts + 1

    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_exception_thrown_then_existing_standing_charge_returned_and_exception_captured():
  mock_api_called = False
  raised_exception = RequestException("My exception", [])
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    raise raised_exception
  
  account_info = get_account_info()
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_from, 1, { "start": period_from - timedelta(days=60), "end": period_to - timedelta(days=60), "value_inc_vat": 2, "tariff_code": tariff_code })
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_standing_charge: ElectricityStandingChargeCoordinatorResult = await async_refresh_electricity_standing_charges_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      existing_standing_charge
    )

    assert retrieved_standing_charge is not None
    assert retrieved_standing_charge.next_refresh == existing_standing_charge.next_refresh + timedelta(minutes=1)
    assert retrieved_standing_charge.last_evaluated == existing_standing_charge.last_evaluated
    assert retrieved_standing_charge.standing_charge == existing_standing_charge.standing_charge
    assert retrieved_standing_charge.request_attempts == existing_standing_charge.request_attempts + 1
    assert retrieved_standing_charge.last_error == raised_exception

    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_previous_standing_charge_is_current_then_data_is_not_re_retrieved():
  expected_standing_charge = {
    "start": period_from,
    "end": period_to,
    "value_inc_vat": 0.30
  }
  mock_api_called = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_standing_charge
  
  account_info = get_account_info()
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_from, 1, { "start": period_from, "end": period_to, "value_inc_vat": 2, "tariff_code": tariff_code })
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_standing_charge: ElectricityStandingChargeCoordinatorResult = await async_refresh_electricity_standing_charges_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      existing_standing_charge
    )

    assert retrieved_standing_charge is not None
    assert retrieved_standing_charge.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_STANDING_CHARGE)
    assert retrieved_standing_charge.last_evaluated == current
    assert retrieved_standing_charge.standing_charge == existing_standing_charge.standing_charge

    assert mock_api_called == False

@pytest.mark.asyncio
async def test_when_previous_standing_charge_is_current_but_different_tariff_code_then_data_is_retrieved():
  expected_standing_charge = {
    "start": period_from,
    "end": period_to,
    "value_inc_vat": 0.30
  }
  mock_api_called = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_standing_charge
  
  account_info = get_account_info()
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_from, 1, { "start": period_from, "end": period_to, "value_inc_vat": 2, "tariff_code": "not-a-tariff" })
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_standing_charge: ElectricityStandingChargeCoordinatorResult = await async_refresh_electricity_standing_charges_data(
      current,
      client,
      account_info,
      mpan,
      serial_number,
      existing_standing_charge
    )

    assert retrieved_standing_charge is not None
    assert retrieved_standing_charge.next_refresh == current.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_STANDING_CHARGE)
    assert retrieved_standing_charge.last_evaluated == current
    assert retrieved_standing_charge.standing_charge == expected_standing_charge

    assert mock_api_called == True