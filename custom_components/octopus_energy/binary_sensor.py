from datetime import timedelta
import math
import logging

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util.dt import (utcnow, as_utc, parse_datetime)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from .const import (
  DOMAIN,

  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,

  DATA_COORDINATOR,
  DATA_CLIENT
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_TARGET_NAME in entry.data:
    if DOMAIN not in hass.data or DATA_COORDINATOR not in hass.data[DOMAIN]:
      raise ConfigEntryNotReady
    
    await async_setup_target_sensors(hass, entry, async_add_entities)

  return True

async def async_setup_target_sensors(hass, entry, async_add_entities):
  config = entry.data
  
  coordinator = hass.data[DOMAIN][DATA_COORDINATOR]

  async_add_entities([OctopusEnergyTargetRate(coordinator, config)], True)

class OctopusEnergyTargetRate(CoordinatorEntity, BinarySensorEntity):
  """Sensor for calculating when a target should be turned on or off."""

  def __init__(self, coordinator, config):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)

    self._config = config
    self._attributes = config
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

    # Find the current rate. 
    # We only need to do this every half an hour
    now = utcnow()
    if (now.minute % 30) == 0 or len(self._target_rates) == 0:
      _LOGGER.info(f'Updating OctopusEnergyTargetRate {self._config[CONFIG_TARGET_NAME]}')

      # If all of our target times have passed, it's time to recalculate the next set
      all_rates_in_past = True
      for rate in self._target_rates:
        if rate["valid_to"] > now:
          all_rates_in_past = False
      
      if all_rates_in_past:
        if (self._config[CONFIG_TARGET_TYPE] == "Continuous"):
          self._target_rates = self.calculate_continuous_times()
        elif (self._config[CONFIG_TARGET_TYPE] == "Intermittent"):
          self._target_rates = self.calculate_intermittent_times()
        else:
          _LOGGER.error(f"Unexpected target type: {self._config[CONFIG_TARGET_TYPE]}")

      attributes = self._config.copy()
      self._target_rates.sort(key=self.get_valid_to)
      attributes["Target times"] = self._target_rates

      if (len(self._target_rates) > 0):
        attributes["Next time"] = self._target_rates[0]["valid_from"]
      else:
        attributes["Next time"] = None

      self._attributes = attributes

    for rate in self._target_rates:
      if now >= rate["valid_from"] and now <= rate["valid_to"]:
        return True

    return False

  def get_valid_to(self, rate):
    return rate["valid_to"]

  def get_applicable_rates(self):
    now = utcnow()

    if CONFIG_TARGET_END_TIME in self._config:
      # Get the target end for today. If this is in the past, then look at tomorrow
      target_end = as_utc(parse_datetime(now.strftime(f"%Y-%m-%dT{self._config[CONFIG_TARGET_END_TIME]}:%SZ")))
      if (target_end < now):
        target_end = target_end + timedelta(days=1)
    else:
      target_end = None

    if CONFIG_TARGET_START_TIME in self._config:
      # Get the target start on the same day as our target end. If this is after our target end (which can occur if we're looking for
      # a time over night), then go back a day
      target_start = as_utc(parse_datetime(target_end.strftime(f"%Y-%m-%dT{self._config[CONFIG_TARGET_START_TIME]}:%SZ")))
      if (target_start > target_end):
        target_start = target_start - timedelta(days=1)

      # If our start date has passed, reset it to now to avoid picking a slot in the past
      if (target_start < now):
        target_start = now
    else:
      target_start = now

    # Retrieve the rates that are applicable for our target rate
    rates = []
    if self.coordinator.data != None:
      for rate in self.coordinator.data:
        if rate["valid_from"] >= target_start and (target_end == None or rate["valid_to"] <= target_end):
          rates.append(rate)

    return rates
    
  def calculate_continuous_times(self):
    rates = self.get_applicable_rates()
    rates_count = len(rates)
    total_required_rates = math.ceil(float(self._config[CONFIG_TARGET_HOURS]) * 2)

    best_continuous_rates = None
    best_continuous_rates_total = None

    # Loop through our rates and try and find the block of time that meets our desired
    # hours and has the lowest combined rates
    for index, rate in enumerate(rates):
      continuous_rates = [rate]
      continuous_rates_total = rate["value_inc_vat"]
      
      for offset in range(1, total_required_rates):
        if (index + offset) < rates_count:
          offset_rate = rates[(index + offset)]
          continuous_rates.append(offset_rate)
          continuous_rates_total += offset_rate["value_inc_vat"]
        else:
          break
      
      if ((best_continuous_rates == None or continuous_rates_total < best_continuous_rates_total) and len(continuous_rates) == total_required_rates):
        best_continuous_rates = continuous_rates
        best_continuous_rates_total = continuous_rates_total

    if best_continuous_rates is not None:
      return best_continuous_rates
    
    return []

  def get_rate(self, rate):
    return rate["value_inc_vat"]
  
  def calculate_intermittent_times(self):
    rates = self.get_applicable_rates()
    total_required_rates = math.ceil(float(self._config[CONFIG_TARGET_HOURS]) * 2)

    rates.sort(key=self.get_rate)
    return rates[:total_required_rates]