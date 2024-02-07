import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (now)

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorStateClass,
)

from ..utils.attributes import dict_to_typed_dict
from ..coordinators.greenness_forecast import GreennessForecastCoordinatorResult
from . import get_current_and_next_forecast, greenness_forecast_to_dictionary, greenness_forecast_to_dictionary_list

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyGreennessForecastCurrentIndex(CoordinatorEntity, RestoreSensor):
  """Sensor for displaying the current rate."""

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)

    self._state = None
    self._last_updated = None
    self._account_id = account_id

    self._attributes = {}
    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_greenness_forecast_current_index"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Greenness Forecast Current Index ({self._account_id})"
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False
  
  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:leaf"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine the current forecast index"""
    current = now()
    self._state = None
    result: GreennessForecastCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    forecast = result.forecast if result is not None else None
    if (forecast is not None):
      _LOGGER.debug(f"Updating OctopusEnergyGreennessForecastCurrentIndex for '{self._account_id}'")

      current_and_next = get_current_and_next_forecast(current, forecast)
      if current_and_next is not None:
        self._attributes = greenness_forecast_to_dictionary(current_and_next.current)
        self._state = current_and_next.current.greenness_score if current_and_next.current is not None else None
        
        if current_and_next.next is not None:
          self._attributes["next_start"] = current_and_next.next.start
          self._attributes["next_end"] = current_and_next.next.end

      self._attributes["forecast"] = greenness_forecast_to_dictionary_list(forecast)
      self._attributes["data_last_retrieved"] = result.last_retrieved

    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else state.state
      self._attributes = dict_to_typed_dict(state.attributes)
      _LOGGER.debug(f'Restored OctopusEnergyGreennessForecastCurrentIndex state: {self._state}')