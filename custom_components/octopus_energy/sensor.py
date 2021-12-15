from datetime import timedelta
import logging

from homeassistant.util.dt import (utcnow, now, as_utc, parse_datetime)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
  DataUpdateCoordinator
)
from homeassistant.components.sensor import (
    DEVICE_CLASS_MONETARY,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_GAS,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
)
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    VOLUME_CUBIC_METERS
)

from typing import Generic, TypeVar

from .utils import (async_get_active_tariff_code, convert_kwh_to_m3)
from .const import (
  DOMAIN,
  
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ACCOUNT_ID,
  
  CONFIG_SMETS1,

  DATA_COORDINATOR,
  DATA_CLIENT,
  DATA_TARIFF_CODE
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

def create_reading_coordinator(hass, client, is_electricity, identifier, serial_number):
  """Create reading coordinator"""

  async def async_update_data():
    """Fetch data from API endpoint."""

    previous_consumption_key = f'{identifier}_{serial_number}_previous_consumption'
    if previous_consumption_key in hass.data[DOMAIN]:
      previous_data = hass.data[DOMAIN][previous_consumption_key]
    else:
      previous_data = None

    current_datetime = now()
    if (previous_data == None or (previous_data[-1]["interval_end"] < utcnow() and current_datetime.minute % 30 == 0)):
      _LOGGER.debug('Updating electricity consumption...')

      period_from = as_utc((current_datetime - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
      period_to = as_utc(current_datetime.replace(hour=0, minute=0, second=0, microsecond=0))
      if (is_electricity == True):
        data = await client.async_electricity_consumption(identifier, serial_number, period_from, period_to)
      else:
        data = await client.async_gas_consumption(identifier, serial_number, period_from, period_to)
      
      if data != None and len(data) == 48:
        hass.data[DOMAIN][previous_consumption_key] = data 
        return data
      
    if previous_data != None:
      return previous_data
    else:
      return []

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="rates",
    update_method=async_update_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

  hass.data[DOMAIN][f'{identifier}_{serial_number}_consumption_coordinator'] = coordinator

  return coordinator

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_default_sensors(hass, entry, async_add_entities)

async def async_setup_default_sensors(hass, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  is_smets1 = False
  if CONFIG_SMETS1 in config:
    is_smets1 = config[CONFIG_SMETS1]
  
  client = hass.data[DOMAIN][DATA_CLIENT]
  
  rate_coordinator = hass.data[DOMAIN][DATA_COORDINATOR]
  
  tariff_code = hass.data[DOMAIN][DATA_TARIFF_CODE]

  await rate_coordinator.async_config_entry_first_refresh()

  entities = [OctopusEnergyElectricityCurrentRate(rate_coordinator), OctopusEnergyElectricityPreviousRate(rate_coordinator)]
  
  account_info = await client.async_get_account(config[CONFIG_MAIN_ACCOUNT_ID])

  if len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      if async_get_active_tariff_code(point["agreements"], client) != None:
        for meter in point["meters"]:
          coordinator = create_reading_coordinator(hass, client, True, point["mpan"], meter["serial_number"])
          entities.append(OctopusEnergyPreviousAccumulativeElectricityReading(coordinator, client, point["mpan"], meter["serial_number"]))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityCost(coordinator, client, tariff_code, point["mpan"], meter["serial_number"]))

  if len(account_info["gas_meter_points"]) > 0:
    for point in account_info["gas_meter_points"]:
      # We only care about points that have active agreements
      if async_get_active_tariff_code(point["agreements"], client) != None:
        for meter in point["meters"]:
          entities.append(OctopusEnergyPreviousAccumulativeGasReading(client, point["mprn"], meter["serial_number"], is_smets1))

  async_add_entities(entities, True)

class OctopusEnergyElectricityCurrentRate(CoordinatorEntity, SensorEntity):
  """Sensor for displaying the current rate."""

  def __init__(self, coordinator):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)

    self._attributes = {}
    self._state = None

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
  def unit_of_measurement(self):
    """Unit of measurement of the sensor."""
    return "GBP/kWh"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state(self):
    """The state of the sensor."""
    # Find the current rate. We only need to do this every half an hour
    now = utcnow()
    if (now.minute % 30) == 0 or self._state == None:
      _LOGGER.info('Updating OctopusEnergyElectricityCurrentRate')
      
      current_rate = None
      if self.coordinator.data != None:
        for period in self.coordinator.data:
          if now >= period["valid_from"] and now <= period["valid_to"]:
            current_rate = period
            break

      if current_rate != None:
        self._attributes = current_rate
        self._state = current_rate["value_inc_vat"] / 100
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
    self._state = None

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
  def unit_of_measurement(self):
    """Unit of measurement of the sensor."""
    return "GBP/kWh"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state(self):
    """The state of the sensor."""
    # Find the previous rate. We only need to do this every half an hour
    now = utcnow()
    if (now.minute % 30) == 0 or self._state == None:
      _LOGGER.info('Updating OctopusEnergyElectricityPreviousRate')
      
      target = now - timedelta(minutes=30)
      
      previous_rate = None
      if self.coordinator.data != None:
        for period in self.coordinator.data:
          if target >= period["valid_from"] and target <= period["valid_to"]:
            previous_rate = period
            break
      
      if previous_rate != None:
        self._attributes = previous_rate
        self._state = previous_rate["value_inc_vat"] / 100
      else:
        self._state = 0

    return self._state

class OctopusEnergyPreviousAccumulativeElectricityReading(CoordinatorEntity, SensorEntity):
  """Sensor for displaying the previous days accumulative electricity reading."""

  def __init__(self, coordinator, client, mprn, serial_number):
    """Init sensor."""
    super().__init__(coordinator)

    self._mprn = mprn
    self._serial_number = serial_number
    self._client = client

    self._attributes = {
      "MPRN": mprn,
      "Serial Number": serial_number
    }

    self._state = None
    self._latest_date = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_previous_accumulative_consumption"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Electricity {self._serial_number} Previous Accumulative Consumption"

  @property
  def device_class(self):
    """The type of sensor"""
    return DEVICE_CLASS_ENERGY

  @property
  def state_class(self):
    """The state class of sensor"""
    return STATE_CLASS_TOTAL_INCREASING

  @property
  def unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return ENERGY_KILO_WATT_HOUR

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state(self):
    """Retrieve the previous days accumulative consumption"""
    if (self.coordinator.data != None and len(self.coordinator.data) == 48):

      if (self._latest_date != self.coordinator.data[-1]["interval_end"]):
        _LOGGER.info(f"Calculating previous electricity consumption for '{self._mprn}/{self._serial_number}'...")

        total = 0
        for consumption in self.coordinator.data:
          total = total + consumption["consumption"]
        
        self._state = total
        self._latest_date = self.coordinator.data[-1]["interval_end"]
    
    return self._state

class OctopusEnergyPreviousAccumulativeElectricityCost(CoordinatorEntity, SensorEntity):
  """Sensor for displaying the previous days accumulative electricity cost."""

  def __init__(self, coordinator, client, tariff_code, mprn, serial_number):
    """Init sensor."""
    super().__init__(coordinator)

    self._mprn = mprn
    self._serial_number = serial_number
    self._client = client
    self._tariff_code = tariff_code

    self._attributes = {
      "MPRN": mprn,
      "Serial Number": serial_number
    }

    self._state = 0
    self._latest_date = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_previous_accumulative_cost"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Electricity {self._serial_number} Previous Accumulative Cost"

  @property
  def device_class(self):
    """The type of sensor"""
    return DEVICE_CLASS_MONETARY

  @property
  def state_class(self):
    """The state class of sensor"""
    return STATE_CLASS_TOTAL_INCREASING

  @property
  def unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return "GBP"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-usd"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def should_poll(self):
    return True

  @property
  def state(self):
    """Retrieve the previously calculated state"""
    return self._state

  async def async_update(self):
    if (self.coordinator.data != None and len(self.coordinator.data) == 48):

      # Only calculate our consumption if our data has changed
      if (self._latest_date != self.coordinator.data[-1]["interval_end"]):
        _LOGGER.debug(f"Calculating previous electricity cost for '{self._mprn}/{self._serial_number}'...")

        current_datetime = now()
        period_from = as_utc((current_datetime - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
        period_to = as_utc(current_datetime.replace(hour=0, minute=0, second=0, microsecond=0))

        rates = await self._client.async_get_rates(self._tariff_code, period_from, period_to)

        total_cost_in_pence = 0
        for consumption in self.coordinator.data:
          value = consumption["consumption"]
          consumption_from = consumption["interval_start"]
          consumption_to = consumption["interval_end"]

          rate = next(rate for rate in rates if rate["valid_from"] == consumption_from and rate["valid_to"] == consumption_to)
          if rate == None:
            raise Exception(f"Failed to find rate for consumption between {consumption_from} and {consumption_to}")

          total_cost_in_pence = total_cost_in_pence + (rate["value_inc_vat"] * value)
        
        self._state = round(total_cost_in_pence / 100, 2)
        self._latest_date = self.coordinator.data[-1]["interval_end"]
      
class OctopusEnergyPreviousAccumulativeGasReading(SensorEntity):
  """Sensor for displaying the previous days accumulative gas reading."""

  def __init__(self, client, mprn, serial_number, is_smets1_meter):
    """Init sensor."""
    self._mprn = mprn
    self._serial_number = serial_number
    self._is_smets1_meter = is_smets1_meter
    self._client = client

    self._attributes = {
      "MPRN": mprn,
      "Serial Number": serial_number,
      "Is SMETS1 Meter": is_smets1_meter
    }

    self._state = None
    self._data = []

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_previous_accumulative_consumption"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Gas {self._serial_number} Previous Accumulative Consumption"

  @property
  def device_class(self):
    """The type of sensor"""
    return DEVICE_CLASS_GAS

  @property
  def state_class(self):
    """The state class of sensor"""
    return STATE_CLASS_TOTAL_INCREASING

  @property
  def unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return VOLUME_CUBIC_METERS

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:fire"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state(self):
    """Native value of the sensor."""
    return self._state

  async def async_update(self):
    """Retrieve the previous days accumulative consumption"""
    
    current_datetime = now()
    
    # We only need to do this once a day, unless we don't have enough data for the day therefore we want to retrieve it
    # every hour until we have enough data for the day
    if (current_datetime.hour == 0 and current_datetime.minute == 0) or self._state == None or (current_datetime.minute % 60 == 0 and len(self._data) != 48):
      _LOGGER.debug('Updating OctopusEnergyPreviousAccumulativeGasReading')

      period_from = as_utc((current_datetime - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
      period_to = as_utc(current_datetime.replace(hour=0, minute=0, second=0, microsecond=0))
      data = await self._client.async_gas_consumption(self._mprn, self._serial_number, period_from, period_to)
      if data != None:
        total = 0
        for item in data:
          total = total + item["consumption"]
        
        self._state = total
        self._data = data
      else:
        self._state = 0
        self._data = []

      if self._is_smets1_meter:
        self._state = convert_kwh_to_m3(self._state)
