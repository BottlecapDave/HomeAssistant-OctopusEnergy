from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from ...const import (
  DOMAIN,
)

class OctopusEnergyGasSensor(SensorEntity, RestoreEntity):
  def __init__(self, meter, point):
    """Init sensor"""
    self._point = point
    self._meter = meter
    
    self._mprn = point["mprn"]
    self._serial_number = meter["serial_number"]

    self._attributes = {
      "mprn": self._mprn,
      "serial_number": self._serial_number
    }

  @property
  def device_info(self):
    return {
        "identifiers": {
            # Serial numbers/mpan are unique identifiers within a specific domain
            (DOMAIN, f"electricity_{self._serial_number}_{self._mprn}")
        },
        "default_name": "Gas Meter",
        "manufacturer": self._meter["manufacturer"],
        "model": self._meter["model"],
        "sw_version": self._meter["firmware"]
    }