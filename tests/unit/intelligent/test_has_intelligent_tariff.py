import pytest
from datetime import datetime

from custom_components.octopus_energy.intelligent import has_intelligent_tariff

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")

def get_account_info(tariff_code: str, is_active_agreement = True):
  return {
    "electricity_meter_points": [
      {
        "mpan": "test-mpan",
        "meters": [
          {
            "serial_number": "test-serial-number",
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
async def test_when_account_info_is_none_then_false_returned():
  account_info = None

  # Act
  assert has_intelligent_tariff(current, account_info) == False

@pytest.mark.asyncio
async def test_when_account_info_has_no_electricity_meters_then_false_returned():
  account_info = {
    "electricity_meter_points": []
  }

  # Act
  assert has_intelligent_tariff(current, account_info) == False

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff_code",[
  ("E-1R-INTELLI-VAR-22-10-14-C".upper()),
  ("E-1R-INTELLI-VAR-22-10-14-C".lower()),
])
async def test_when_tariff_code_is_and_not_active_then_true_returned(tariff_code: str):
  account_info = get_account_info(tariff_code, False)

  # Act
  assert has_intelligent_tariff(current, account_info) == False

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff_code",[
  ("E-1R-INTELLI-VAR-22-10-14-C".upper()),
  ("E-1R-INTELLI-VAR-22-10-14-C".lower()),
])
async def test_when_tariff_code_is_valid_and_active_then_true_returned(tariff_code: str):
  account_info = get_account_info(tariff_code, True)

  # Act
  assert has_intelligent_tariff(current, account_info) == True

@pytest.mark.asyncio
async def test_when_tariff_is_invalid_then_false_returned():
  account_info = get_account_info("invalid-tariff-code", True)

  # Act
  assert has_intelligent_tariff(current, account_info) == False