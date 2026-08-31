from homeassistant.core import HomeAssistant

from homeassistant.helpers.entity import generate_entity_id, DeviceInfo

from ..const import (
  DOMAIN,
)
from ..api_client.charge_point import OnboardedChargePoint

class BaseOctopusEnergyChargePointSensor:
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, charge_point_id: str, charge_point: OnboardedChargePoint, entity_domain = "sensor"):
    """Init sensor"""
    self._charge_point = charge_point
    self._charge_point_id = charge_point_id

    self._attributes = {
      "bluetooth_low_energy_pin": charge_point.bluetoothLowEnergyPin,
      "simcard_identifier": charge_point.simcardIdentifier,
    }

    if charge_point.onboarding is not None:
      self._attributes["external_device_id"] = charge_point.onboarding.externalDeviceId
      self._attributes["onboarded_at"] = charge_point.onboarding.onboardedAt

    self.entity_id = generate_entity_id(entity_domain + ".{}", self.unique_id, hass=hass)

    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, f"charge_point_{charge_point.serialNumber}")},
      # NOT "Octopus Charge (...)" - collides with the existing IOG device's name
      name=f"Octopus Charge Point ({charge_point.model})",
      connections=set(),
      manufacturer="Octopus",
      model=charge_point.model,
      sw_version=charge_point.firmwareVersion,
      serial_number=charge_point.serialNumber,
    )
