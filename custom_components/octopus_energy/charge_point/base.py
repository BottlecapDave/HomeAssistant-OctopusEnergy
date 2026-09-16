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

    # Device-level info (bluetoothLowEnergyPin, simcardIdentifier, onboarding)
    # belongs on the device page via DeviceInfo below, the same way
    # firmwareVersion/model/serialNumber already do - not duplicated as an
    # attribute on every single entity, which is what was here before.
    self._attributes = {}

    self.entity_id = generate_entity_id(entity_domain + ".{}", self.unique_id, hass=hass)

    # Deliberately the SAME device identifier the existing Intelligent
    # Octopus Go (IOG) entities already register under (see
    # intelligent/base.py's `(DOMAIN, self._device.id)`, where
    # `self._device.id` is the IOG device's id - which is the same physical
    # charger's externalDeviceId). This merges onto the existing "Octopus
    # Charge (Electric Vehicle Charger)" device instead of creating a
    # second, separate device for the same physical charger. Falls back to
    # a charge-point-scoped identifier only in the unlikely case onboarding
    # data is missing (would otherwise crash with no external device id).
    device_identifier = (
      charge_point.onboarding.externalDeviceId
      if charge_point.onboarding is not None and charge_point.onboarding.externalDeviceId is not None
      else f"charge_point_{charge_point.serialNumber}"
    )

    # manufacturer/model are supplied as *defaults* (default_manufacturer/
    # default_model), not the direct manufacturer/model fields. Home
    # Assistant's device registry only applies a default_* value when the
    # device doesn't already have a real one set (device.manufacturer is
    # None), and a real (non-default) value from another entity sharing this
    # identifier - e.g. intelligent/base.py's manufacturer=self._device.make,
    # when IOG genuinely manages this same physical charger - always wins,
    # regardless of which entity's setup runs first. This is HA's own
    # built-in mechanism for exactly this "two entities may share a device;
    # only apply my value as a fallback" situation, so charge point and IOG
    # entities can safely share a device without either needing to look up
    # or know anything about the other.
    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, device_identifier)},
      connections=set(),
      default_manufacturer="Octopus",
      default_model=charge_point.model,
      sw_version=charge_point.firmwareVersion,
      serial_number=charge_point.serialNumber,
    )
