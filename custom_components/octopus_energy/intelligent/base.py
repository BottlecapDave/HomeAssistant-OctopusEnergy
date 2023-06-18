from homeassistant.helpers.entity import DeviceInfo

from ..const import (
  DOMAIN,
)

class OctopusEnergyIntelligentSensor:
  def __init__(self, device):
    """Init sensor"""

    self._device = device
    self._attr_device_info = DeviceInfo(
      identifiers={
        (DOMAIN, self._device["krakenflexDeviceId"] if "krakenflexDeviceId" in self._device and self._device["krakenflexDeviceId"] is not None else "charger-1")
      },
      default_name="Charger",
      manufacturer=self._device["chargePointMake"],
      model=self._device["chargePointModel"]
    )