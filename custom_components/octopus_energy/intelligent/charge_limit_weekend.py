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

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentChargeLimitWeekend(CoordinatorEntity, RestoreNumber, OctopusEnergyIntelligentSensor):
  """Sensor for setting the target percentage for car charging on weekend."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, device, account_id: str):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)
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
    return f"octopus_energy_intelligent_charge_limit_weekend"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Intelligent Charge Limit Weekend"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:battery-charging"
  
  @property
  def native_unit_of_measurement(self):
    return NumberDeviceClass.BATTERY

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self) -> float:
    """The state of the sensor."""
    if (self.coordinator.data is None) or (self._last_updated is not None and "last_updated" in self.coordinator.data and self._last_updated > self.coordinator.data["last_updated"]):
      self._attributes["last_updated_timestamp"] = self._last_updated
      return self._state
    
    self._attributes["last_updated_timestamp"] = self.coordinator.data["last_updated"]
    return self.coordinator.data["charge_limit_weekend"]

  async def async_set_native_value(self, value: float) -> None:
    """Set new value."""
    await self._client.async_update_intelligent_car_preferences(
      self._account_id,
      self.coordinator.data["charge_limit_weekday"] if self.coordinator.data is not None else 100,
      int(value),
      self.coordinator.data["ready_time_weekday"] if self.coordinator.data is not None else time(9,0),
      self.coordinator.data["ready_time_weekend"] if self.coordinator.data is not None else time(9,0),
    )
    self._state = value
    self._last_updated = utcnow()
    self.async_write_ha_state()