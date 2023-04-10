from homeassistant.helpers.restore_state import RestoreEntity

from ..const import (
  DOMAIN,
)

class OctopusEnergyIntelligentSensor(RestoreEntity):
  def __init__(self, device):
    """Init sensor"""

    self._device = device

  @property
  def device_info(self):
    return {
        "identifiers": {
            (DOMAIN, self._device["krakenflexDeviceId"])
        },
        "default_name": "Charger",
        "manufacturer": self._device["chargePointMake"],
        "model": self._device["chargePointModel"]
    }