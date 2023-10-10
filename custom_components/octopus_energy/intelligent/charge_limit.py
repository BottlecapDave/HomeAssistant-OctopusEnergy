import logging

from datetime import time

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.number import RestoreNumber, NumberDeviceClass
from homeassistant.util.dt import (utcnow)

from .base import OctopusEnergyIntelligentSensor
from ..api_client import OctopusEnergyApiClient
from ..coordinators.intelligent_settings import IntelligentCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentChargeLimit(CoordinatorEntity, RestoreNumber, OctopusEnergyIntelligentSensor):
  """Sensor for setting the target percentage for car charging."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, device, account_id: str):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)

    self._state = None
    self._last_updated = None
    self._client = client
    self._account_id = account_id
    self._attributes = {}
    self.entity_id = generate_entity_id("number.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_intelligent_charge_limit"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Intelligent Charge Limit"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:battery-charging"
  
  @property
  def device_class(self):
    """The type of sensor"""
    return NumberDeviceClass.BATTERY
  
  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return "%"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self) -> float:
    """The value of the charge limit."""
    settings_result: IntelligentCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if settings_result is None or (self._last_updated is not None and self._last_updated > settings_result.last_retrieved):
      self._attributes["last_updated_timestamp"] = self._last_updated
      return self._state
    
    self._attributes["last_updated_timestamp"] = settings_result.last_retrieved
    self._state = settings_result.settings.charge_limit_weekday
    
    return self._state

  async def async_set_native_value(self, value: float) -> None:
    """Set new value."""
    await self._client.async_update_intelligent_car_target_percentage(
      self._account_id,
      int(value)
    )
    self._state = value
    self._last_updated = utcnow()
    self.async_write_ha_state()