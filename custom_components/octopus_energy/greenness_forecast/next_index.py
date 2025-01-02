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

class OctopusEnergyGreennessForecastNextIndex(CoordinatorEntity, RestoreSensor):
  """Sensor for displaying the next rate."""
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

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
    return f"octopus_energy_{self._account_id}_greenness_forecast_next_index"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Greenness Forecast Next Index ({self._account_id})"
  
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
    """Determine the next forecast index"""
    current = now()
    self._state = None
    result: GreennessForecastCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    forecast = result.forecast if result is not None else None
    if (forecast is not None):
      _LOGGER.debug(f"Updating OctopusEnergyGreennessForecastNextIndex for '{self._account_id}'")

      current_and_next = get_current_and_next_forecast(current, forecast)
      if current_and_next is not None:
        self._attributes = greenness_forecast_to_dictionary(current_and_next.next)
        self._state = current_and_next.next.greenness_score if current_and_next.next is not None else None

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)
      _LOGGER.debug(f'Restored OctopusEnergyGreennessForecastNextIndex state: {self._state}')