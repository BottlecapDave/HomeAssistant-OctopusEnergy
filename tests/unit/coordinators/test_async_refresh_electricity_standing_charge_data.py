from datetime import datetime, timedelta
import pytest
import mock

from unit import (create_rate_data)

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.coordinators.electricity_standing_charges import ElectricityStandingChargeCoordinatorResult, async_refresh_electricity_standing_charges_data
from custom_components.octopus_energy.const import EVENT_ELECTRICITY_CURRENT_DAY_RATES, EVENT_ELECTRICITY_NEXT_DAY_RATES, EVENT_ELECTRICITY_PREVIOUS_DAY_RATES

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
            "valid_from": "2023-07-01T00:00:00+01:00" if is_active_agreement else "2023-08-01T00:00:00+01:00",
            "valid_to": "2023-08-01T00:00:00+01:00" if is_active_agreement else "2023-09-01T00:00:00+01:00",
            "tariff_code": tariff_code,
            "product": "SUPER-GREEN-24M-21-07-30"
          }
        ]
      }
    ]
  }

@pytest.mark.asyncio
async def test_when_account_info_is_none_then_existing_standing_charge_returned():
  expected_standing_charge = {
    "valid_from": period_from,
    "valid_to": period_to,
    "value_inc_vat": 0.30
  }
  standing_charge_returned = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal standing_charge_returned
    standing_charge_returned = True
    return expected_standing_charge
  
  account_info = None
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_from, create_rate_data(period_from, period_to, [2, 4]))
  
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
    assert standing_charge_returned == False

@pytest.mark.asyncio
async def test_when_no_active_standing_charge_then_none_returned():
  expected_standing_charge = {
    "valid_from": period_from,
    "valid_to": period_to,
    "value_inc_vat": 0.30
  }
  standing_charge_returned = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal standing_charge_returned
    standing_charge_returned = True
    return expected_standing_charge
  
  account_info = get_account_info(False)
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_from, create_rate_data(period_from, period_to, [2, 4]))
  
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
    assert standing_charge_returned == False

@pytest.mark.asyncio
async def test_when_current_is_not_thirty_minutes_then_existing_standing_charge_returned():
  for minute in range(60):
    if minute == 0 or minute == 30:
      continue

    current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z").replace(minute=minute)
    expected_standing_charge = {
      "valid_from": period_from,
      "valid_to": period_to,
      "value_inc_vat": 0.30
    }
    standing_charge_returned = False
    async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
      nonlocal standing_charge_returned
      standing_charge_returned = True
      return expected_standing_charge
    
    account_info = get_account_info()
    existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_from, {
      "valid_from": period_from,
      "valid_to": period_to,
      "value_inc_vat": 0.10
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
      assert standing_charge_returned == False


@pytest.mark.asyncio
async def test_when_existing_standing_charge_is_none_then_standing_charge_retrieved():
  expected_period_from = current.replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = expected_period_from + timedelta(days=1)
  expected_standing_charge = {
    "valid_from": period_from,
    "valid_to": period_to,
    "value_inc_vat": 0.30
  }
  standing_charge_returned = False
  requested_period_from = None
  requested_period_to = None
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal requested_period_from, requested_period_to, standing_charge_returned, expected_standing_charge

    requested_client, requested_tariff_code, requested_period_from, requested_period_to = args
    standing_charge_returned = True
    return expected_standing_charge
  
  account_info = get_account_info()
  existing_standing_charge = None
  expected_retrieved_standing_charge = ElectricityStandingChargeCoordinatorResult(current, expected_standing_charge)
  
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
    assert retrieved_standing_charge.last_retrieved == expected_retrieved_standing_charge.last_retrieved
    assert retrieved_standing_charge.standing_charge == expected_retrieved_standing_charge.standing_charge
    assert standing_charge_returned == True
    assert requested_period_from == expected_period_from
    assert requested_period_to == expected_period_to
    
@pytest.mark.asyncio
async def test_when_existing_standing_charge_is_old_then_standing_charge_retrieved():
  expected_period_from = (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_period_to = (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  expected_standing_charge = {
    "valid_from": period_from,
    "valid_to": period_to,
    "value_inc_vat": 0.30
  }
  standing_charge_returned = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal standing_charge_returned
    standing_charge_returned = True
    return expected_standing_charge
  
  account_info = get_account_info()
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_to - timedelta(days=60), create_rate_data(period_from - timedelta(days=60), period_to - timedelta(days=60), [2, 4]))
  expected_retrieved_standing_charge = ElectricityStandingChargeCoordinatorResult(current, expected_standing_charge)
  
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
    assert retrieved_standing_charge.last_retrieved == expected_retrieved_standing_charge.last_retrieved
    assert retrieved_standing_charge.standing_charge == expected_retrieved_standing_charge.standing_charge
    assert standing_charge_returned == True

@pytest.mark.asyncio
async def test_when_standing_charge_not_retrieved_then_existing_standing_charge_returned():
  expected_standing_charge = create_rate_data(period_from, period_to, [1, 2, 3, 4])
  standing_charge_returned = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal standing_charge_returned
    standing_charge_returned = True
    return None
  
  account_info = get_account_info()
  existing_standing_charge = ElectricityStandingChargeCoordinatorResult(period_from, expected_standing_charge)
  
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
    assert standing_charge_returned == True