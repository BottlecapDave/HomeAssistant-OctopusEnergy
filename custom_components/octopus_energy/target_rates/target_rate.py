import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (utcnow, now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.helpers import translation

from ..const import (
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
  DATA_ACCOUNT,
  DOMAIN,
)

from . import (
  calculate_continuous_times,
  calculate_intermittent_times,
  get_applicable_rates,
  get_target_rate_info
)

from ..config.target_rates import validate_target_rate_config
from ..target_rates.repairs import check_for_errors
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyTargetRate(CoordinatorEntity, BinarySensorEntity, RestoreEntity):
  """Sensor for calculating when a target should be turned on or off."""

  def __init__(self, hass: HomeAssistant, account_id: str, coordinator, config, is_export):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)

    self._state = None
    self._config = config
    self._is_export = is_export
    self._attributes = self._config.copy()
    self._is_export = is_export
    self._attributes["is_target_export"] = is_export
    self._last_evaluated = None
    self._account_id = account_id
    
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

    check_for_errors(self._hass, self._config, account_info, now())

    # Find the current rate. Rates change a maximum of once every 30 minutes.
    current_date = utcnow()

    if (current_date.minute % 30) == 0 or len(self._target_rates) == 0 or self._last_evaluated is None or self._last_evaluated + timedelta(minutes=30) < current_date:
      _LOGGER.debug(f'Updating OctopusEnergyTargetRate {self._config[CONFIG_TARGET_NAME]}')
      self._last_evaluated = current_date

      # If all of our target times have passed, it's time to recalculate the next set
      all_rates_in_past = True
      for rate in self._target_rates:
        if rate["end"] > current_date:
          all_rates_in_past = False
          break
      
      if all_rates_in_past:
        if self.coordinator is not None and self.coordinator.data is not None:
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

          find_highest_rates = (self._is_export and invert_target_rates == False) or (self._is_export == False and invert_target_rates)

          applicable_rates = get_applicable_rates(
            current_date,
            start_time,
            end_time,
            all_rates,
            is_rolling_target
          )

          if (self._config[CONFIG_TARGET_TYPE] == "Continuous"):
            self._target_rates = calculate_continuous_times(
              applicable_rates,
              target_hours,
              find_highest_rates,
              find_last_rates
            )
          elif (self._config[CONFIG_TARGET_TYPE] == "Intermittent"):
            self._target_rates = calculate_intermittent_times(
              applicable_rates,
              target_hours,
              find_highest_rates,
              find_last_rates
            )
          else:
            _LOGGER.error(f"Unexpected target type: {self._config[CONFIG_TARGET_TYPE]}")

          self._attributes["rates_incomplete"] = applicable_rates is None
          self._attributes["target_times"] = self._target_rates
          self._attributes["target_times_last_evaluated"] = current_date
          _LOGGER.debug(f"calculated rates: {self._target_rates}")

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
    
    self._attributes["last_evaluated"] = current_date
    self._state = active_result["is_active"]

    _LOGGER.debug(f"calculated: {self._state}")
    super()._handle_coordinator_update()
  
  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state == "unknown" else state.state
      self._attributes = dict_to_typed_dict(
        state.attributes,
        [CONFIG_TARGET_OLD_NAME, CONFIG_TARGET_OLD_HOURS, CONFIG_TARGET_OLD_TYPE, CONFIG_TARGET_OLD_START_TIME, CONFIG_TARGET_OLD_END_TIME, CONFIG_TARGET_OLD_MPAN]
      )
      # Make sure our attributes don't override any changed settings
      self._attributes.update(self._config)
    
      _LOGGER.debug(f'Restored OctopusEnergyTargetRate state: {self._state}')

  @callback
  async def async_update_config(self, target_start_time=None, target_end_time=None, target_hours=None, target_offset=None):
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