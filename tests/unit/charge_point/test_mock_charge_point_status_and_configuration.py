from custom_components.octopus_energy.charge_point import mock_charge_point_status_and_configuration

def test_when_mock_charge_point_status_and_configuration_called_then_valid_data_returned():
  # Act
  result = mock_charge_point_status_and_configuration()

  # Assert
  assert result is not None
  assert result.deviceUUID is not None
  assert result.model is not None
  assert result.serialNumber is not None
  assert result.operationalState in ["CHARGING", "NOT_CHARGING", "UNPLUGGED"]
  assert result.controlMode == "SMART"
  assert result.chargingMethod == "SCHEDULED"

  assert result.onboarding is not None
  assert result.onboarding.externalDeviceId is not None

  assert result.configuration is not None
  assert result.configuration.LEDBrightnessPercentage is not None
  assert result.configuration.isChargeCableAutoLockAvailable == True
