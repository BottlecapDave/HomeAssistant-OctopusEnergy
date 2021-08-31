from datetime import timedelta
import logging
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
from .const import (
  DOMAIN,
  
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ELEC_MPAN,
  CONFIG_MAIN_ELEC_SN,
  CONFIG_MAIN_GAS_MPRN,
  CONFIG_MAIN_GAS_SN,

  DATA_COORDINATOR,
  DATA_CLIENT
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_default_sensors(hass, entry, async_add_entities)

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
    return "octopus_energy_electricity_current_rate"
    
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
      
      if self.coordinator.data != None:
        for period in self.coordinator.data:
          if now < period["valid_to"]:
            current_rate = period
          else:
            break

        self._attributes = current_rate
        self._state = current_rate["value_inc_vat"]
      else:
        self._state = 0

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
    return "octopus_energy_electricity_previous_rate"
    
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
      
      if self.coordinator.data != None:
        for period in self.coordinator.data:
          if target < period["valid_to"]:
            previous_rate = period
          else:
            break
      
        self._attributes = previous_rate
        self._state = previous_rate["value_inc_vat"]
      else:
        self._state = 0

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
    return "octopus_energy_electricity_latest_consumption"
    
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
    return "octopus_energy_gas_latest_consumption"
    
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