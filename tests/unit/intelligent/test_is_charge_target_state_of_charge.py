import pytest

from custom_components.octopus_energy.const import INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS, INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES
from custom_components.octopus_energy.intelligent import is_charge_target_state_of_charge

@pytest.mark.parametrize("device_type,expected_result",[
  (INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES, True),
  (INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS, False),
])
def test_when_called_then_expected_result_returned(device_type: str, expected_result: bool):
  # Act
  result = is_charge_target_state_of_charge(device_type)

  # Assert
  assert result == expected_result
