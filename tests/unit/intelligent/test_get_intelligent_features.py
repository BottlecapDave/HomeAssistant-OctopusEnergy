import pytest

from custom_components.octopus_energy.intelligent import get_intelligent_features

@pytest.mark.asyncio
@pytest.mark.parametrize("provider,expected_bump_charge_supported,expected_charge_limit_supported,expected_planned_dispatches_supported,expected_ready_time_supported,expected_smart_charge_supported,expected_default_features",[
  ("DAIKIN", True, True, True, True, True, False),
  ("ECOBEE", True, True, True, True, True, False),
  ("ENERGIZER", True, True, True, True, True, False),
  ("ENPHASE", True, True, True, True, True, False),
  ("ENODE", True, True, True, True, True, False),
  ("FORD", True, True, True, True, True, False),
  ("GIVENERGY", True, True, True, True, True, False),
  ("HUAWEI", True, True, True, True, True, False),
  ("JEDLIX", True, True, True, True, True, False),
  ("MYENERGI", True, True, True, True, True, False),
  ("OCPP_WALLBOX", True, True, True, True, True, False),
  ("SENSI", True, True, True, True, True, False),
  ("SMARTCAR", True, True, True, True, True, False),
  ("TESLA", True, True, True, True, True, False),
  ("SMART_PEAR", True, True, True, True, True, False),
  ("HYPERVOLT", True, True, True, True, True, False),
  ("INDRA", True, True, True, True, True, False),
  ("OHME", False, False, False, False, False, False),
  ("DAIKIN".lower(), True, True, True, True, True, False),
  ("ECOBEE".lower(), True, True, True, True, True, False),
  ("ENERGIZER".lower(), True, True, True, True, True, False),
  ("ENPHASE".lower(), True, True, True, True, True, False),
  ("ENODE".lower(), True, True, True, True, True, False),
  ("FORD".lower(), True, True, True, True, True, False),
  ("GIVENERGY".lower(), True, True, True, True, True, False),
  ("HUAWEI".lower(), True, True, True, True, True, False),
  ("JEDLIX".lower(), True, True, True, True, True, False),
  ("MYENERGI".lower(), True, True, True, True, True, False),
  ("OCPP_WALLBOX".lower(), True, True, True, True, True, False),
  ("SENSI".lower(), True, True, True, True, True, False),
  ("SMARTCAR".lower(), True, True, True, True, True, False),
  ("TESLA".lower(), True, True, True, True, True, False),
  ("SMART_PEAR".lower(), True, True, True, True, True, False),
  ("HYPERVOLT".lower(), True, True, True, True, True, False),
  ("INDRA".lower(), True, True, True, True, True, False),
  ("OHME".lower(), False, False, False, False, False, False),
  # Unexpected providers
  ("unexpected".lower(), False, False, False, False, False, True),
  ("".lower(), False, False, False, False, False, True),
  (None, False, False, False, False, False, True),
])
async def test_when_provider_provided_then_expected_features_returned(
  provider: str,
  expected_bump_charge_supported: bool,
  expected_charge_limit_supported: bool,
  expected_planned_dispatches_supported: bool,
  expected_ready_time_supported: bool,
  expected_smart_charge_supported: bool,
  expected_default_features: bool
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