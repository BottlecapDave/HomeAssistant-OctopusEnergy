from homeassistant.helpers.entity import DeviceInfo

from ..const import (
  DOMAIN,
)
from ..api_client.intelligent_device import IntelligentDevice
from ..intelligent import device_type_to_friendly_string

class OctopusEnergyIntelligentSensor:
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})
  
  def __init__(self, device: IntelligentDevice):
    """Init sensor"""

    self._device = device
    self._attr_device_info = DeviceInfo(
      identifiers={
        (DOMAIN, self._device.id)
      },
      name=f"{self._device.make} {self._device.model} ({device_type_to_friendly_string(self._device.device_type)})",
      connections=set(),
      manufacturer=self._device.make,
      model=self._device.model
    )