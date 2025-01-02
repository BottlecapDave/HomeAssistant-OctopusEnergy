from datetime import datetime
import logging

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (now)

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass,
)

from homeassistant.helpers.event import (
  EventStateChangedData,
  async_track_state_change_event,
  async_track_entity_registry_updated_event,
)

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)

from ..const import (
  CONFIG_COST_TRACKER_NAME,
  CONFIG_COST_TRACKER_WEEKDAY_RESET,
  DOMAIN,
)

from . import accumulate_cost, get_device_info_from_device_entry

from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCostTrackerWeekSensor(RestoreSensor):
  """Sensor for calculating the cost for a given sensor over the course of a week."""

  def __init__(self, hass: HomeAssistant, config_entry, config, device_entry, tracked_entity_id: str, peak_type = None):
    """Init sensor."""
    # Pass coordinator to base class

    self._state = None
    self._config = config
    self._attributes = self._config.copy()
    self._attributes["total_consumption"] = 0
    self._attributes["accumulated_data"] = []
    self._last_reset = None
    self._tracked_entity_id = tracked_entity_id
    self._config_entry = config_entry
    self._peak_type = peak_type
    
    self._hass = hass
    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

    self._attr_device_info = get_device_info_from_device_entry(device_entry)

  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return self._peak_type is None

  @property
  def unique_id(self):
    """The id of the sensor."""
    base_name = f"octopus_energy_cost_tracker_{self._config[CONFIG_COST_TRACKER_NAME]}_week"
    if self._peak_type is not None:
      return f"{base_name}_{self._peak_type}"
    
    return base_name
    
  @property
  def name(self):
    """Name of the sensor."""
    base_name = f"Octopus Energy Cost Tracker {self._config[CONFIG_COST_TRACKER_NAME]} Week"
    if self._peak_type is not None:
      return f"{base_name} ({self._peak_type})"

    return base_name

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.MONETARY
  
  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL
  
  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return "GBP"
  
  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-gbp"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def native_value(self):
    """Determines the total cost of the tracked entity."""
    return self._state
  
  @property
  def last_reset(self):
    """Return the time when the sensor was last reset, if any."""
    current: datetime = now()
    self._reset_if_new_week(current)

    return self._last_reset
  
  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)
      # Make sure our attributes don't override any changed settings
      self._attributes.update(self._config)
    
      _LOGGER.debug(f'Restored {self.unique_id} state: {self._state}')

    self.async_on_remove(
      async_track_state_change_event(
        self.hass, [self._tracked_entity_id], self._async_calculate_cost
      )
    )

    self.async_on_remove(
      async_track_entity_registry_updated_event(
        self.hass, [self._tracked_entity_id], self._async_update_tracked_entity
      )
    )

  async def _async_update_tracked_entity(self, event) -> None:
    data = event.data
    if data["action"] != "update":
      return

    if "entity_id" in data["changes"]:
      new_entity_id = data["entity_id"]
      _LOGGER.debug(f"Tracked entity for '{self.entity_id}' updated from '{self._tracked_entity_id}' to '{new_entity_id}'. Reloading...")
      await self._hass.config_entries.async_reload(self._config_entry.entry_id)

  async def _async_calculate_cost(self, event: Event[EventStateChangedData]):
    current = now()
    self._reset_if_new_week(current)

    new_state = event.data["new_state"]
    if new_state is None or new_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
      return
    
    _LOGGER.debug(f"Source entity updated for '{self.entity_id}'; Event: {event.data}")

    self._recalculate_cost(current, float(new_state.state), float(new_state.attributes["total_consumption"]))
  
  @callback
  async def async_reset_cost_tracker(self):
    """Resets the sensor"""
    self._state = 0
    self._attributes["total_consumption"] = 0
    self._attributes["accumulated_data"] = []

    self.async_write_ha_state()

  @callback
  async def async_adjust_accumulative_cost_tracker(self, date, consumption: float, cost: float):
    """Adjusts the sensor"""
    selected_date = None
    for data in self._attributes["accumulated_data"]:
      if data["start"].date() == date:
        selected_date = data["start"]

    if selected_date is None:
      raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="cost_tracker_invalid_date",
        translation_placeholders={ 
          "min_date": self._attributes["accumulated_data"][0]["start"].date(),
          "max_date": self._attributes["accumulated_data"][-1]["start"].date() 
        },
      )

    self._recalculate_cost(selected_date, cost, consumption)

  def _recalculate_cost(self, current: datetime, new_cost: float, new_consumption: float):
    result = accumulate_cost(current, self._attributes["accumulated_data"], new_cost, new_consumption)
        
    self._attributes["total_consumption"] = result.total_consumption
    self._attributes["accumulated_data"] = result.accumulative_data
    self._state = result.total_cost

    self.async_write_ha_state()

  def _reset_if_new_week(self, current: datetime):
    start_of_day = current.replace(hour=0, minute=0, second=0, microsecond=0)
    if self._last_reset is None:
      self._last_reset = start_of_day
      return True
    
    target_weekday = self._config[CONFIG_COST_TRACKER_WEEKDAY_RESET] if CONFIG_COST_TRACKER_WEEKDAY_RESET in self._config else 0
    if self._last_reset.weekday() != current.weekday() and current.weekday() == target_weekday:
      self._state = 0
      self._attributes["total_consumption"] = 0
      self._attributes["accumulated_data"] = []
      self._last_reset = start_of_day

      return True

    return False