from datetime import datetime
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (now, parse_datetime)

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

from homeassistant.helpers.typing import EventType

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)

from ..const import (
  CONFIG_COST_ENTITY_ACCUMULATIVE_VALUE,
  CONFIG_COST_TARGET_ENTITY_ID,
  CONFIG_COST_NAME,
)

from ..coordinators.electricity_rates import ElectricityRatesCoordinatorResult
from . import add_consumption
from ..electricity import calculate_electricity_consumption_and_cost

from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCostTrackerSensor(CoordinatorEntity, RestoreSensor):
  """Sensor for calculating the cost for a given sensor."""

  def __init__(self, hass: HomeAssistant, coordinator, config, is_export):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)

    self._state = None
    self._config = config
    self._is_export = is_export
    self._attributes = self._config.copy()
    self._attributes["is_tracking"] = True
    self._attributes["tracked_charges"] = []
    self._attributes["untracked_charges"] = []
    self._is_export = is_export
    self._last_reset = None
    
    self._hass = hass
    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_cost_tracker_{self._config[CONFIG_COST_NAME]}"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Cost Tracker {self._config[CONFIG_COST_NAME]}"

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
    
      _LOGGER.debug(f'Restored OctopusEnergyCostTrackerSensor state: {self._state}')

    self.async_on_remove(
        async_track_state_change_event(
            self.hass, [self._config[CONFIG_COST_TARGET_ENTITY_ID]], self._async_calculate_cost
        )
    )

  async def _async_calculate_cost(self, event: EventType[EventStateChangedData]):
    new_state = event.data["new_state"]
    old_state = event.data["old_state"]
    if new_state is None or new_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
      return

    current = now()
    rates_result: ElectricityRatesCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None

    consumption_data = add_consumption(current,
                                       self._attributes["tracked_charges"],
                                       self._attributes["untracked_charges"],
                                       float(new_state.state),
                                       None if old_state.state is None or old_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else float(old_state.state),
                                       parse_datetime(new_state.attributes["last_reset"]) if "last_reset" in new_state.attributes and new_state.attributes["last_reset"] is not None else None,
                                       parse_datetime(old_state.attributes["last_reset"]) if "last_reset" in old_state.attributes and old_state.attributes["last_reset"] is not None else None,
                                       self._config[CONFIG_COST_ENTITY_ACCUMULATIVE_VALUE],
                                       self._attributes["is_tracking"])

    if (consumption_data is not None and rates_result is not None and rates_result.rates is not None):
      self._reset_if_new_day(current)

      tracked_result = calculate_electricity_consumption_and_cost(
        current,
        consumption_data.tracked_consumption_data,
        rates_result.rates,
        0,
        None, # We want to always recalculate
        rates_result.rates[0]["tariff_code"],
        0,
        False
      )

      untracked_result = calculate_electricity_consumption_and_cost(
        current,
        consumption_data.untracked_consumption_data,
        rates_result.rates,
        0,
        None, # We want to always recalculate
        rates_result.rates[0]["tariff_code"],
        0,
        False
      )

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

        self.async_write_ha_state()

  @callback
  async def async_update_cost_tracker_config(self, is_tracking_enabled: bool):
    """Toggle tracking on/off"""
    self._attributes["is_tracking"] = is_tracking_enabled

    self.async_write_ha_state()

  def _reset_if_new_day(self, current: datetime):
    current: datetime = now()
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

      return True

    return False