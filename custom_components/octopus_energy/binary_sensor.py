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
from homeassistant.helpers.restore_state import RestoreEntity
from .const import (
  CONFIG_TARGET_OFFSET,
  DOMAIN,

  CONFIG_MAIN_ACCOUNT_ID,

  CONFIG_MAIN_API_KEY,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_MPAN,
  CONFIG_TARGET_ROLLING_TARGET,

  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_CLIENT
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

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_season_sensors(hass, entry, async_add_entities)
  elif CONFIG_TARGET_NAME in entry.data:
    if DOMAIN not in hass.data or DATA_ELECTRICITY_RATES_COORDINATOR not in hass.data[DOMAIN]:
      raise ConfigEntryNotReady
    
    await async_setup_target_sensors(hass, entry, async_add_entities)

  return True

async def async_setup_season_sensors(hass, entry, async_add_entities):
  _LOGGER.debug('Setting up Season Saving entity')
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  account_id = config[CONFIG_MAIN_ACCOUNT_ID]
  client = hass.data[DOMAIN][DATA_CLIENT]
  async_add_entities([OctopusEnergySeasonSaving(client, account_id)], True)

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
      _LOGGER.debug(f'Updating OctopusEnergyTargetRate {self._config[CONFIG_TARGET_NAME]}')

      # If all of our target times have passed, it's time to recalculate the next set
      all_rates_in_past = True
      for rate in self._target_rates:
        if rate["valid_to"] > current_date:
          all_rates_in_past = False
          break
      
      if all_rates_in_past:
        if self.coordinator.data != None:
          all_rates = self.coordinator.data
          
          # Retrieve our rates. For backwards compatibility, if CONFIG_TARGET_MPAN is not set, then pick the first set
          if CONFIG_TARGET_MPAN not in self._config:
            _LOGGER.debug(f"'CONFIG_TARGET_MPAN' not set.'{len(all_rates)}' rates available. Retrieving the first rate.")
            all_rates = next(iter(all_rates.values()))
          else:
            _LOGGER.debug(f"Retrieving rates for '{self._config[CONFIG_TARGET_MPAN]}'")
            all_rates = all_rates.get(self._config[CONFIG_TARGET_MPAN])
        else:
          _LOGGER.debug(f"Rate data missing. Setting to empty array")
          all_rates = []

        _LOGGER.debug(f'{len(all_rates) if all_rates != None else None} rate periods found')

        start_time = None
        if CONFIG_TARGET_START_TIME in self._config:
          start_time = self._config[CONFIG_TARGET_START_TIME]

        end_time = None
        if CONFIG_TARGET_END_TIME in self._config:
          end_time = self._config[CONFIG_TARGET_END_TIME]

        # True by default for backwards compatibility
        is_rolling_target = True
        if CONFIG_TARGET_ROLLING_TARGET in self._config:
          is_rolling_target = self._config[CONFIG_TARGET_ROLLING_TARGET]     

        target_hours = float(self._config[CONFIG_TARGET_HOURS])

        if (self._config[CONFIG_TARGET_TYPE] == "Continuous"):
          self._target_rates = calculate_continuous_times(
            now(),
            start_time,
            end_time,
            target_hours,
            all_rates,
            offset,
            is_rolling_target
          )
        elif (self._config[CONFIG_TARGET_TYPE] == "Intermittent"):
          self._target_rates = calculate_intermittent_times(
            now(),
            start_time,
            end_time,
            target_hours,
            all_rates,
            offset,
            is_rolling_target
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

class OctopusEnergySeasonSaving(BinarySensorEntity, RestoreEntity):
  """Sensor for determining if a season saving is active."""

  def __init__(self, client, account_id):
    """Init sensor."""
  
    self._state = None
    self._client = client
    self._account_id = account_id
    self._events = []
    self._attributes = {
      "joined_events": [],
      "next_joined_event_start": None
    }

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_season_savings"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Season Savings"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:leaf"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    """The state of the sensor."""

    return self._state

  async def async_update(self):
    current_date = utcnow()
    if (current_date.minute % 30) == 0 or len(self._events) == 0:
      events = await self._client.async_get_season_savings(self._account_id)

      self._events = events
      self._attributes = {
        "joined_events": events
      }

    self._attributes["next_joined_event_start"] = None

    current_date = now()
    for event in self._events:
      if (event["start"] <= current_date and event["end"] >= current_date):
        self._state = True

      if event["start"] > current_date and (self._attributes["next_joined_event_start"] == None or event["start"] < self._attributes["next_joined_event_start"]):
        self._attributes["next_joined_event_start"] = event["start"]

    self._state = False

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = state.state
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored state: {self._state}')
