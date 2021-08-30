from datetime import timedelta
import math
import logging
import async_timeout
from datetime import datetime

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.core import callback
from homeassistant.util.dt import (utcnow, as_utc)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
    DEVICE_CLASS_MONETARY,
    DEVICE_CLASS_ENERGY,
    SensorEntity,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from .const import (
  DOMAIN,
  
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_TARIFF,
  CONFIG_MAIN_TARIFF_CODE,
  CONFIG_MAIN_ELEC_MPAN,
  CONFIG_MAIN_ELEC_SN,
  CONFIG_MAIN_GAS_MPRN,
  CONFIG_MAIN_GAS_SN,

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

async def async_setup_default_sensors(hass, entry, async_add_entities):
  config = entry.data
  
  client = hass.data[DOMAIN][DATA_CLIENT]
  
  coordinator = hass.data[DOMAIN][DATA_COORDINATOR]

  await coordinator.async_config_entry_first_refresh()

  entities = [OctopusEnergyElectricityCurrentRate(coordinator), OctopusEnergyElectricityPreviousRate(coordinator)]

  if config[CONFIG_MAIN_ELEC_MPAN] != "" and config[CONFIG_MAIN_ELEC_SN] != "":
    entities.append(OctopusEnergyLatestElectricityReading(client, config[CONFIG_MAIN_ELEC_MPAN], config[CONFIG_MAIN_ELEC_SN]))

  if config[CONFIG_MAIN_GAS_MPRN] != "" and config[CONFIG_MAIN_GAS_SN] != "":
    entities.append(OctopusEnergyLatestGasReading(client, config[CONFIG_MAIN_GAS_MPRN], config[CONFIG_MAIN_GAS_SN]))

  async_add_entities(entities, True)

async def async_setup_target_sensors(hass, entry, async_add_entities):
  config = entry.data
  
  client = hass.data[DOMAIN][DATA_CLIENT]
  
  coordinator = hass.data[DOMAIN][DATA_COORDINATOR]

  async_add_entities([OctopusEnergyTargetRate(coordinator, config)], True)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_default_sensors(hass, entry, async_add_entities)
  elif CONFIG_TARGET_NAME in entry.data:
    await async_setup_target_sensors(hass, entry, async_add_entities)

class OctopusEnergyElectricityCurrentRate(CoordinatorEntity, SensorEntity):
  """Sensor for displaying the current rate."""

  def __init__(self, coordinator):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)

    self._attributes = {}
    self._state = 0

  @property
  def unique_id(self):
    """The id of the sensor."""
    return "sensor.octopus_energy_electricity_current_rate"
    
  @property
  def name(self):
    """Name of the sensor."""
    return "Octopus Energy Electricity Current Rate"

  @property
  def device_class(self):
    """The type of sensor"""
    return DEVICE_CLASS_MONETARY

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-usd"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state(self):
    """The state of the sensor."""
    # Find the current rate. 
    # We only need to do this every half an hour
    now = utcnow()
    if (now.minute % 30) == 0 or self._state == 0:
      _LOGGER.info('Updating OctopusEnergyElectricityCurrentRate')
      
      for period in self.coordinator.data:
        if now < period["valid_to"]:
          current_rate = period
        else:
          break

      self._attributes = current_rate
      self._state = current_rate["value_inc_vat"]

    return self._state

class OctopusEnergyElectricityPreviousRate(CoordinatorEntity, SensorEntity):
  """Sensor for displaying the previous rate."""

  def __init__(self, coordinator):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)

    self._attributes = {}
    self._state = 0

  @property
  def unique_id(self):
    """The id of the sensor."""
    return "sensor.octopus_energy_electricity_previous_rate"
    
  @property
  def name(self):
    """Name of the sensor."""
    return "Octopus Energy Electricity Previous Rate"

  @property
  def device_class(self):
    """The type of sensor"""
    return DEVICE_CLASS_MONETARY

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-usd"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state(self):
    """The state of the sensor."""
    # Find the current rate. 
    # We only need to do this every half an hour
    now = utcnow()
    if (now.minute % 30) == 0 or self._state == 0:
      _LOGGER.info('Updating OctopusEnergyElectricityPreviousRate')
      
      target = utcnow() - timedelta(minutes=30)
      for period in self.coordinator.data:
        if target < period["valid_to"]:
          previous_rate = period
        else:
          break
      
      self._attributes = previous_rate
      self._state = previous_rate["value_inc_vat"]

    return self._state

class OctopusEnergyLatestElectricityReading(SensorEntity):
  """Sensor for displaying the current electricity rate."""

  def __init__(self, client, mpan, serial_number):
    """Init sensor."""
    self._mpan = mpan
    self._serial_number = serial_number
    self._client = client

    self._state = 0
    self._last_reset = utcnow()

  @property
  def unique_id(self):
    """The id of the sensor."""
    return "sensor.octopus_energy_electricity_latest_consumption"
    
  @property
  def name(self):
    """Name of the sensor."""
    return "Octopus Energy Electricity Latest Consumption"

  @property
  def device_class(self):
    """The type of sensor"""
    return DEVICE_CLASS_ENERGY

  @property
  def state_class(self):
    """The state class of sensor"""
    return "measurement"

  @property
  def unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return "kWh"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def state(self):
    """Native value of the sensor."""
    return self._state

  @property
  def last_reset(self):
    """Last reset of the sensor."""
    return self._last_reset

  async def async_update(self):
    """Retrieve the latest consumption"""
    # We only need to do this every half an hour
    now = utcnow()
    if (now.minute % 30) == 0 or self._state == 0:
      _LOGGER.info('Updating OctopusEnergyLatestElectricityReading')

      data = await self._client.async_latest_electricity_consumption(self._mpan, self._serial_number)
      if data != None:
        self._state = data["consumption"]
        self._last_reset = data["interval_end"]
      else:
        self._state = 0
        self._last_reset = utcnow()

class OctopusEnergyLatestGasReading(SensorEntity):
  """Sensor for displaying the current gas rate."""

  def __init__(self, client, mprn, serial_number):
    """Init sensor."""
    self._mprn = mprn
    self._serial_number = serial_number
    self._client = client

    self._state = 0
    self._last_reset = utcnow()

  @property
  def unique_id(self):
    """The id of the sensor."""
    return "sensor.octopus_energy_gas_latest_consumption"
    
  @property
  def name(self):
    """Name of the sensor."""
    return "Octopus Energy Gas Latest Consumption"

  @property
  def device_class(self):
    """The type of sensor"""
    return DEVICE_CLASS_ENERGY

  @property
  def state_class(self):
    """The state class of sensor"""
    return "measurement"

  @property
  def unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return "kWh"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def state(self):
    """Native value of the sensor."""
    return self._state

  @property
  def last_reset(self):
    """Last reset of the sensor."""
    return self._last_reset

  async def async_update(self):
    """Retrieve the latest consumption"""
    # We only need to do this every half an hour
    now = utcnow()
    if (now.minute % 30) == 0 or self._state == 0:
      _LOGGER.info('Updating OctopusEnergyLatestGasReading')

      data = await self._client.async_latest_gas_consumption(self._mprn, self._serial_number)
      if data != None:
        self._state = data["consumption"]
        self._last_reset = data["interval_end"]
      else:
        self._state = 0
        self._last_reset = utcnow()

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
    return f"sensor.octopus_energy_target_{self._config[CONFIG_TARGET_NAME]}"
    
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
  def state(self):
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

    for rate in self._target_rates:
      if now >= rate["valid_from"] and now <= rate["valid_to"]:
        return True

    return False

  def get_applicable_rates(self):
    now = utcnow()

    if CONFIG_TARGET_END_TIME in self._config:
      target_end = as_utc(datetime.strptime(now.strftime(f"%Y-%m-%dT{self._config[CONFIG_TARGET_END_TIME]}:%SZ"), f"%Y-%m-%dT%H:%M:%SZ"))
      if (target_end < now):
        target_end = target_end + timedelta(days=1)
    else:
      target_end = None

    if CONFIG_TARGET_START_TIME in self._config:
      target_start = as_utc(datetime.strptime(target_end.strftime(f"%Y-%m-%dT{self._config[CONFIG_TARGET_START_TIME]}:%SZ"), f"%Y-%m-%dT%H:%M:%SZ"))
      if (target_start > target_end):
        target_start = target_start - timedelta(days=1)
    else:
      target_start = now

    # Retrieve the rates that are applicable for our target rate
    rates = []
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

    attributes = self._config.copy()
    attributes["Target Times"] = best_continuous_rates
    self._attributes = attributes

    if best_continuous_rates is not None:
      return best_continuous_rates
    
    return []