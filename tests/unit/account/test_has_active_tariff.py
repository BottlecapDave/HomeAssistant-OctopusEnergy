import pytest
from datetime import datetime, timedelta

from custom_components.octopus_energy.account import has_active_tariff

current = datetime.strptime("2022-02-12T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

def create_point(agreement_start_offset: int, agreement_end_offset: int, meters: list = [{}]):
  return {
    "meters": meters,
    "agreements": [
      {
        "start": (current + timedelta(days=agreement_start_offset)).isoformat(),
        "end": (current + timedelta(days=agreement_end_offset)).isoformat(),
        "tariff_code": "E-1R-SUPER-GREEN-24M-21-07-30-A",
        "product_code": "SUPER-GREEN-24M-21-07-30"
      }
    ]
  }

@pytest.mark.parametrize("electricity_points,gas_points,expected",[
  ([], [], False),
  ([create_point(-1, 1)], [], True),
  ([], [create_point(-1, 1)], True),
  ([create_point(-10, -5)], [create_point(5, 10)], False),
  ([create_point(-10, -5)], [create_point(-1, 1)], True),
  ([create_point(-1, 1, [])], [], False),
])
def test_when_meter_points_provided_then_active_tariff_detected(electricity_points: list, gas_points: list, expected: bool):
  account_info = { "electricity_meter_points": electricity_points, "gas_meter_points": gas_points }
  assert has_active_tariff(current, account_info) == expected

def test_when_account_info_is_none_then_false_returned():
  assert has_active_tariff(current, None) == False
