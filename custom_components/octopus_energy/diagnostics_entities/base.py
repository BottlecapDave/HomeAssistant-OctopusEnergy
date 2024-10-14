import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    EntityCategory,
)
from homeassistant.core import callback

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)

from homeassistant.helpers.entity import generate_entity_id

from ..coordinators import BaseCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyBaseDataLastRetrieved(CoordinatorEntity, RestoreSensor):
  """Base sensor for data last retrieved."""

  def __init__(self, hass, coordinator):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    self._state = None

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.TIMESTAMP
  
  @property
  def entity_category(self):
    """The category of the sensor"""
    return EntityCategory.DIAGNOSTIC

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:clock"

  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    result: BaseCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    self._state = result.last_retrieved if result is not None else None
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else dict_to_typed_dict({ "date": state.state })["date"]
      _LOGGER.debug(f'Restored state: {self._state}')