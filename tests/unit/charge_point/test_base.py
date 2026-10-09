import mock

from custom_components.octopus_energy.charge_point.base import BaseOctopusEnergyChargePointSensor
from custom_components.octopus_energy.api_client.charge_point import OnboardedChargePoint
from custom_components.octopus_energy.api_client.intelligent_device import IntelligentDevice
from custom_components.octopus_energy.const import DATA_INTELLIGENT_DEVICES, DOMAIN

account_id = "A-XXXXXX"
charge_point_id = "00000000-0000-0000-0000-000000000000"
external_device_id = "external-device-1"

class FakeStates:
  def async_available(self, entity_id):
    return True

class FakeHass:
  def __init__(self, data: dict = None):
    self.data = data if data is not None else {}
    self.states = FakeStates()

class ConcreteChargePointSensor(BaseOctopusEnergyChargePointSensor):
  """Minimal concrete subclass - base.py's unique_id is provided by
  whichever real entity subclasses it in production."""

  @property
  def unique_id(self):
    return f"octopus_energy_charge_point_{self._charge_point_id}_test"

def get_charge_point() -> OnboardedChargePoint:
  return OnboardedChargePoint.model_validate({
    "deviceUUID": charge_point_id,
    "model": "Ohme Home Pro",
    "serialNumber": "ABC123456789",
    "firmwareVersion": "1.2.3",
    "onboarding": { "accountNumber": account_id, "propertyId": "12345", "externalDeviceId": external_device_id },
  })

def get_intelligent_device(id: str) -> IntelligentDevice:
  return IntelligentDevice(id=id, provider="OCTOPUS_ENERGY", make="Ohme", model="Home Pro", vehicleBatterySizeInKwh=None, chargePointPowerInKw=None, device_type="ELECTRIC_VEHICLE_CHARGERS")

def test_when_matching_intelligent_device_exists_then_manufacturer_and_model_not_set():
  # Arrange - a matching IOG device exists for this identifier, so it owns
  # manufacturer/model; charge point must not set conflicting plain values
  # for the same fields (there's no default_* fallback mechanism anymore -
  # see base.py's comment on HA core PR #179549).
  hass = FakeHass({
    DOMAIN: {
      account_id: {
        DATA_INTELLIGENT_DEVICES: mock.Mock(devices=[get_intelligent_device(external_device_id)])
      }
    }
  })

  # Act
  sensor = ConcreteChargePointSensor(hass, account_id, charge_point_id, get_charge_point())

  # Assert
  assert "manufacturer" not in sensor._attr_device_info
  assert "model" not in sensor._attr_device_info
  assert sensor._attr_device_info["identifiers"] == {(DOMAIN, external_device_id)}
  assert sensor._attr_device_info["sw_version"] == "1.2.3"
  assert sensor._attr_device_info["serial_number"] == "ABC123456789"

def test_when_no_matching_intelligent_device_then_manufacturer_and_model_set():
  # Arrange - IOG is configured, but for a different physical device entirely
  hass = FakeHass({
    DOMAIN: {
      account_id: {
        DATA_INTELLIGENT_DEVICES: mock.Mock(devices=[get_intelligent_device("some-other-device-id")])
      }
    }
  })

  # Act
  sensor = ConcreteChargePointSensor(hass, account_id, charge_point_id, get_charge_point())

  # Assert
  assert sensor._attr_device_info["manufacturer"] == "Octopus"
  assert sensor._attr_device_info["model"] == "Ohme Home Pro"

def test_when_no_intelligent_devices_data_at_all_then_manufacturer_and_model_set():
  # Arrange - account has no IOG data at all (e.g. not enrolled)
  hass = FakeHass({ DOMAIN: { account_id: {} } })

  # Act
  sensor = ConcreteChargePointSensor(hass, account_id, charge_point_id, get_charge_point())

  # Assert
  assert sensor._attr_device_info["manufacturer"] == "Octopus"
  assert sensor._attr_device_info["model"] == "Ohme Home Pro"

def test_when_onboarding_missing_external_device_id_then_falls_back_to_serial_number():
  # Arrange
  hass = FakeHass()
  charge_point = OnboardedChargePoint.model_validate({
    "deviceUUID": charge_point_id,
    "model": "Ohme Home Pro",
    "serialNumber": "ABC123456789",
  })

  # Act
  sensor = ConcreteChargePointSensor(hass, account_id, charge_point_id, charge_point)

  # Assert
  assert sensor._attr_device_info["identifiers"] == {(DOMAIN, "charge_point_ABC123456789")}
