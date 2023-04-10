from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from ..const import (
  DOMAIN,
)

class OctopusEnergyIntelligentSensor(RestoreEntity):
  def __init_intelligent_sensor__(self, device):
    """Init sensor"""

    self._device = device

  @property
  def device_info(self):
    return {
        "identifiers": {
            (DOMAIN, self._device["krakenflexDeviceId"])
        },
        "default_name": "",
        "manufacturer": self._device["chargePointMake"],
        "model": self._device["model"]
    }