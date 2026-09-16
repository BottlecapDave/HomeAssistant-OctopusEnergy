from homeassistant.core import HomeAssistant

from homeassistant.helpers.entity import generate_entity_id, DeviceInfo

from ..const import (
  DATA_INTELLIGENT_DEVICES,
  DOMAIN,
)
from ..api_client.charge_point import OnboardedChargePoint

class BaseOctopusEnergyChargePointSensor:
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint, entity_domain = "sensor"):
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

    # charge_point and IOG entities share this device from within the SAME
    # config entry (both are set up under the account entry), so - unlike
    # the cross-config-entry "primary integration" scenario default_manufacturer
    # /default_model used to exist for (removed in HA core PR #179549: a
    # device now belongs to a single config entry, so there's no primary
    # integration left to defer to, and passing those deprecated fields
    # just logs a warning) - HA itself won't arbitrate a conflict between
    # our own two entity families here. So we do it ourselves: only supply
    # manufacturer/model when an IOG-managed device with this exact
    # identifier genuinely exists for this account (i.e. IOG really is
    # managing this same physical Octopus charger, not a different one set
    # up separately) - otherwise there's no other entity to supply these
    # fields, and no clash risk either since a fresh (non-matching)
    # identifier can't merge with anything else.
    intelligent_devices_result = hass.data.get(DOMAIN, {}).get(account_id, {}).get(DATA_INTELLIGENT_DEVICES)
    intelligent_device_ids = (
      { device.id for device in intelligent_devices_result.devices }
      if intelligent_devices_result is not None else set()
    )
    has_matching_intelligent_device = device_identifier in intelligent_device_ids

    device_info_kwargs = {
      "identifiers": {(DOMAIN, device_identifier)},
      "connections": set(),
      "sw_version": charge_point.firmwareVersion,
      "serial_number": charge_point.serialNumber,
    }

    if not has_matching_intelligent_device:
      device_info_kwargs["manufacturer"] = "Octopus"
      device_info_kwargs["model"] = charge_point.model

    self._attr_device_info = DeviceInfo(**device_info_kwargs)
