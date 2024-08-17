import pytest

from custom_components.octopus_energy.target_rates import compare_config
from custom_components.octopus_energy.const import CONFIG_TARGET_HOURS, CONFIG_TARGET_TYPE

@pytest.mark.asyncio
@pytest.mark.parametrize("existing_config,expected_result",[
  (None, False),
  ({}, False),
  ({ CONFIG_TARGET_HOURS: 1 }, False),
  ({ CONFIG_TARGET_HOURS: 2, CONFIG_TARGET_TYPE: "Continuous" }, False),
  ({ CONFIG_TARGET_HOURS: 1, CONFIG_TARGET_TYPE: "Intermittent" }, False),
  ({ CONFIG_TARGET_HOURS: 1, CONFIG_TARGET_TYPE: "Continuous" }, True),
  ({ CONFIG_TARGET_HOURS: 1, CONFIG_TARGET_TYPE: "Continuous", "Something": "else" }, True),
])
async def test_when_config_is_compared_then_expected_value_is_returned(existing_config, expected_result):
  current_config = {
    CONFIG_TARGET_HOURS: 1,
    CONFIG_TARGET_TYPE: "Continuous"
  }

  actual_result = compare_config(current_config, existing_config)
  assert actual_result == expected_result