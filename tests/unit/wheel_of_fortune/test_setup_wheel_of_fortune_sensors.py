import mock
import pytest

from custom_components.octopus_energy import sensor


@pytest.mark.parametrize("account_info,expected_entities", [
  ({"electricity_meter_points": [{}], "gas_meter_points": [{}]}, ["electricity", "gas"]),
  ({"electricity_meter_points": [{}], "gas_meter_points": []}, ["electricity"]),
  ({"electricity_meter_points": [], "gas_meter_points": [{}]}, ["gas"]),
  ({"electricity_meter_points": [], "gas_meter_points": []}, []),
  (None, ["electricity", "gas"]),
])
def test_when_setup_then_spin_sensors_only_created_for_supplies_on_account(account_info, expected_entities):
  with mock.patch.object(sensor, "OctopusEnergyWheelOfFortuneElectricitySpins", return_value="electricity"), \
       mock.patch.object(sensor, "OctopusEnergyWheelOfFortuneGasSpins", return_value="gas"):
    result = sensor.setup_wheel_of_fortune_sensors(None, None, None, "A-123", account_info)

  assert result == expected_entities
