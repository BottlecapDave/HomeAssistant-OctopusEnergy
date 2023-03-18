from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from ...const import (
  DOMAIN,
)

class OctopusEnergyElectricitySensor(SensorEntity, RestoreEntity):
  def __init__(self, mpan, serial_number, is_export, is_smart_meter):
    """Init sensor"""
    self._mpan = mpan
    self._serial_number = serial_number
    self._is_export = is_export
    self._is_smart_meter = is_smart_meter
    self._export_id_addition = "_export" if self._is_export == True else ""
    self._export_name_addition = " Export" if self._is_export == True else ""

    self._attributes = {
      "mpan": self._mpan,
      "serial_number": self._serial_number,
      "is_export": self._is_export,
      "is_smart_meter": self._is_smart_meter
    }

  @property
  def device_info(self):
    return {
        "identifiers": {
            # Serial numbers/mpan are unique identifiers within a specific domain
            (DOMAIN, f"electricity_{self._serial_number}_{self._mpan}")
        },
        "default_name": "Electricity Meter",
    }