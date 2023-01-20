from datetime import timedelta
import logging
from custom_components.octopus_energy.utils import apply_offset

import re
import voluptuous as vol

from homeassistant.core import callback
from homeassistant.util.dt import (utcnow, now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers import config_validation as cv, entity_platform, service
from .const import (
  CONFIG_TARGET_OFFSET,
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_MPAN,
  CONFIG_TARGET_ROLLING_TARGET,
  
  REGEX_HOURS,
  REGEX_TIME,
  REGEX_OFFSET_PARTS,

  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_SAVING_SESSIONS_COORDINATOR,
  DATA_ACCOUNT
)

from .target_sensor_utils import (
  calculate_continuous_times,
  calculate_intermittent_times,
  is_target_rate_active
)

from .sensor_utils import (
  is_saving_sessions_event_active,
  get_next_saving_sessions_event
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_season_sensors(hass, entry, async_add_entities)
  elif CONFIG_TARGET_NAME in entry.data:
    await async_setup_target_sensors(hass, entry, async_add_entities)

  platform = entity_platform.async_get_current_platform()
  platform.async_register_entity_service(
    "update_target_config",
    vol.All(
      vol.Schema(
        {
          vol.Required("target_hours"): str,
          vol.Optional("target_start_time"): str,
          vol.Optional("target_end_time"): str,
          vol.Optional("target_offset"): str,
        },
        extra=vol.ALLOW_EXTRA,
      ),
      cv.has_at_least_one_key(
        "target_hours", "target_start_time", "target_end_time", "target_offset"
      ),
    ),
    "async_update_config",
  )

  return True

async def async_setup_season_sensors(hass, entry, async_add_entities):
  _LOGGER.debug('Setting up Season Saving entity')
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  saving_session_coordinator = hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR]

  await saving_session_coordinator.async_config_entry_first_refresh()

  async_add_entities([OctopusEnergySavingSessions(saving_session_coordinator)], True)

async def async_setup_target_sensors(hass, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)
  
  coordinator = hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR]

  account_info = hass.data[DOMAIN][DATA_ACCOUNT]

  mpan = config[CONFIG_TARGET_MPAN]

  is_export = False
  for point in account_info["electricity_meter_points"]:
    if point["mpan"] == mpan:
      for meter in point["meters"]:
        is_export = meter["is_export"]

  entities = [OctopusEnergyTargetRate(coordinator, config, is_export)]
  async_add_entities(entities, True)

class OctopusEnergyTargetRate(CoordinatorEntity, BinarySensorEntity):
  """Sensor for calculating when a target should be turned on or off."""

  def __init__(self, coordinator, config, is_export):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)

    self._config = config
    self._is_export = is_export
    self._attributes = self._config.copy()
    self._is_export = is_export
    self._attributes["is_target_export"] = is_export
    is_rolling_target = True
    if CONFIG_TARGET_ROLLING_TARGET in self._config:
      is_rolling_target = self._config[CONFIG_TARGET_ROLLING_TARGET]
    self._attributes[CONFIG_TARGET_ROLLING_TARGET] = is_rolling_target
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
            is_rolling_target,
            self._is_export
          )
        elif (self._config[CONFIG_TARGET_TYPE] == "Intermittent"):
          self._target_rates = calculate_intermittent_times(
            now(),
            start_time,
            end_time,
            target_hours,
            all_rates,
            offset,
            is_rolling_target,
            self._is_export
          )
        else:
          _LOGGER.error(f"Unexpected target type: {self._config[CONFIG_TARGET_TYPE]}")

        self._attributes["target_times"] = self._target_rates

    active_result = is_target_rate_active(current_date, self._target_rates, offset)

    if offset != None and active_result["next_time"] != None:
      self._attributes["next_time"] = apply_offset(active_result["next_time"], offset)
    else:
      self._attributes["next_time"] = active_result["next_time"]
    
    self._attributes["current_duration_in_hours"] = active_result["current_duration_in_hours"]
    self._attributes["next_duration_in_hours"] = active_result["next_duration_in_hours"]

    return active_result["is_active"]

  @callback
  def async_update_config(self, target_start_time=None, target_end_time=None, target_hours=None, target_offset=None):
    """Update sensors config"""

    config = dict(self._config)
    
    if target_hours is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_hours = target_hours.strip('\"')
      matches = re.search(REGEX_HOURS, trimmed_target_hours)
      if matches == None:
        raise vol.Invalid(f"Target hours of '{trimmed_target_hours}' must be in half hour increments.")
      else:
        trimmed_target_hours = float(trimmed_target_hours)
        if trimmed_target_hours % 0.5 != 0:
          raise vol.Invalid(f"Target hours of '{trimmed_target_hours}' must be in half hour increments.")
        else:
          config.update({
            CONFIG_TARGET_HOURS: trimmed_target_hours
          })

    if target_start_time is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_start_time = target_start_time.strip('\"')
      matches = re.search(REGEX_TIME, trimmed_target_start_time)
      if matches == None:
        raise vol.Invalid("Start time must be in the format HH:MM")
      else:
        config.update({
          CONFIG_TARGET_START_TIME: trimmed_target_start_time
        })

    if target_end_time is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_end_time = target_end_time.strip('\"')
      matches = re.search(REGEX_TIME, trimmed_target_end_time)
      if matches == None:
        raise vol.Invalid("End time must be in the format HH:MM")
      else:
        config.update({
          CONFIG_TARGET_END_TIME: trimmed_target_end_time
        })

    if target_offset is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_offset = target_offset.strip('\"')
      matches = re.search(REGEX_OFFSET_PARTS, trimmed_target_offset)
      if matches == None:
        raise vol.Invalid("Offset must be in the form of HH:MM:SS with an optional negative symbol")
      else:
        config.update({
          CONFIG_TARGET_OFFSET: trimmed_target_offset
        })

    self._config = config
    self._attributes = self._config.copy()
    self._attributes["is_target_export"] = self._is_export
    self._target_rates = []
    self.async_write_ha_state()

class OctopusEnergySavingSessions(CoordinatorEntity, BinarySensorEntity, RestoreEntity):
  """Sensor for determining if a saving session is active."""

  def __init__(self, coordinator):
    """Init sensor."""

    super().__init__(coordinator)
  
    self._state = None
    self._events = []
    self._attributes = {
      "joined_events": [],
      "next_joined_event_start": None
    }

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_saving_sessions"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Saving Session"

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
    saving_session = self.coordinator.data
    if (saving_session is not None and "events" in saving_session):
      self._events = saving_session["events"]
    else:
      self._events = []
    
    self._attributes = {
      "joined_events": self._events,
      "next_joined_event_start": None,
      "next_joined_event_end": None,
      "next_joined_event_duration_in_minutes": None
    }

    current_date = now()
    self._state = is_saving_sessions_event_active(current_date, self._events)
    next_event = get_next_saving_sessions_event(current_date, self._events)
    if (next_event is not None):
      self._attributes["next_joined_event_start"] = next_event["start"]
      self._attributes["next_joined_event_end"] = next_event["end"]
      self._attributes["next_joined_event_duration_in_minutes"] = next_event["duration_in_minutes"]

    return self._state

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
