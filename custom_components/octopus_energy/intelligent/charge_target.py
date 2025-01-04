import logging
from datetime import time

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.number import RestoreNumber, NumberDeviceClass, NumberMode
from homeassistant.util.dt import (utcnow)

from .base import OctopusEnergyIntelligentSensor
from ..api_client import OctopusEnergyApiClient
from ..coordinators.intelligent_settings import IntelligentCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyIntelligentChargeTarget(CoordinatorEntity, RestoreNumber, OctopusEnergyIntelligentSensor):
  """Sensor for setting the target percentage for car charging."""

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, device, account_id: str, is_mocked: bool):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)

    self._state = None
    self._last_updated = None
    self._client = client
    self._account_id = account_id
    self._attributes = {}
    self._is_mocked = is_mocked
    self.entity_id = generate_entity_id("number.{}", self.unique_id, hass=hass)

    self._attr_native_min_value = 10
    self._attr_native_max_value = 100
    self._attr_native_step = 1
    self._attr_mode = NumberMode.BOX

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_intelligent_charge_target"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Intelligent Charge Target ({self._account_id})"

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
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """The value of the charge limit."""
    settings_result: IntelligentCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if settings_result is None or (self._last_updated is not None and self._last_updated > settings_result.last_retrieved):
      return self._state
    
    if settings_result.settings is not None:
      self._state = settings_result.settings.charge_limit_weekday

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_set_native_value(self, value: float) -> None:
    """Set new value."""
    if value and value % self._attr_native_step == 0:
      try:
        await self._client.async_update_intelligent_car_target_percentage(
          self._account_id,
          self._device.id,
          int(value)
        )
      except Exception as e:
        if self._is_mocked:
          _LOGGER.warning(f'Suppress async_set_native_value error due to mocking mode: {e}')
        else:
          raise

      self._state = value
      self._last_updated = utcnow()
      self.async_write_ha_state()
    else:
      raise Exception(f"Value must be between {self._attr_native_min_value} and {self._attr_native_max_value} and be a multiple of {self._attr_native_step}")

  async def async_added_to_hass(self) -> None:
    """Restore last state."""
    await super().async_added_to_hass()

    if ((last_state := await self.async_get_last_state()) and 
        (last_number_data := await self.async_get_last_number_data())
      ):
      
      self._attributes = dict_to_typed_dict(last_state.attributes, ["min", "max", "step", "mode"])
      if last_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
        self._state = last_number_data.native_value
          
    _LOGGER.debug(f'Restored OctopusEnergyIntelligentChargeTarget state: {self._state}')