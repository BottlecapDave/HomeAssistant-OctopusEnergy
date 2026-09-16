import random

from ..api_client.charge_point import OnboardedChargePoint

def get_mock_charge_point_id():
  return "00000000-0000-0000-0000-000000000000"

def mock_charge_point_status_and_configuration():
  data = {
    "deviceUUID": get_mock_charge_point_id(),
    "model": "Ohme Home Pro",
    "serialNumber": "ABC123456789",
    "bluetoothLowEnergyPin": "123456",
    "simcardIdentifier": "8944000000000000000",
    "firmwareVersion": "3.6.6",
    "controlMode": "SMART",
    "chargingMethod": "SCHEDULED",
    "operationalState": random.choice(["CHARGING", "NOT_CHARGING", "UNPLUGGED"]),
    "boostEndTime": None,
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

  return OnboardedChargePoint.model_validate(data)
