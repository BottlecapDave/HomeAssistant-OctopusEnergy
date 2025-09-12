from datetime import datetime, timedelta
import logging
from typing import List

from homeassistant.util.dt import (utcnow)
from homeassistant.exceptions import ServiceValidationError

from homeassistant.const import (
    UnitOfTemperature,
    PRECISION_HALVES,
    ATTR_TEMPERATURE,
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
    STATE_HEAT_PUMP,
    STATE_HIGH_DEMAND,
    STATE_ELECTRIC
)

from .base import (BaseOctopusEnergyHeatPumpSensor)
from ..utils.attributes import dict_to_typed_dict
from ..api_client.heat_pump import ConfigurationZone, HeatPump, Sensor, Zone
from ..coordinators.heat_pump_configuration_and_status import HeatPumpCoordinatorResult
from ..api_client import OctopusEnergyApiClient
from ..const import DEFAULT_BOOST_TEMPERATURE_WATER, DOMAIN

_LOGGER = logging.getLogger(__name__)

OE_TO_HA_STATE = {
    "AUTO": STATE_HEAT_PUMP,
    "BOOST": STATE_HIGH_DEMAND,
    "ON": STATE_ELECTRIC,
    "OFF": STATE_OFF,
}

HA_TO_OE_STATE = {
    STATE_HEAT_PUMP: "AUTO",
    STATE_HIGH_DEMAND: "BOOST",
    STATE_ELECTRIC: "ON",
    STATE_OFF: "OFF",
}

class OctopusEnergyHeatPumpWaterHeater(CoordinatorEntity, BaseOctopusEnergyHeatPumpSensor, WaterHeaterEntity):
  """Sensor for interacting with a heat pump water heater zone."""

  _attr_supported_features = (
    WaterHeaterEntityFeature.ON_OFF
    | WaterHeaterEntityFeature.TARGET_TEMPERATURE
    | WaterHeaterEntityFeature.OPERATION_MODE
  )

  _attr_operation_list = [STATE_ELECTRIC, STATE_OFF, STATE_HEAT_PUMP, STATE_HIGH_DEMAND]
  _attr_current_operation = None
  _attr_temperature_unit = UnitOfTemperature.CELSIUS
  _attr_precision = PRECISION_HALVES

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, account_id: str, heat_pump_id: str, heat_pump: HeatPump, zone: ConfigurationZone, is_mocked: bool):
    """Init sensor."""
    self._zone = zone
    self._account_id = account_id
    self._client = client
    self._is_mocked = is_mocked
    self._end_timestamp = None

    self._attr_min_temp = 40
    self._attr_max_temp = 60

    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyHeatPumpSensor.__init__(self, hass, heat_pump_id, heat_pump, "water_heater")

    self._state = None
    self._last_updated = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_heat_pump_{self._heat_pump_id}"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Zone ({self._zone.configuration.displayName}) Heat Pump ({self._heat_pump_id})"
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the previous rate."""

    current = now()
    result: HeatPumpCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None    
    if (result is not None and 
        result.data is not None and 
        result.data.octoHeatPumpControllerStatus is not None and
        result.data.octoHeatPumpControllerStatus.zones and
        (self._last_updated is None or self._last_updated < result.last_retrieved)):
      _LOGGER.debug(f"Updating OctopusEnergyHeatPumpWaterHeater for '{self._heat_pump_id}/{self._zone.configuration.code}'")

      zones: List[Zone] = result.data.octoHeatPumpControllerStatus.zones
      for zone in zones:
        if zone.telemetry is not None and zone.zone == self._zone.configuration.code and zone.telemetry.mode is not None:

          if zone.telemetry.mode in OE_TO_HA_STATE:
            self._attr_current_operation = OE_TO_HA_STATE[zone.telemetry.mode]
          else:
            raise Exception(f"Unexpected heat pump mode detected: {zone.telemetry.mode}")

          self._attr_target_temperature = None
          if zone.telemetry.setpointInCelsius is not None and zone.telemetry.setpointInCelsius > 0:
            self._attr_target_temperature = zone.telemetry.setpointInCelsius

          if result.data.octoHeatPumpControllerStatus.sensors and self._zone.configuration.primarySensor:
            sensors: List[Sensor] = result.data.octoHeatPumpControllerStatus.sensors
            for sensor in sensors:
              if sensor.code == self._zone.configuration.primarySensor and sensor.telemetry is not None:
                self._attr_current_temperature = sensor.telemetry.temperatureInCelsius
                self._attr_current_humidity = sensor.telemetry.humidityPercentage

          if result.data.octoHeatPumpControllerConfiguration is not None and result.data.octoHeatPumpControllerConfiguration.zones:
            configs: List[ConfigurationZone] = result.data.octoHeatPumpControllerConfiguration.zones
            for config in configs:
              if config.configuration is not None and config.configuration.code == self._zone.configuration.code and config.configuration.currentOperation is not None:
                self._end_timestamp = datetime.fromisoformat(config.configuration.currentOperation.end) if config.configuration.currentOperation.end is not None else None
      
      self._last_updated = current

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_set_operation_mode(self, operation_mode: str):
    """Set new target operation mode."""
    try:
      self._attr_current_operation = operation_mode
      
      if OE_TO_HA_STATE["BOOST"] == self._attr_current_operation:
        self._end_timestamp = utcnow()
        self._end_timestamp += timedelta(hours=1)
        await self._client.async_boost_heat_pump_zone(
          self._account_id,
          self._heat_pump_id,
          self._zone.configuration.code,
          self._end_timestamp,
          self._attr_target_temperature if self._attr_target_temperature is not None else DEFAULT_BOOST_TEMPERATURE_WATER
        )
      else:
        zone_mode = self.get_zone_mode()
        await self._client.async_set_heat_pump_zone_mode(self._account_id, self._heat_pump_id, self._zone.configuration.code, zone_mode, None)
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_set_operation_mode error due to mocking mode: {e}')
      else:
        raise

    self.async_write_ha_state()

  async def async_turn_on(self):
    """Turn the entity on."""
    try:
      self._attr_current_operation = OE_TO_HA_STATE["ON"]
      await self._client.async_set_heat_pump_zone_mode(self._account_id, self._heat_pump_id, self._zone.configuration.code, 'ON', None)
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_turn_on error due to mocking mode: {e}')
      else:
        raise

    self.async_write_ha_state()

  async def async_turn_off(self):
    """Turn the entity off."""
    try:
      self._attr_current_operation = OE_TO_HA_STATE["OFF"]
      await self._client.async_set_heat_pump_zone_mode(self._account_id, self._heat_pump_id, self._zone.configuration.code, 'OFF', None)
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_turn_off error due to mocking mode: {e}')
      else:
        raise

    self.async_write_ha_state()

  async def async_set_temperature(self, **kwargs) -> None:
    """Set new target temperature."""

    try:
      self._attr_target_temperature = kwargs[ATTR_TEMPERATURE]
      if OE_TO_HA_STATE["BOOST"] == self._attr_current_operation:
        await self._client.async_boost_heat_pump_zone(self._account_id, self._heat_pump_id, self._zone.configuration.code, self._end_timestamp, self._attr_target_temperature)
      else:
        zone_mode = self.get_zone_mode()
        await self._client.async_set_heat_pump_zone_mode(self._account_id, self._heat_pump_id, self._zone.configuration.code, zone_mode, self._attr_target_temperature)
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_set_temperature error due to mocking mode: {e}')
      else:
        raise

    self.async_write_ha_state()

  @callback
  async def async_boost_water_heater(self, hours: int, minutes: int, target_temperature: float | None = None):
    """Boost the water heater"""

    if target_temperature is not None:
      if target_temperature < self._attr_min_temp or target_temperature > self._attr_max_temp:
        raise ServiceValidationError(
          translation_domain=DOMAIN,
          translation_key="invalid_target_temperature",
          translation_placeholders={ 
            "min_temperature": self._attr_min_temp,
            "max_temperature": self._attr_max_temp
          },
        )

    self._end_timestamp = utcnow()
    self._end_timestamp += timedelta(hours=hours, minutes=minutes)
    self._attr_current_operation = OE_TO_HA_STATE["BOOST"]

    boost_temperature = target_temperature if target_temperature is not None else self._attr_target_temperature
    if boost_temperature is None:
      boost_temperature = DEFAULT_BOOST_TEMPERATURE_WATER

    try:
      await self._client.async_boost_heat_pump_zone(
        self._account_id,
        self._heat_pump_id,
        self._zone.configuration.code,
        self._end_timestamp,
        boost_temperature
      )
    except Exception as e:
      if self._is_mocked:
        _LOGGER.warning(f'Suppress async_boost_water_heater error due to mocking mode: {e}')
      else:
        raise

    self.async_write_ha_state()

  def get_zone_mode(self):
    if self._attr_current_operation in HA_TO_OE_STATE:
      return HA_TO_OE_STATE[self._attr_current_operation]
    else:
      raise Exception(f"Unexpected heat pump mode detected: {self._attr_current_operation}")