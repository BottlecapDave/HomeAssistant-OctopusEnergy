import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (utcnow)

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
  CONFIG_COST_ENTITY_ID,
  CONFIG_COST_NAME,
)

from ..coordinators.electricity_rates import ElectricityRatesCoordinatorResult
from . import calculate_consumption
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
    self._attributes["charges"] = []
    self._is_export = is_export
    
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
  
  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state == "unknown" else state.state
      self._attributes = dict_to_typed_dict(state.attributes)
      # Make sure our attributes don't override any changed settings
      self._attributes.update(self._config)
    
      _LOGGER.debug(f'Restored OctopusEnergyCostTrackerSensor state: {self._state}')

    self.async_on_remove(
        async_track_state_change_event(
            self.hass, [self._config[CONFIG_COST_ENTITY_ID]], self._async_calculate_cost
        )
    )

  async def _async_calculate_cost(self, event: EventType[EventStateChangedData]):
    new_state = event.data["new_state"]
    old_state = event.data["old_state"]
    if self._attributes["is_tracking"] == False or new_state is None or new_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
      return

    current = utcnow()
    rates_result: ElectricityRatesCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None

    consumption_data = calculate_consumption(current,
                                             self._attributes["charges"],
                                             float(new_state.state),
                                             None if old_state.state is None or old_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else float(old_state.state),
                                             self._config[CONFIG_COST_ENTITY_ACCUMULATIVE_VALUE])

    if (consumption_data is not None and rates_result.rates is not None):
      result = calculate_electricity_consumption_and_cost(
        current,
        consumption_data,
        rates_result.rates,
        0,
        None, # We want to always recalculate
        rates_result.rates[0]["tariff_code"]
      )

      if result is not None:
        self._attributes["charges"] = list(map(lambda charge: {
          "start": charge["start"],
          "end": charge["end"],
          "rate": charge["rate"],
          "consumption": charge["consumption"],
          "cost": charge["cost"]
        }, result["charges"]))
        self._attributes["total_consumption"] = result["total_consumption"]
        self._state = result["total_cost"]

  @callback
  async def async_toggle_tracking(self):
    """Toggle tracking on/off"""
    self._attributes["is_tracking"] = self._attributes["is_tracking"] == False

    self.async_write_ha_state()