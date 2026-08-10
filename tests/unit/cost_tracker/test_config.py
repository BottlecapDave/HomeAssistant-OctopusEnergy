from custom_components.octopus_energy.config.cost_tracker import (
  get_cost_tracker_unique_id,
  get_cost_tracker_unique_id_from_config,
)
from custom_components.octopus_energy.const import (
  CONFIG_ACCOUNT_ID,
  CONFIG_COST_TRACKER_TARGET_ENTITY_ID,
)


def test_get_cost_tracker_unique_id_uses_account_and_target():
  result = get_cost_tracker_unique_id(
    "A-TEST",
    "sensor.kitchen_heating_energy",
  )

  assert result == "octopus_energy_ct_A-TEST_sensor.kitchen_heating_energy"


def test_get_cost_tracker_unique_id_from_config_uses_canonical_target():
  result = get_cost_tracker_unique_id_from_config({
    CONFIG_ACCOUNT_ID: "A-TEST",
    CONFIG_COST_TRACKER_TARGET_ENTITY_ID: "sensor.kitchen_heating_energy",
  })

  assert result == "octopus_energy_ct_A-TEST_sensor.kitchen_heating_energy"
