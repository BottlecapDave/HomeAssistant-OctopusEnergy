from homeassistant.core import HomeAssistant

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.helpers.entity import generate_entity_id, DeviceInfo

from ..const import (
  DOMAIN,
)

class OctopusEnergyGasSensor(SensorEntity, RestoreEntity):
  def __init__(self, hass: HomeAssistant, meter, point):
    """Init sensor"""
    self._point = point
    self._meter = meter
    
    self._mprn = point["mprn"]
    self._serial_number = meter["serial_number"]
    self._is_smart_meter = meter["is_smart_meter"]

    self._attributes = {
      "mprn": self._mprn,
      "serial_number": self._serial_number
    }

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, f"gas_{self._serial_number}_{self._mprn}")},
      default_name="Gas Meter",
      manufacturer=self._meter["manufacturer"],
      model=self._meter["model"],
      sw_version=self._meter["firmware"]
    )