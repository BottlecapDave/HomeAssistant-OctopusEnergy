from custom_components.octopus_energy.charge_point.base import BaseOctopusEnergyChargePointSensor
from custom_components.octopus_energy.api_client.charge_point import OnboardedChargePoint
from custom_components.octopus_energy.const import DOMAIN

charge_point_id = "00000000-0000-0000-0000-000000000000"
external_device_id = "external-device-1"

class FakeStates:
  def async_available(self, entity_id):
    return True

class FakeHass:
  def __init__(self):
    self.data = {}
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
    "onboarding": { "accountNumber": "A-XXXXXX", "propertyId": "12345", "externalDeviceId": external_device_id },
  })

def test_when_created_then_manufacturer_and_model_are_supplied_as_defaults_only():
  # Arrange
  hass = FakeHass()

  # Act
  sensor = ConcreteChargePointSensor(hass, charge_point_id, get_charge_point())

  # Assert - default_manufacturer/default_model, NOT manufacturer/model, so
  # Home Assistant's device registry only applies them when no other entity
  # (e.g. an IOG entity sharing this device) has already set a real value.
  assert "manufacturer" not in sensor._attr_device_info
  assert "model" not in sensor._attr_device_info
  assert sensor._attr_device_info["default_manufacturer"] == "Octopus"
  assert sensor._attr_device_info["default_model"] == "Ohme Home Pro"
  assert sensor._attr_device_info["identifiers"] == {(DOMAIN, external_device_id)}
  assert sensor._attr_device_info["sw_version"] == "1.2.3"
  assert sensor._attr_device_info["serial_number"] == "ABC123456789"

def test_when_onboarding_missing_external_device_id_then_falls_back_to_serial_number():
  # Arrange
  hass = FakeHass()
  charge_point = OnboardedChargePoint.model_validate({
    "deviceUUID": charge_point_id,
    "model": "Ohme Home Pro",
    "serialNumber": "ABC123456789",
  })

  # Act
  sensor = ConcreteChargePointSensor(hass, charge_point_id, charge_point)

  # Assert
  assert sensor._attr_device_info["identifiers"] == {(DOMAIN, "charge_point_ABC123456789")}
