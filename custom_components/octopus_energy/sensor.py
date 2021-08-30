from datetime import timedelta
import logging
import async_timeout
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.util.dt import utcnow
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
  DataUpdateCoordinator,
  UpdateFailed,
)
from homeassistant.components.sensor import (
    DEVICE_CLASS_MONETARY,
    DEVICE_CLASS_ENERGY,
    SensorEntity,
)
from .const import DOMAIN
from .api_client import OctopusEnergyApiClient
from .const import (
  DOMAIN,
  
  CONFIG_API_KEY,
  CONFIG_TARIFF,
  CONFIG_TARIFF_CODE,
  CONFIG_ELEC_MPAN,
  CONFIG_ELEC_SN,
  CONFIG_GAS_MPRN,
  CONFIG_GAS_SN
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    _LOGGER.error('setup_platform')
    _LOGGER.error(discovery_info)
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""
  config = entry.data

  client = OctopusEnergyApiClient(config[CONFIG_API_KEY], config[CONFIG_TARIFF])

  async def async_update_data():
    """Fetch data from API endpoint."""
    _LOGGER.info('Updating rates...')
    return await client.async_get_rates('AGILE-18-02-21', config[CONFIG_TARIFF_CODE])
  
  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    # Name of the data. For logging purposes.
    name="rates",
    update_method=async_update_data,
    # Polling interval. Will only be polled if there are subscribers.
    update_interval=timedelta(hours=1),
  )

  await coordinator.async_config_entry_first_refresh()

  entities = [OctopusEnergyCurrentRate(coordinator)]

  if config[CONFIG_ELEC_MPAN] != "" and config[CONFIG_ELEC_SN] != "":
    entities.append(OctopusEnergyLatestElectricityReading(client, config[CONFIG_ELEC_MPAN], config[CONFIG_ELEC_SN]))

  if config[CONFIG_GAS_MPRN] != "" and config[CONFIG_GAS_SN] != "":
    entities.append(OctopusEnergyLatestGasReading(client, config[CONFIG_GAS_MPRN], config[CONFIG_GAS_SN]))

  async_add_entities(entities, True)

class OctopusEnergyCurrentRate(CoordinatorEntity, SensorEntity):
  """Sensor for displaying the current rate."""

  def __init__(self, coordinator):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)

  @property
  def unique_id(self):
    """The id of sensor"""
    return "sensor.octopus_energy_current_rate"
    
  @property
  def name(self):
    """Name of the sensor."""
    return "Octopus Energy Current Rate"

  @property
  def device_class(self):
    """The type of sensor"""
    return DEVICE_CLASS_MONETARY

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-usd"

  @property
  def state(self):
    """The current state of the sensor"""
    now = utcnow()
    for period in self.coordinator.data:
      if now < period["valid_to"]:
        current_rate = period
      else:
        break

    return current_rate["value_inc_vat"]

class OctopusEnergyLatestElectricityReading(SensorEntity):
  """Sensor for displaying the current electricity rate."""

  def __init__(self, client, mpan, serial_number):
    """Init sensor."""
    self._mpan = mpan
    self._serial_number = serial_number
    self._client = client
    self._last_reset = utcnow()

    self._state = 0

  @property
  def unique_id(self):
    """The id of sensor"""
    return "sensor.octopus_energy_latest_electricity_consumption"
    
  @property
  def name(self):
    """Name of the sensor."""
    return "Octopus Energy Latest Electricity Consumption"

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
    """The current state of the sensor"""
    return self._state

  @property
  def last_reset(self):
    """The timestamp when the state was last reset for this sensor"""
    return self._last_reset

  async def async_update(self):
    """Retrieve the latest consumption"""
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
    self._last_reset = utcnow()

    self._state = 0

  @property
  def unique_id(self):
    """The id of sensor"""
    return "sensor.octopus_energy_latest_gas_consumption"
    
  @property
  def name(self):
    """Name of the sensor."""
    return "Octopus Energy Latest Gas Consumption"

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
    """The current state of the sensor"""
    return self._state

  @property
  def last_reset(self):
    """The timestamp when the state was last reset for this sensor"""
    return self._last_reset

  async def async_update(self):
    """Retrieve the latest consumption"""
    data = await self._client.async_latest_gas_consumption(self._mprn, self._serial_number)
    if data != None:
      self._state = data["consumption"]
      self._last_reset = data["interval_end"]
    else:
      self._state = 0
      self._last_reset = utcnow()