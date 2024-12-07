from datetime import datetime
import logging
from typing import List

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
    PRECISION_TENTHS,
    ATTR_TEMPERATURE
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.climate import (
  ClimateEntity,
  ClimateEntityFeature,
  HVACMode,
  PRESET_NONE,
  PRESET_BOOST,
)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import (BaseOctopusEnergyHeatPumpSensor)
from ..utils.attributes import dict_to_typed_dict
from ..api_client.heat_pump import ConfigurationZone, HeatPump, Sensor, Zone
from ..coordinators.heatpump_configuration_and_status import HeatPumpCoordinatorResult
from ..api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyHeatPumpZone(CoordinatorEntity, BaseOctopusEnergyHeatPumpSensor, ClimateEntity):
  """Sensor for interacting with a heat pump zone."""

  _attr_supported_features = (
    ClimateEntityFeature.TURN_OFF
    | ClimateEntityFeature.TURN_ON
    | ClimateEntityFeature.TARGET_TEMPERATURE
    | ClimateEntityFeature.PRESET_MODE
  )

  _attr_min_temp = 5
  _attr_max_temp = 50
  _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF, HVACMode.AUTO]
  _attr_hvac_mode = None
  _attr_preset_modes = [PRESET_NONE, PRESET_BOOST]
  _attr_preset_mode = None
  _attr_temperature_unit = UnitOfTemperature.CELSIUS
  _attr_target_temperature_step = PRECISION_TENTHS

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, heat_pump_id: str, heat_pump: HeatPump, zone: ConfigurationZone, is_mocked: bool):
    """Init sensor."""
    self._zone = zone
    self._client = client
    self._is_mocked = is_mocked

    # self._attributes = {
    #   "type": zone.configuration.zoneType,
    #   "calling_for_heat": zone.configuration.callForHeat,
    #   "is_enabled": zone.configuration.enabled
    # }

    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyHeatPumpSensor.__init__(self, hass, heat_pump_id, heat_pump, "climate")

    self._state = None
    self._last_updated = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_heat_pump_{self._heat_pump_id}_{self._zone.configuration.code}"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Zone ({self._zone.configuration.displayName}) Heat Pump ({self._heat_pump_id})"
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the previous rate."""

    # self._attributes = {
    #   "type": self._zone.configuration.zoneType,
    #   "calling_for_heat": self._zone.configuration.callForHeat,
    #   "is_enabled": self._zone.configuration.enabled
    # }

    # Find the previous rate. We only need to do this every half an hour
    current = now()
    result: HeatPumpCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if (result is not None and 
        result.data is not None and 
        result.data.octoHeatPumpControllerStatus is not None and
        result.data.octoHeatPumpControllerStatus.zones):
      _LOGGER.debug(f"Updating OctopusEnergyHeatPumpZone for '{self._heat_pump_id}/{self._zone.configuration.code}'")

      zones: List[Zone] = result.data.octoHeatPumpControllerStatus.zones
      for zone in zones:
        if zone.zone == self._zone.configuration.code and zone.telemetry is not None:

          if zone.telemetry.mode == "ON":
            self._attr_hvac_mode = HVACMode.HEAT
            self._attr_preset_mode = PRESET_NONE
          elif zone.telemetry.mode == "OFF":
            self._attr_hvac_mode = HVACMode.OFF
            self._attr_preset_mode = PRESET_NONE
          elif zone.telemetry.mode == "AUTO":
            self._attr_hvac_mode = HVACMode.AUTO
            self._attr_preset_mode = PRESET_NONE
          elif zone.telemetry.mode == "ON":
            self._attr_preset_mode = PRESET_BOOST
          else:
            raise Exception(f"Unexpected heat pump mode detected: {zone.telemetry.mode}")

          self._attr_target_temperature = zone.telemetry.setpointInCelsius

          if (result.data.octoHeatPumpControllerStatus.sensors and self._zone.configuration.primarySensor):
            sensors: List[Sensor] = result.data.octoHeatPumpControllerStatus.sensors
            for sensor in sensors:
              if sensor.code == self._zone.configuration.primarySensor and sensor.telemetry is not None:
                self._attr_current_temperature = sensor.telemetry.temperatureInCelsius
          
          self._attributes["retrieved_at"] = datetime.strptime(zone.telemetry.retrievedAt, "%Y-%m-%dT%H:%M:%S%z")

      self._last_updated = current

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_set_hvac_mode(self, hvac_mode):
    """Set new target hvac mode."""
    # await self._client.async_set_heat_pump_mode()
    self._attr_hvac_mode = hvac_mode
    self.async_write_ha_state()

  async def async_turn_on(self):
    """Turn the entity on."""
    # await self._client.async_set_heat_pump_mode()
    self._attr_hvac_mode = HVACMode.HEAT
    self.async_write_ha_state()

  async def async_turn_off(self):
    """Turn the entity off."""
    # await self._client.async_set_heat_pump_mode()
    self._attr_hvac_mode = HVACMode.OFF
    self.async_write_ha_state()

  async def async_set_preset_mode(self, preset_mode):
    """Set new target preset mode."""
    # await self._client.async_set_heat_pump_mode()
    self._attr_preset_mode = preset_mode
    self.async_write_ha_state()

  async def async_set_temperature(self, **kwargs) -> None:
    """Set new target temperature."""
    temperature = kwargs[ATTR_TEMPERATURE]
    # await self._client.async_set_heat_pump_mode()
    self._attr_target_temperature = temperature
    self.async_write_ha_state()