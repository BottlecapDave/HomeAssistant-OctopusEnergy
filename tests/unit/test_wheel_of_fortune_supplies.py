import mock

from custom_components.octopus_energy.const import (
  CONFIG_MAIN_SUPPLIES_TO_MONITOR,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS,
  CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS,
)
from custom_components.octopus_energy import sensor


def test_setup_wheel_of_fortune_sensors_only_creates_monitored_supply_entities():
  with mock.patch.object(sensor, "OctopusEnergyWheelOfFortuneElectricitySpins", return_value="electricity"), \
       mock.patch.object(sensor, "OctopusEnergyWheelOfFortuneGasSpins", return_value="gas"):
    assert sensor.setup_wheel_of_fortune_sensors(
      None,
      None,
      None,
      "A-123",
      {CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY},
    ) == ["electricity"]

    assert sensor.setup_wheel_of_fortune_sensors(
      None,
      None,
      None,
      "A-123",
      {CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_GAS},
    ) == ["gas"]

    assert sensor.setup_wheel_of_fortune_sensors(
      None,
      None,
      None,
      "A-123",
      {CONFIG_MAIN_SUPPLIES_TO_MONITOR: CONFIG_MAIN_SUPPLIES_TO_MONITOR_ELECTRICITY_AND_GAS},
    ) == ["electricity", "gas"]
