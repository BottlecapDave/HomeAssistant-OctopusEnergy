from custom_components.octopus_energy.config.cost_tracker import (
  build_cost_tracker_unique_id,
)


def test_build_cost_tracker_unique_id_uses_account_and_target():
  result = build_cost_tracker_unique_id(
    "A-TEST",
    "sensor.kitchen_heating_energy",
  )

  assert result == "octopus_energy_ct_A-TEST_sensor.kitchen_heating_energy"
