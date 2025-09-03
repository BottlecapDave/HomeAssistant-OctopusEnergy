import pytest

from custom_components.octopus_energy.intelligent import get_intelligent_features

@pytest.mark.asyncio
@pytest.mark.parametrize("provider,expected_bump_charge_supported,expected_charge_limit_supported,expected_planned_dispatches_supported,expected_ready_time_supported,expected_smart_charge_supported,expected_default_features,expected_current_state_supported",[
  ("DAIKIN", True, True, True, True, True, False, True),
  ("ECOBEE", True, True, True, True, True, False, True),
  ("ENERGIZER", True, True, True, True, True, False, True),
  ("ENPHASE", True, True, True, True, True, False, True),
  ("ENODE", True, True, True, True, True, False, True),
  ("FORD", True, True, True, True, True, False, True),
  ("GIVENERGY", True, True, True, True, True, False, True),
  ("HUAWEI", True, True, True, True, True, False, True),
  ("HUAWEI_V2", True, True, True, True, True, False, True),
  ("JEDLIX", True, True, True, True, True, False, True),
  ("JEDLIX_V2", True, True, True, True, True, False, True),
  ("MYENERGI", True, True, True, True, True, False, True),
  ("MYENERGI_V2", True, True, True, True, True, False, True),
  ("OCPP_WALLBOX", True, True, True, True, True, False, True),
  ("SENSI", True, True, True, True, True, False, True),
  ("SMARTCAR", True, True, True, True, True, False, True),
  ("TESLA", True, True, True, True, True, False, True),
  ("TESLA_V2", True, True, True, True, True, False, True),
  ("SMART_PEAR", True, True, True, True, True, False, True),
  ("HYPERVOLT", True, True, True, True, True, False, True),
  ("INDRA", True, True, True, True, True, False, True),
  ("OHME", False, False, False, False, False, False, False),
  ("OCPP", True, True, True, True, True, False, True),
  ("DAIKIN".lower(), True, True, True, True, True, False, True),
  ("ECOBEE".lower(), True, True, True, True, True, False, True),
  ("ENERGIZER".lower(), True, True, True, True, True, False, True),
  ("ENPHASE".lower(), True, True, True, True, True, False, True),
  ("ENODE".lower(), True, True, True, True, True, False, True),
  ("FORD".lower(), True, True, True, True, True, False, True),
  ("GIVENERGY".lower(), True, True, True, True, True, False, True),
  ("HUAWEI".lower(), True, True, True, True, True, False, True),
  ("HUAWEI_V2".lower(), True, True, True, True, True, False, True),
  ("JEDLIX".lower(), True, True, True, True, True, False, True),
  ("JEDLIX_V2".lower(), True, True, True, True, True, False, True),
  ("MYENERGI".lower(), True, True, True, True, True, False, True),
  ("MYENERGI_V2".lower(), True, True, True, True, True, False, True),
  ("OCPP_WALLBOX".lower(), True, True, True, True, True, False, True),
  ("SENSI".lower(), True, True, True, True, True, False, True),
  ("SMARTCAR".lower(), True, True, True, True, True, False, True),
  ("TESLA".lower(), True, True, True, True, True, False, True),
  ("TESLA_V2".lower(), True, True, True, True, True, False, True),
  ("SMART_PEAR".lower(), True, True, True, True, True, False, True),
  ("HYPERVOLT".lower(), True, True, True, True, True, False, True),
  ("INDRA".lower(), True, True, True, True, True, False, True),
  ("OHME".lower(), False, False, False, False, False, False, False),
  ("OCPP".lower(), True, True, True, True, True, False, True),
  # Unexpected providers
  ("unexpected".lower(), False, False, False, False, False, True, False),
  ("".lower(), False, False, False, False, False, True, False),
  (None, False, False, False, False, False, True, False),
])
async def test_when_provider_provided_then_expected_features_returned(
  provider: str,
  expected_bump_charge_supported: bool,
  expected_charge_limit_supported: bool,
  expected_planned_dispatches_supported: bool,
  expected_ready_time_supported: bool,
  expected_smart_charge_supported: bool,
  expected_default_features: bool,
  expected_current_state_supported: bool
):
  # Act
  result = get_intelligent_features(provider)

  # Assert
  assert result is not None
  assert result.bump_charge_supported == expected_bump_charge_supported 
  assert result.charge_limit_supported == expected_charge_limit_supported 
  assert result.planned_dispatches_supported == expected_planned_dispatches_supported 
  assert result.ready_time_supported == expected_ready_time_supported
  assert result.smart_charge_supported == expected_smart_charge_supported 
  assert result.is_default_features == expected_default_features
  assert result.current_state_supported == expected_current_state_supported