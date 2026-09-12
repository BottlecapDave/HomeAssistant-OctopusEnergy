from custom_components.octopus_energy.api_client.charge_point import OnboardedChargePoint

def test_when_valid_dictionary_returned_then_it_can_be_parsed_into_charge_point_object():
  # Arrange
  data = {
    "deviceUUID": "00000000-0000-0000-0000-000000000000",
    "model": "Ohme Home Pro",
    "serialNumber": "ABC123456789",
    "bluetoothLowEnergyPin": "123456",
    "simcardIdentifier": "8944000000000000000",
    "firmwareVersion": "3.6.6",
    "controlMode": "SMART",
    "chargingMethod": "SCHEDULED",
    "operationalState": "CHARGING",
    "boostEndTime": "2025-05-09T18:28:51.628000+00:00",
    "onboarding": {
      "accountNumber": "A-12345678",
      "propertyId": "12345",
      "onboardedAt": "2024-01-01T00:00:00+00:00",
      "externalDeviceId": "00000000-1111-2222-3333-444444444444",
    },
    "configuration": {
      "isRandomDelayEnabled": True,
      "isConnected": True,
      "LEDBrightnessPercentage": 80,
      "isChargeCableAutoLockAvailable": True,
      "isChargeCableAutoLockEnabled": False,
      "isEcoModeEnabled": True,
      "isAwayMode": False,
    }
  }

  # Act
  result = OnboardedChargePoint.model_validate(data)

  # Assert
  assert result is not None
  assert result.deviceUUID == "00000000-0000-0000-0000-000000000000"
  assert result.model == "Ohme Home Pro"
  assert result.serialNumber == "ABC123456789"
  assert result.bluetoothLowEnergyPin == "123456"
  assert result.simcardIdentifier == "8944000000000000000"
  assert result.firmwareVersion == "3.6.6"
  assert result.controlMode == "SMART"
  assert result.chargingMethod == "SCHEDULED"
  assert result.operationalState == "CHARGING"
  assert result.boostEndTime == "2025-05-09T18:28:51.628000+00:00"

  assert result.onboarding is not None
  assert result.onboarding.accountNumber == "A-12345678"
  assert result.onboarding.propertyId == "12345"
  assert result.onboarding.onboardedAt == "2024-01-01T00:00:00+00:00"
  assert result.onboarding.externalDeviceId == "00000000-1111-2222-3333-444444444444"

  assert result.configuration is not None
  assert result.configuration.isRandomDelayEnabled == True
  assert result.configuration.isConnected == True
  assert result.configuration.LEDBrightnessPercentage == 80
  assert result.configuration.isChargeCableAutoLockAvailable == True
  assert result.configuration.isChargeCableAutoLockEnabled == False
  assert result.configuration.isEcoModeEnabled == True
  assert result.configuration.isAwayMode == False

def test_when_charging_method_is_null_then_it_defaults_to_none():
  # Arrange - schema says chargingMethod is non-null, but treat defensively
  data = {
    "deviceUUID": "00000000-0000-0000-0000-000000000000",
    "model": "Ohme Home Pro",
    "serialNumber": "ABC123456789",
    "controlMode": "MANUAL",
    "chargingMethod": None,
    "operationalState": "NOT_CHARGING",
    "boostEndTime": None,
  }

  # Act
  result = OnboardedChargePoint.model_validate(data)

  # Assert
  assert result is not None
  assert result.chargingMethod is None
  assert result.boostEndTime is None
  assert result.onboarding is None
  assert result.configuration is None

def test_when_optional_fields_missing_then_they_default_to_none():
  # Arrange
  data = {
    "deviceUUID": "00000000-0000-0000-0000-000000000000",
  }

  # Act
  result = OnboardedChargePoint.model_validate(data)

  # Assert
  assert result is not None
  assert result.deviceUUID == "00000000-0000-0000-0000-000000000000"
  assert result.model is None
  assert result.serialNumber is None
  assert result.controlMode is None
  assert result.chargingMethod is None
  assert result.operationalState is None
  assert result.boostEndTime is None
  assert result.onboarding is None
  assert result.configuration is None
