from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from ...const import (
  DOMAIN,
)

class OctopusEnergyIntelligentSensor(RestoreEntity):
  def __init__(self, meter, point):
    """Init sensor"""

    self._attributes = {
    }

  @property
  def device_info(self):
    return {
        "identifiers": {
            # Serial numbers/mpan are unique identifiers within a specific domain
            (DOMAIN, f"electricity_{self._serial_number}_{self._mpan}")
        },
        "default_name": f"Electricity Meter{self._export_name_addition}",
        "manufacturer": self._meter["manufacturer"],
        "model": self._meter["model"],
        "sw_version": self._meter["firmware"]
    }