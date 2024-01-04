import pytest

from custom_components.octopus_energy.intelligent import get_intelligent_features

@pytest.mark.asyncio
@pytest.mark.parametrize("provider,expected_bump_charge_supported,expected_charge_limit_supported,expected_planned_dispatches_supported,expected_ready_time_supported,expected_smart_charge_supported",[
  ("DAIKIN", True, True, True, True, True),
  ("ECOBEE", True, True, True, True, True),
  ("ENERGIZER", True, True, True, True, True),
  ("ENPHASE", True, True, True, True, True),
  ("ENODE", True, True, True, True, True),
  ("GIVENERGY", True, True, True, True, True),
  ("HUAWEI", True, True, True, True, True),
  ("JEDLIX", True, True, True, True, True),
  ("MYENERGI", True, True, True, True, True),
  ("OCPP_WALLBOX", True, True, True, True, True),
  ("SENSI", True, True, True, True, True),
  ("SMARTCAR", True, True, True, True, True),
  ("TESLA", True, True, True, True, True),
  ("SMART_PEAR", True, True, True, True, True),
  ("OHME", False, False, False, False, False),
  ("DAIKIN".lower(), True, True, True, True, True),
  ("ECOBEE".lower(), True, True, True, True, True),
  ("ENERGIZER".lower(), True, True, True, True, True),
  ("ENPHASE".lower(), True, True, True, True, True),
  ("ENODE".lower(), True, True, True, True, True),
  ("GIVENERGY".lower(), True, True, True, True, True),
  ("HUAWEI".lower(), True, True, True, True, True),
  ("JEDLIX".lower(), True, True, True, True, True),
  ("MYENERGI".lower(), True, True, True, True, True),
  ("OCPP_WALLBOX".lower(), True, True, True, True, True),
  ("SENSI".lower(), True, True, True, True, True),
  ("SMARTCAR".lower(), True, True, True, True, True),
  ("TESLA".lower(), True, True, True, True, True),
  ("SMART_PEAR".lower(), True, True, True, True, True),
  ("OHME".lower(), False, False, False, False, False),
])
async def test_when_provider_provided_then_expected_features_returned(
  provider: str,
  expected_bump_charge_supported: bool,
  expected_charge_limit_supported: bool,
  expected_planned_dispatches_supported: bool,
  expected_ready_time_supported: bool,
  expected_smart_charge_supported: bool,
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