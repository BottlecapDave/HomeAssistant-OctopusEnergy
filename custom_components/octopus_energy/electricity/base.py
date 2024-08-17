from homeassistant.core import HomeAssistant

from homeassistant.helpers.entity import generate_entity_id, DeviceInfo

from ..const import (
  DOMAIN,
)

class OctopusEnergyElectricitySensor:
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, meter, point, entity_domain = "sensor"):
    """Init sensor"""
    self._point = point
    self._meter = meter

    self._mpan = point["mpan"]
    self._serial_number = meter["serial_number"]
    self._is_export = meter["is_export"]
    self._is_smart_meter = meter["is_smart_meter"]
    self._export_id_addition = "_export" if self._is_export == True else ""
    self._export_name_addition = "Export " if self._is_export == True else ""

    self._attributes = {
      "mpan": self._mpan,
      "serial_number": self._serial_number,
      "is_export": self._is_export,
      "is_smart_meter": self._is_smart_meter
    }

    self.entity_id = generate_entity_id(entity_domain + ".{}", self.unique_id, hass=hass)

    export_name_suffix = " Export" if self._is_export == True else ""
    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, f"electricity_{self._serial_number}_{self._mpan}")},
      name=f"Electricity Meter{export_name_suffix}",
      connections=set(),
      manufacturer=self._meter["manufacturer"],
      model=self._meter["model"],
      sw_version=self._meter["firmware"]
    )