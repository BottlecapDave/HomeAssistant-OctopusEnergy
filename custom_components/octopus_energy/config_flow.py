import voluptuous as vol
import logging

from homeassistant.util.dt import (utcnow)
from homeassistant.config_entries import (ConfigFlow, OptionsFlow)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .config.target_rates import merge_target_rate_config, validate_target_rate_config
from .config.main import async_validate_main_config, merge_main_config
from .const import (
  CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_DEFAULT_PREVIOUS_CONSUMPTION_OFFSET_IN_DAYS,
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_TARGET_RATE,
  CONFIG_MAIN_ACCOUNT_ID,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET,
  CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET,
  CONFIG_TARGET_ACCOUNT_ID,
  CONFIG_VERSION,
  DOMAIN,
  
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION,
  CONFIG_MAIN_CALORIFIC_VALUE,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,
  
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_MPAN,
  CONFIG_TARGET_OFFSET,
  CONFIG_TARGET_ROLLING_TARGET,
  CONFIG_TARGET_LAST_RATES,
  CONFIG_TARGET_INVERT_TARGET_RATES,

  DATA_SCHEMA_ACCOUNT,
  DATA_CLIENT,
  DATA_ACCOUNT_ID,
)

from .utils import get_active_tariff_code

_LOGGER = logging.getLogger(__name__)

def get_target_rate_meters(account_info, now):
  meters = {}
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff_code = get_active_tariff_code(now, point["agreements"])

      is_export = False
      for meter in point["meters"]:
        if meter["is_export"] == True:
          is_export = True
          break

      if active_tariff_code is not None:
        meters[point["mpan"]] = f'{point["mpan"]} ({"Export" if is_export == True else "Import"})'

  return meters

class OctopusEnergyConfigFlow(ConfigFlow, domain=DOMAIN): 
  """Config flow."""

  VERSION = CONFIG_VERSION

  def get_account_ids(self):
    account_ids = {}
    for entry in self.hass.config_entries.async_entries(DOMAIN):
      if CONFIG_KIND in entry.data and entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
        account_id = entry.data[CONFIG_MAIN_ACCOUNT_ID]
        account_ids[account_id] = account_id

    return account_ids

  async def async_setup_initial_account(self, user_input):
    """Setup the initial account based on the provided user input"""
    errors = await async_validate_main_config(user_input)

    if len(errors) < 1:
      user_input[CONFIG_KIND] = CONFIG_KIND_ACCOUNT
      return self.async_create_entry(
        title=user_input[CONFIG_MAIN_ACCOUNT_ID], 
        data=user_input
      )

    return self.async_show_form(
      step_id="user", data_schema=DATA_SCHEMA_ACCOUNT, errors=errors
    )

  async def async_setup_target_rate_schema(self):
    client = self.hass.data[DOMAIN][DATA_CLIENT]
    account_info = await client.async_get_account(self.hass.data[DOMAIN][DATA_ACCOUNT_ID])

    now = utcnow()
    meters = get_target_rate_meters(account_info, now)

    return vol.Schema({
      vol.Required(CONFIG_TARGET_NAME): str,
      vol.Required(CONFIG_TARGET_HOURS): str,
      vol.Required(CONFIG_TARGET_TYPE, default="Continuous"): vol.In({
        "Continuous": "Continuous",
        "Intermittent": "Intermittent"
      }),
      vol.Required(CONFIG_TARGET_MPAN): vol.In(
        meters
      ),
      vol.Optional(CONFIG_TARGET_START_TIME): str,
      vol.Optional(CONFIG_TARGET_END_TIME): str,
      vol.Optional(CONFIG_TARGET_OFFSET): str,
      vol.Optional(CONFIG_TARGET_ROLLING_TARGET, default=False): bool,
      vol.Optional(CONFIG_TARGET_LAST_RATES, default=False): bool,
      vol.Optional(CONFIG_TARGET_INVERT_TARGET_RATES, default=False): bool,
    })

  async def async_step_target_rate(self, user_input):
    """Setup a target based on the provided user input"""
    client = self.hass.data[DOMAIN][DATA_CLIENT]
    account_info = await client.async_get_account(self.hass.data[DOMAIN][DATA_ACCOUNT_ID])

    now = utcnow()
    errors = validate_target_rate_config(user_input, account_info, now)
    account_ids = self.get_account_ids()

    if len(errors) < 1:
      user_input[CONFIG_KIND] = CONFIG_KIND_TARGET_RATE
      user_input[CONFIG_TARGET_ACCOUNT_ID] = list(account_ids.keys())[0]
      # Setup our targets sensor
      return self.async_create_entry(
        title=f"{user_input[CONFIG_TARGET_NAME]} (target)", 
        data=user_input
      )

    # Reshow our form with raised logins
    data_Schema = await self.async_setup_target_rate_schema()
    return self.async_show_form(
      step_id="target_rate", data_schema=data_Schema, errors=errors
    )

  async def async_step_user(self, user_input):
    """Setup based on user config"""

    is_account_setup = False
    for entry in self._async_current_entries(include_ignore=False):
      if CONFIG_MAIN_API_KEY in entry.data:
        is_account_setup = True
        break

    if user_input is not None:
      # We are setting up our initial stage
      if CONFIG_MAIN_API_KEY in user_input:
        return await self.async_setup_initial_account(user_input)

      # We are setting up a target
      if CONFIG_TARGET_NAME in user_input:
        return await self.async_step_target_rate(user_input)

    if is_account_setup:
      data_Schema = await self.async_setup_target_rate_schema()
      return self.async_show_form(
        step_id="target_rate", data_schema=data_Schema
      )

    return self.async_show_form(
      step_id="user", data_schema=DATA_SCHEMA_ACCOUNT
    )

  @staticmethod
  @callback
  def async_get_options_flow(entry):
    return OptionsFlowHandler(entry)

class OptionsFlowHandler(OptionsFlow):
  """Handles options flow for the component."""

  def __init__(self, entry) -> None:
    self._entry = entry

  async def __async_setup_target_rate_schema(self, config, errors):
    client = self.hass.data[DOMAIN][DATA_CLIENT]
    account_info = await client.async_get_account(self.hass.data[DOMAIN][DATA_ACCOUNT_ID])
    if account_info is None:
      errors[CONFIG_TARGET_MPAN] = "account_not_found"

    now = utcnow()
    meters = get_target_rate_meters(account_info, now)

    if (CONFIG_TARGET_MPAN not in config):
      config[CONFIG_TARGET_MPAN] = meters[0]

    start_time_key = vol.Optional(CONFIG_TARGET_START_TIME)
    if (CONFIG_TARGET_START_TIME in config):
      start_time_key = vol.Optional(CONFIG_TARGET_START_TIME, default=config[CONFIG_TARGET_START_TIME])

    end_time_key = vol.Optional(CONFIG_TARGET_END_TIME)
    if (CONFIG_TARGET_END_TIME in config):
      end_time_key = vol.Optional(CONFIG_TARGET_END_TIME, default=config[CONFIG_TARGET_END_TIME])

    offset_key = vol.Optional(CONFIG_TARGET_OFFSET)
    if (CONFIG_TARGET_OFFSET in config):
      offset_key = vol.Optional(CONFIG_TARGET_OFFSET, default=config[CONFIG_TARGET_OFFSET])

    # True by default for backwards compatibility
    is_rolling_target = True
    if (CONFIG_TARGET_ROLLING_TARGET in config):
      is_rolling_target = config[CONFIG_TARGET_ROLLING_TARGET]

    find_last_rates = False
    if (CONFIG_TARGET_LAST_RATES in config):
      find_last_rates = config[CONFIG_TARGET_LAST_RATES]

    invert_target_rates = False
    if (CONFIG_TARGET_INVERT_TARGET_RATES in config):
      invert_target_rates = config[CONFIG_TARGET_INVERT_TARGET_RATES]
    
    return self.async_show_form(
      step_id="target_rate",
      data_schema=self.add_suggested_values_to_schema(
          vol.Schema({
            vol.Required(CONFIG_TARGET_NAME): str,
            vol.Required(CONFIG_TARGET_HOURS): str,
            vol.Required(CONFIG_TARGET_TYPE): vol.In({
              "Continuous": "Continuous",
              "Intermittent": "Intermittent"
            }),
            vol.Required(CONFIG_TARGET_MPAN): vol.In(
              meters
            ),
            start_time_key: str,
            end_time_key: str,
            offset_key: str,
            vol.Optional(CONFIG_TARGET_ROLLING_TARGET): bool,
            vol.Optional(CONFIG_TARGET_LAST_RATES): bool,
            vol.Optional(CONFIG_TARGET_INVERT_TARGET_RATES): bool,
          }),
          {
            CONFIG_TARGET_NAME: config[CONFIG_TARGET_NAME],
            CONFIG_TARGET_HOURS: f'{config[CONFIG_TARGET_HOURS]}',
            CONFIG_TARGET_TYPE: config[CONFIG_TARGET_TYPE],
            CONFIG_TARGET_MPAN: config[CONFIG_TARGET_MPAN],
            CONFIG_TARGET_ROLLING_TARGET: is_rolling_target,
            CONFIG_TARGET_LAST_RATES: find_last_rates,
            CONFIG_TARGET_INVERT_TARGET_RATES: invert_target_rates,
          }
      ),
      errors=errors
    )
  
  async def __async_setup_main_schema(self, config, errors):
    supports_live_consumption = False
    if CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in config:
      supports_live_consumption = config[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION]

    live_electricity_consumption_refresh_in_minutes = CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES
    if CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES in config:
      live_electricity_consumption_refresh_in_minutes = config[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES]

    live_gas_consumption_refresh_in_minutes = CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES
    if CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES in config:
      live_gas_consumption_refresh_in_minutes = config[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES]

    previous_electricity_consumption_days_offset = CONFIG_DEFAULT_PREVIOUS_CONSUMPTION_OFFSET_IN_DAYS
    if CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET in config:
      previous_electricity_consumption_days_offset = config[CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET]

    previous_gas_consumption_days_offset = CONFIG_DEFAULT_PREVIOUS_CONSUMPTION_OFFSET_IN_DAYS
    if CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET in config:
      previous_gas_consumption_days_offset = config[CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET]
    
    calorific_value = 40
    if CONFIG_MAIN_CALORIFIC_VALUE in config:
      calorific_value = config[CONFIG_MAIN_CALORIFIC_VALUE]
    
    return self.async_show_form(
      step_id="user",
      data_schema=self.add_suggested_values_to_schema(
        vol.Schema({
          vol.Required(CONFIG_MAIN_API_KEY): str,
          vol.Required(CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION): bool,
          vol.Required(CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES): cv.positive_int,
          vol.Required(CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES): cv.positive_int,
          vol.Required(CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET): cv.positive_int,
          vol.Required(CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET): cv.positive_int,
          vol.Required(CONFIG_MAIN_CALORIFIC_VALUE): cv.positive_float,
          vol.Optional(CONFIG_MAIN_ELECTRICITY_PRICE_CAP): cv.positive_float,
          vol.Optional(CONFIG_MAIN_GAS_PRICE_CAP): cv.positive_float,
        }),
        {
          CONFIG_MAIN_API_KEY: config[CONFIG_MAIN_API_KEY],
          CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: supports_live_consumption,
          CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: live_electricity_consumption_refresh_in_minutes,
          CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: live_gas_consumption_refresh_in_minutes,
          CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET: previous_electricity_consumption_days_offset,
          CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET: previous_gas_consumption_days_offset,
          CONFIG_MAIN_CALORIFIC_VALUE: calorific_value,
          CONFIG_MAIN_ELECTRICITY_PRICE_CAP: config[CONFIG_MAIN_ELECTRICITY_PRICE_CAP] if CONFIG_MAIN_ELECTRICITY_PRICE_CAP in config else None,
          CONFIG_MAIN_GAS_PRICE_CAP: config[CONFIG_MAIN_GAS_PRICE_CAP] if CONFIG_MAIN_GAS_PRICE_CAP in config else None,
        }
      ),
      errors=errors
    )

  async def async_step_init(self, user_input):
    """Manage the options for the custom component."""

    if CONFIG_MAIN_API_KEY in self._entry.data:
      config = merge_main_config(self._entry.data, self._entry.options, user_input)
      return await self.__async_setup_main_schema(config, {})
    elif CONFIG_TARGET_TYPE in self._entry.data:
      config = merge_target_rate_config(self._entry.data, self._entry.options, user_input)
      
      return await self.__async_setup_target_rate_schema(config, {})

    return self.async_abort(reason="not_supported")

  async def async_step_user(self, user_input):
    """Manage the options for the custom component."""

    config = merge_main_config(self._entry.data, self._entry.options, user_input)

    errors = await async_validate_main_config(config)
    
    if (len(errors) > 0):
      return await self.__async_setup_main_schema(config, errors)

    return self.async_create_entry(title="", data=config)

  async def async_step_target_rate(self, user_input):
    """Manage the options for the custom component."""

    config = merge_target_rate_config(self._entry.data, self._entry.options, user_input)

    client = self.hass.data[DOMAIN][DATA_CLIENT]
    account_info = await client.async_get_account(self.hass.data[DOMAIN][DATA_ACCOUNT_ID])

    now = utcnow()
    errors = validate_target_rate_config(user_input, account_info, now)

    if (len(errors) > 0):
      return await self.__async_setup_target_rate_schema(config, errors)

    return self.async_create_entry(title="", data=config)