from datetime import timedelta
import math
import logging
from custom_components.octopus_energy.utils import apply_offset

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util.dt import (utcnow, now, as_utc, parse_datetime)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from .const import (
  CONFIG_TARGET_OFFSET,
  DOMAIN,

  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_MPAN,

  DATA_ELECTRICITY_RATES_COORDINATOR
)

from .target_sensor_utils import (
  calculate_continuous_times,
  calculate_intermittent_times,
  is_target_rate_active
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_TARGET_NAME in entry.data:
    if DOMAIN not in hass.data or DATA_ELECTRICITY_RATES_COORDINATOR not in hass.data[DOMAIN]:
      raise ConfigEntryNotReady
    
    await async_setup_target_sensors(hass, entry, async_add_entities)

  return True

async def async_setup_target_sensors(hass, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)
  
  coordinator = hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR]

  async_add_entities([OctopusEnergyTargetRate(coordinator, config)], True)

class OctopusEnergyTargetRate(CoordinatorEntity, BinarySensorEntity):
  """Sensor for calculating when a target should be turned on or off."""

  def __init__(self, coordinator, config):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)

    self._config = config
    self._attributes = self._config.copy()
    self._target_rates = []

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_target_{self._config[CONFIG_TARGET_NAME]}"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Target {self._config[CONFIG_TARGET_NAME]}"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:camera-timer"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    """The state of the sensor."""

    if CONFIG_TARGET_OFFSET in self._config:
      offset = self._config[CONFIG_TARGET_OFFSET]
    else:
      offset = None

    # Find the current rate. Rates change a maximum of once every 30 minutes.
    current_date = utcnow()
    if (current_date.minute % 30) == 0 or len(self._target_rates) == 0:
      _LOGGER.info(f'Updating OctopusEnergyTargetRate {self._config[CONFIG_TARGET_NAME]}')

      # If all of our target times have passed, it's time to recalculate the next set
      all_rates_in_past = True
      for rate in self._target_rates:
        if rate["valid_to"] > current_date:
          all_rates_in_past = False
          break
      
      if all_rates_in_past:
        # Retrieve our rates. For backwards compatibility, if there is only one rate or CONFIG_TARGET_MPAN
        # is not set, then pick the first set
        if self.coordinator.data != None:
          all_rates = self.coordinator.data
          if len(all_rates) == 1 or CONFIG_TARGET_MPAN not in self._config:
            all_rates = next(iter(all_rates.values()))
          else: 
            all_rates = all_rates.get(self._config[CONFIG_TARGET_MPAN])
        else:
          all_rates = []

        if CONFIG_TARGET_START_TIME in self._config:
          start_time = self._config[CONFIG_TARGET_START_TIME]

        if CONFIG_TARGET_END_TIME in self._config:
          end_time = self._config[CONFIG_TARGET_END_TIME]

        if (self._config[CONFIG_TARGET_TYPE] == "Continuous"):
          self._target_rates = calculate_continuous_times(
            now(),
            start_time,
            end_time,
            float(self._config[CONFIG_TARGET_HOURS]),
            all_rates,
            offset
          )
        elif (self._config[CONFIG_TARGET_TYPE] == "Intermittent"):
          self._target_rates = calculate_intermittent_times(
            now(),
            start_time,
            end_time,
            float(self._config[CONFIG_TARGET_HOURS]),
            all_rates,
            offset
          )
        else:
          _LOGGER.error(f"Unexpected target type: {self._config[CONFIG_TARGET_TYPE]}")

        self._attributes["target_times"] = self._target_rates

    active_result = is_target_rate_active(current_date, self._target_rates, offset)

    if offset != None and active_result["next_time"] != None:
      self._attributes["next_time"] = apply_offset(active_result["next_time"], offset)
    else:
      self._attributes["next_time"] = active_result["next_time"]

    return active_result["is_active"]