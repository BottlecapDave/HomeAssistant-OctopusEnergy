from homeassistant.helpers.entity import DeviceInfo

from ..const import (
  DOMAIN,
)
from ..api_client.intelligent_device import IntelligentDevice

class OctopusEnergyIntelligentSensor:
  def __init__(self, device: IntelligentDevice):
    """Init sensor"""

    self._device = device
    self._attr_device_info = DeviceInfo(
      identifiers={
        (DOMAIN, self._device.krakenflexDeviceId if self._device.krakenflexDeviceId is not None else "charger-1")
      },
      name="Charger",
      connections=set(),
      manufacturer=self._device.chargePointMake,
      model=self._device.chargePointModel
    )