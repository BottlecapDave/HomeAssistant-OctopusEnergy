from homeassistant.core import HomeAssistant

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.helpers.entity import generate_entity_id, DeviceInfo

from ..const import (
  DOMAIN,
)

class OctopusEnergyElectricitySensor(SensorEntity, RestoreEntity):
  def __init__(self, hass: HomeAssistant, meter, point):
    """Init sensor"""
    self._point = point
    self._meter = meter

    self._mpan = point["mpan"]
    self._serial_number = meter["serial_number"]
    self._is_export = meter["is_export"]
    self._is_smart_meter = meter["is_smart_meter"]
    self._export_id_addition = "_export" if self._is_export == True else ""
    self._export_name_addition = " Export" if self._is_export == True else ""

    self._attributes = {
      "mpan": self._mpan,
      "serial_number": self._serial_number,
      "is_export": self._is_export,
      "is_smart_meter": self._is_smart_meter
    }

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, f"electricity_{self._serial_number}_{self._mpan}")},
      default_name=f"Electricity Meter{self._export_name_addition}",
      manufacturer=self._meter["manufacturer"],
      model=self._meter["model"],
      sw_version=self._meter["firmware"]
    )