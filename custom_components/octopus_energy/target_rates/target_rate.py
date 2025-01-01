import logging
from datetime import timedelta
import math

import voluptuous as vol

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (utcnow, now)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.helpers import translation

from ..const import (
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE,
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST,
  CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING,
  CONFIG_TARGET_HOURS_MODE,
  CONFIG_TARGET_MAX_RATE,
  CONFIG_TARGET_MIN_RATE,
  CONFIG_TARGET_MPAN,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_OLD_END_TIME,
  CONFIG_TARGET_OLD_HOURS,
  CONFIG_TARGET_OLD_MPAN,
  CONFIG_TARGET_OLD_NAME,
  CONFIG_TARGET_OLD_START_TIME,
  CONFIG_TARGET_OLD_TYPE,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_ROLLING_TARGET,
  CONFIG_TARGET_LAST_RATES,
  CONFIG_TARGET_INVERT_TARGET_RATES,
  CONFIG_TARGET_OFFSET,
  CONFIG_TARGET_TYPE_CONTINUOUS,
  CONFIG_TARGET_TYPE_INTERMITTENT,
  CONFIG_TARGET_WEIGHTING,
  DATA_ACCOUNT,
  DATA_CUSTOM_RATE_WEIGHTINGS_KEY,
  DOMAIN,
)

from . import (
  apply_free_electricity_weighting,
  calculate_continuous_times,
  calculate_intermittent_times,
  compare_config,
  create_weighting,
  extract_config,
  get_applicable_rates,
  get_target_rate_info,
  should_evaluate_target_rates
)

from ..config.target_rates import validate_target_rate_config
from ..target_rates.repairs import check_for_errors
from ..utils.attributes import dict_to_typed_dict
from ..coordinators import MultiCoordinatorEntity
from ..coordinators.free_electricity_sessions import FreeElectricitySessionsCoordinatorResult
from ..utils.weightings import apply_weighting

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyTargetRate(MultiCoordinatorEntity, BinarySensorEntity, RestoreEntity):
  """Sensor for calculating when a target should be turned on or off."""
  
  _unrecorded_attributes = frozenset({"data_last_retrieved", "target_times_last_evaluated"})

  def __init__(self, hass: HomeAssistant, account_id: str, config_entry, config, is_export, coordinator, free_electricity_coordinator):
    """Init sensor."""
    # Pass coordinator to base class
    MultiCoordinatorEntity.__init__(self, coordinator, [free_electricity_coordinator])

    self._state = None
    self._config_entry = config_entry
    self._config = config
    self._is_export = is_export
    self._attributes = self._config.copy()
    self._is_export = is_export
    self._attributes["is_target_export"] = is_export
    self._last_evaluated = None
    self._account_id = account_id
    self._free_electricity_coordinator = free_electricity_coordinator
    
    is_rolling_target = True
    if CONFIG_TARGET_ROLLING_TARGET in self._config:
      is_rolling_target = self._config[CONFIG_TARGET_ROLLING_TARGET]
    self._attributes[CONFIG_TARGET_ROLLING_TARGET] = is_rolling_target

    find_last_rates = False
    if CONFIG_TARGET_LAST_RATES in self._config:
      find_last_rates = self._config[CONFIG_TARGET_LAST_RATES]
    self._attributes[CONFIG_TARGET_LAST_RATES] = find_last_rates

    self._target_rates = []
    
    self._hass = hass
    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

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
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determines if the target rate sensor is active."""
    if CONFIG_TARGET_OFFSET in self._config:
      offset = self._config[CONFIG_TARGET_OFFSET]
    else:
      offset = None

    account_result = self._hass.data[DOMAIN][self._account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None

    current_local_date = now()
    check_for_errors(self._hass, self._config, account_info, current_local_date)

    # Find the current rate. Rates change a maximum of once every 30 minutes.
    current_date = utcnow()

    if ((current_date.minute % 30) == 0 or
        self._target_rates is None or
        len(self._target_rates) == 0 or
        self._last_evaluated is None or
        self._last_evaluated + timedelta(minutes=30) < current_date):
      _LOGGER.debug(f'Updating OctopusEnergyTargetRate {self._config[CONFIG_TARGET_NAME]}')
      self._last_evaluated = current_date

      should_evaluate = should_evaluate_target_rates(current_date, self._target_rates, self._config[CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE] if CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE in self._config else CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST)
      if should_evaluate:
        if self.coordinator is not None and self.coordinator.data is not None and self.coordinator.data.rates is not None:
          all_rates = self.coordinator.data.rates
        else:
          _LOGGER.debug(f"Rate data missing. Setting to empty array")
          all_rates = []

        _LOGGER.debug(f'{len(all_rates) if all_rates is not None else None} rate periods found')

        if len(all_rates) > 0:
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

          find_last_rates = False
          if CONFIG_TARGET_LAST_RATES in self._config:
            find_last_rates = self._config[CONFIG_TARGET_LAST_RATES]     

          target_hours = float(self._config[CONFIG_TARGET_HOURS])

          invert_target_rates = False
          if (CONFIG_TARGET_INVERT_TARGET_RATES in self._config):
            invert_target_rates = self._config[CONFIG_TARGET_INVERT_TARGET_RATES]

          min_rate = None
          if CONFIG_TARGET_MIN_RATE in self._config:
            min_rate = self._config[CONFIG_TARGET_MIN_RATE]

          max_rate = None
          if CONFIG_TARGET_MAX_RATE in self._config:
            max_rate = self._config[CONFIG_TARGET_MAX_RATE]

          find_highest_rates = (self._is_export and invert_target_rates == False) or (self._is_export == False and invert_target_rates)

          applicable_rates = get_applicable_rates(
            current_local_date,
            start_time,
            end_time,
            all_rates,
            is_rolling_target
          )

          free_electricity_sessions: FreeElectricitySessionsCoordinatorResult = self._free_electricity_coordinator.data if self._free_electricity_coordinator is not None else None
          applicable_rates = apply_free_electricity_weighting(
            applicable_rates,
            free_electricity_sessions.events if free_electricity_sessions is not None else [],
            self._config[CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING] if CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING in self._config else 1
          )

          weightings_key = DATA_CUSTOM_RATE_WEIGHTINGS_KEY.format(self._config[CONFIG_TARGET_MPAN])
          applicable_rates = apply_weighting(
            applicable_rates,
            self._hass.data[DOMAIN][self._account_id][weightings_key] 
            if weightings_key in self._hass.data[DOMAIN][self._account_id] 
            else []
          )

          if applicable_rates is not None:
            number_of_slots = math.ceil(target_hours * 2)
            weighting = create_weighting(self._config[CONFIG_TARGET_WEIGHTING] if CONFIG_TARGET_WEIGHTING in self._config else None, number_of_slots)

            if (self._config[CONFIG_TARGET_TYPE] == CONFIG_TARGET_TYPE_CONTINUOUS):
              self._target_rates = calculate_continuous_times(
                applicable_rates,
                target_hours,
                find_highest_rates,
                find_last_rates,
                min_rate,
                max_rate,
                weighting,
                hours_mode = self._config[CONFIG_TARGET_HOURS_MODE]
              )
            elif (self._config[CONFIG_TARGET_TYPE] == CONFIG_TARGET_TYPE_INTERMITTENT):
              self._target_rates = calculate_intermittent_times(
                applicable_rates,
                target_hours,
                find_highest_rates,
                find_last_rates,
                min_rate,
                max_rate,
                hours_mode = self._config[CONFIG_TARGET_HOURS_MODE]
              )
            else:
              _LOGGER.error(f"Unexpected target type: {self._config[CONFIG_TARGET_TYPE]}")

            self._attributes["target_times"] = self._target_rates
            self._attributes["target_times_last_evaluated"] = current_date
            _LOGGER.debug(f"calculated rates: {self._target_rates}")
          
          self._attributes["rates_incomplete"] = applicable_rates is None

    active_result = get_target_rate_info(current_date, self._target_rates, offset)

    self._attributes["overall_average_cost"] = active_result["overall_average_cost"]
    self._attributes["overall_min_cost"] = active_result["overall_min_cost"]
    self._attributes["overall_max_cost"] = active_result["overall_max_cost"]

    self._attributes["current_duration_in_hours"] = active_result["current_duration_in_hours"]
    self._attributes["current_average_cost"] = active_result["current_average_cost"]
    self._attributes["current_min_cost"] = active_result["current_min_cost"]
    self._attributes["current_max_cost"] = active_result["current_max_cost"]

    self._attributes["next_time"] = active_result["next_time"]
    self._attributes["next_duration_in_hours"] = active_result["next_duration_in_hours"]
    self._attributes["next_average_cost"] = active_result["next_average_cost"]
    self._attributes["next_min_cost"] = active_result["next_min_cost"]
    self._attributes["next_max_cost"] = active_result["next_max_cost"]
    
    self._state = active_result["is_active"]

    _LOGGER.debug(f"calculated: {self._state}")
    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()
  
  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or state.state is None else state.state.lower() == 'on'
      self._attributes = dict_to_typed_dict(
        state.attributes,
        [CONFIG_TARGET_OLD_NAME, CONFIG_TARGET_OLD_HOURS, CONFIG_TARGET_OLD_TYPE, CONFIG_TARGET_OLD_START_TIME, CONFIG_TARGET_OLD_END_TIME, CONFIG_TARGET_OLD_MPAN]
      )

      self._target_rates = self._attributes["target_times"] if "target_times" in self._attributes else []

      # Reset everything if our settings have changed
      if compare_config(self._config, self._attributes) == False:
        self._state = False
        self._attributes = self._config.copy()
        self._attributes["is_target_export"] = self._is_export
        self._target_rates = None
    
      _LOGGER.debug(f'Restored OctopusEnergyTargetRate state: {self._state}')

  @callback
  async def async_update_target_rate_config(self, target_start_time=None, target_end_time=None, target_hours=None, target_offset=None, target_minimum_rate=None, target_maximum_rate=None, target_weighting=None, persist_changes=False):
    """Update sensors config"""

    config = dict(self._config)
    if target_hours is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_hours = target_hours.strip('\"')
      config.update({
        CONFIG_TARGET_HOURS: trimmed_target_hours
      })

    if target_start_time is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_start_time = target_start_time.strip('\"')
      config.update({
        CONFIG_TARGET_START_TIME: trimmed_target_start_time
      })

    if target_end_time is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_end_time = target_end_time.strip('\"')
      config.update({
        CONFIG_TARGET_END_TIME: trimmed_target_end_time
      })

    if target_offset is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_offset = target_offset.strip('\"')
      config.update({
        CONFIG_TARGET_OFFSET: trimmed_target_offset
      })

    if target_minimum_rate is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_minimum_rate = target_minimum_rate.strip('\"')
      config.update({
        CONFIG_TARGET_MIN_RATE: trimmed_target_minimum_rate if trimmed_target_minimum_rate != "" else None
      })

    if target_maximum_rate is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_maximum_rate = target_maximum_rate.strip('\"')
      config.update({
        CONFIG_TARGET_MAX_RATE: trimmed_target_maximum_rate if trimmed_target_maximum_rate != "" else None
      })

    if target_weighting is not None:
      # Inputs from automations can include quotes, so remove these
      trimmed_target_weighting = target_weighting.strip('\"')
      config.update({
        CONFIG_TARGET_WEIGHTING: trimmed_target_weighting if trimmed_target_weighting != "" else None
      })

    account_result = self._hass.data[DOMAIN][self._account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None

    errors = validate_target_rate_config(config, account_info, now())
    keys = list(errors.keys())
    if (len(keys)) > 0:
      translations = await translation.async_get_translations(self._hass, self._hass.config.language, "options", {DOMAIN})
      raise vol.Invalid(translations[f'component.{DOMAIN}.options.error.{errors[keys[0]]}'])

    self._config = config
    self._attributes = self._config.copy()
    self._attributes["is_target_export"] = self._is_export
    self._target_rates = []
    self.async_write_ha_state()

    if persist_changes:
      updatable_keys = [CONFIG_TARGET_HOURS, CONFIG_TARGET_START_TIME, CONFIG_TARGET_END_TIME, CONFIG_TARGET_OFFSET, CONFIG_TARGET_MIN_RATE, CONFIG_TARGET_MAX_RATE, CONFIG_TARGET_WEIGHTING]
      new_config_data = { **self._config_entry.data }
      new_config_data.update(extract_config(config, updatable_keys))
      new_config_options = { **self._config_entry.options }
      new_config_options.update(extract_config(config, updatable_keys))

      self._hass.config_entries.async_update_entry(
        self._config_entry,
        data = new_config_data,
        options = new_config_options
      )