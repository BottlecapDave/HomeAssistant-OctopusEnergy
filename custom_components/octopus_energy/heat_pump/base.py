from homeassistant.core import HomeAssistant

from homeassistant.helpers.entity import generate_entity_id, DeviceInfo

from ..const import (
  DOMAIN,
)
from ..api_client.heat_pump import HeatPump, SensorConfiguration

class BaseOctopusEnergyHeatPumpSensor:
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, heat_pump_id: str, heat_pump: HeatPump, entity_domain = "sensor"):
    """Init sensor"""
    self._heat_pump = heat_pump
    self._heat_pump_id = heat_pump_id

    self._attributes = {
    }

    self.entity_id = generate_entity_id(entity_domain + ".{}", self.unique_id, hass=hass)

    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, f"heat_pump_{heat_pump.serialNumber}")},
      name=f"Heat Pump ({heat_pump.serialNumber})",
      connections=set(),
      manufacturer="Octopus" if heat_pump.model is not None and "cosy" in heat_pump.model.lower() else None,
      model=heat_pump.model,
      hw_version=heat_pump.hardwareVersion
    )

class BaseOctopusEnergyHeatPumpSensorSensor(BaseOctopusEnergyHeatPumpSensor):
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, heat_pump_id: str, heat_pump: HeatPump, sensor: SensorConfiguration, entity_domain = "sensor"):
    """Init sensor"""
    self._heat_pump = heat_pump
    self._heat_pump_id = heat_pump_id
    self._sensor = sensor

    self._attributes = {
      "type": sensor.type,
      "code": sensor.code
    }

    self.entity_id = generate_entity_id(entity_domain + ".{}", self.unique_id, hass=hass)

    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, f"heat_pump_sensor_{heat_pump.serialNumber}_{sensor.code}")},
      name=f"Heat Pump Sensor ({sensor.code})",
      connections=set(),
      manufacturer="Octopus" if heat_pump.model is not None and "cosy" in heat_pump.model.lower() else None,
      model=heat_pump.model,
      sw_version=sensor.firmwareVersion,
      hw_version=sensor.type
    )