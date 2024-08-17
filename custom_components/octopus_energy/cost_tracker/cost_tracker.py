from datetime import datetime
import logging

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (now, parse_datetime, as_local)

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass,
)

from homeassistant.helpers.event import (
  EventStateChangedData,
  async_track_state_change_event,
)

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)

from ..const import (
  CONFIG_COST_TRACKER_ENTITY_ACCUMULATIVE_VALUE,
  CONFIG_COST_TRACKER_TARGET_ENTITY_ID,
  CONFIG_COST_TRACKER_NAME,
  DOMAIN,
)

from ..coordinators.electricity_rates import ElectricityRatesCoordinatorResult
from . import add_consumption
from ..electricity import calculate_electricity_consumption_and_cost
from ..utils.rate_information import get_rate_index, get_unique_rates
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCostTrackerSensor(CoordinatorEntity, RestoreSensor):
  """Sensor for calculating the cost for a given sensor."""

  def __init__(self, hass: HomeAssistant, coordinator, config, peak_type = None):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)

    self._state = None
    self._config = config
    self._attributes = self._config.copy()
    self._attributes["is_tracking"] = True
    self._attributes["tracked_charges"] = []
    self._attributes["untracked_charges"] = []
    self._last_reset = None
    self._peak_type = peak_type
    
    self._hass = hass
    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return self._peak_type is None

  @property
  def unique_id(self):
    """The id of the sensor."""
    base_name = f"octopus_energy_cost_tracker_{self._config[CONFIG_COST_TRACKER_NAME]}"
    if self._peak_type is not None:
      return f"{base_name}_{self._peak_type}"
    
    return base_name
    
  @property
  def name(self):
    """Name of the sensor."""
    base_name = f"Octopus Energy Cost Tracker {self._config[CONFIG_COST_TRACKER_NAME]}"
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
    self._reset_if_new_day(current)

    return self._last_reset
  
  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else state.state
      self._attributes = dict_to_typed_dict(state.attributes)
      # Make sure our attributes don't override any changed settings
      self._attributes.update(self._config)
    
      _LOGGER.debug(f'Restored {self.unique_id} state: {self._state}')

    self.async_on_remove(
        async_track_state_change_event(
            self.hass, [self._config[CONFIG_COST_TRACKER_TARGET_ENTITY_ID]], self._async_calculate_cost
        )
    )

  async def _async_calculate_cost(self, event: Event[EventStateChangedData]):
    new_state = event.data["new_state"]
    old_state = event.data["old_state"]
    _LOGGER.debug(f"State updated for '{self._config[CONFIG_COST_TRACKER_TARGET_ENTITY_ID]}' for '{self.unique_id}': new_state: {new_state}; old_state: {old_state}")
    if new_state is None or new_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or old_state is None or old_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
      return
    
    _LOGGER.debug(f'event: {event.data}')

    current = now()
    rates_result: ElectricityRatesCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None

    new_last_reset = None
    if "last_reset" in new_state.attributes and new_state.attributes["last_reset"] is not None:
      if isinstance(new_state.attributes["last_reset"], datetime):
        new_last_reset = new_state.attributes["last_reset"]
      else:
        new_last_reset = parse_datetime(new_state.attributes["last_reset"])

    old_last_reset = None
    if "last_reset" in old_state.attributes and old_state.attributes["last_reset"] is not None:
      if isinstance(old_state.attributes["last_reset"], datetime):
        old_last_reset = old_state.attributes["last_reset"]
      else:
        old_last_reset = parse_datetime(old_state.attributes["last_reset"])

    consumption_data = add_consumption(current,
                                       self._attributes["tracked_charges"] if "tracked_charges" in self._attributes else [],
                                       self._attributes["untracked_charges"] if "untracked_charges" in self._attributes else [],
                                       float(new_state.state),
                                       None if old_state.state is None or old_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else float(old_state.state),
                                       new_last_reset,
                                       old_last_reset,
                                       self._config[CONFIG_COST_TRACKER_ENTITY_ACCUMULATIVE_VALUE],
                                       self._attributes["is_tracking"] if "is_tracking" in self._attributes else True,
                                       new_state.attributes["state_class"] if "state_class" in new_state.attributes else None)
    
    
    _LOGGER.debug(f"Consumption calculated for '{self.unique_id}': {consumption_data}")

    if (consumption_data is not None and rates_result is not None and rates_result.rates is not None):
      self._reset_if_new_day(current)

      self._recalculate_cost(current, consumption_data.tracked_consumption_data, consumption_data.untracked_consumption_data, rates_result.rates)

  @callback
  async def async_update_cost_tracker_config(self, is_tracking_enabled: bool):
    """Toggle tracking on/off"""
    self._attributes["is_tracking"] = is_tracking_enabled

    self.async_write_ha_state()
  
  @callback
  async def async_reset_cost_tracker(self):
    """Resets the sensor"""
    self._state = 0
    self._attributes["tracked_charges"] = []
    self._attributes["untracked_charges"] = []
    self._attributes["total_consumption"] = 0

    self.async_write_ha_state()
    _LOGGER.debug(f"Cost tracker '{self.unique_id}' manually reset")

  @callback
  async def async_adjust_cost_tracker(self, datetime, consumption: float):
    """Adjusts the sensor"""
    local_datetime = as_local(datetime)
    selected_datetime = None
    for data in self._attributes["tracked_charges"]:
      if local_datetime >= data["start"] and local_datetime < data["end"]:
        selected_datetime = data["start"]
        data["consumption"] = consumption

    if selected_datetime is None:
      raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="cost_tracker_invalid_date",
        translation_placeholders={ 
          "min_date": self._attributes["tracked_charges"][0]["start"].date(),
          "max_date": self._attributes["tracked_charges"][-1]["end"].date() 
        },
      )

    rates_result: ElectricityRatesCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    self._recalculate_cost(now(), self._attributes["tracked_charges"], self._attributes["untracked_charges"], rates_result.rates)
    _LOGGER.debug(f"Cost tracker '{self.unique_id}' manually adjusted")

  def _recalculate_cost(self, current: datetime, tracked_consumption_data: list, untracked_consumption_data: list, rates: list):
    target_rate = None
    if self._peak_type is not None:
      unique_rates = get_unique_rates(current, rates)
      unique_rate_index = get_rate_index(len(unique_rates), self._peak_type)
      target_rate = unique_rates[unique_rate_index] if unique_rate_index is not None else None

    tracked_result = calculate_electricity_consumption_and_cost(
      tracked_consumption_data,
      rates,
      0,
      None, # We want to always recalculate
      0,
      False,
      target_rate=target_rate
    )

    untracked_result = calculate_electricity_consumption_and_cost(
      untracked_consumption_data,
      rates,
      0,
      None, # We want to always recalculate
      0,
      False,
      target_rate=target_rate
    )

    _LOGGER.debug(f"Cost calculated for '{self.unique_id}'; tracked_result: {tracked_result}; untracked_result: {untracked_result}")

    if tracked_result is not None and untracked_result is not None:
      self._attributes["tracked_charges"] = list(map(lambda charge: {
        "start": charge["start"],
        "end": charge["end"],
        "rate": charge["rate"],
        "consumption": charge["consumption"],
        "cost": charge["cost"]
      }, tracked_result["charges"]))
      
      self._attributes["untracked_charges"] = list(map(lambda charge: {
        "start": charge["start"],
        "end": charge["end"],
        "rate": charge["rate"],
        "consumption": charge["consumption"],
        "cost": charge["cost"]
      }, untracked_result["charges"]))
      
      self._attributes["total_consumption"] = tracked_result["total_consumption"] + untracked_result["total_consumption"]
      self._state = tracked_result["total_cost"]

      self._attributes = dict_to_typed_dict(self._attributes)
      self.async_write_ha_state()

  def _reset_if_new_day(self, current: datetime):
    start_of_day = current.replace(hour=0, minute=0, second=0, microsecond=0)
    if self._last_reset is None:
      self._last_reset = start_of_day
      return True
    
    if self._last_reset.date() != current.date():
      self._state = 0
      self._attributes["tracked_charges"] = []
      self._attributes["untracked_charges"] = []
      self._attributes["total_consumption"] = 0
      self._last_reset = start_of_day
      
      _LOGGER.debug(f"Cost tracker '{self.unique_id}' reset. self._last_reset: {self._last_reset.date()}; current: {current.date()}")

      return True

    return False