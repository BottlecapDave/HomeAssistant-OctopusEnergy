from homeassistant.helpers.entity import DeviceInfo

from ..const import (
  DOMAIN,
)
from ..api_client.intelligent_device import IntelligentDevice

class OctopusEnergyIntelligentSensor:
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})
  
  def __init__(self, device: IntelligentDevice):
    """Init sensor"""

    self._device = device
    self._attr_device_info = DeviceInfo(
      identifiers={
        (DOMAIN, self._device.id if self._device.id is not None else "charger-1")
      },
      name="Charger" if self._device.is_charger else "Vehicle",
      connections=set(),
      manufacturer=self._device.make,
      model=self._device.model
    )