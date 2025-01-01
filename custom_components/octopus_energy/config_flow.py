from decimal import Decimal
import voluptuous as vol
import logging

from homeassistant.util.dt import (utcnow)
from homeassistant.config_entries import (ConfigFlow, OptionsFlow)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector
from homeassistant.components.sensor import (
  SensorDeviceClass,
)

from .coordinators.account import AccountCoordinatorResult
from .config.cost_tracker import merge_cost_tracker_config, validate_cost_tracker_config
from .config.target_rates import merge_target_rate_config, validate_target_rate_config
from .config.main import async_validate_main_config, merge_main_config
from .const import (
  CONFIG_COST_TRACKER_MANUAL_RESET,
  CONFIG_FAVOUR_DIRECT_DEBIT_RATES,
  CONFIG_KIND_ROLLING_TARGET_RATE,
  CONFIG_MAIN_HOME_PRO_ADDRESS,
  CONFIG_MAIN_HOME_PRO_API_KEY,
  CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD,
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE,
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST,
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST,
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS,
  CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING,
  CONFIG_TARGET_HOURS_MODE,
  CONFIG_TARGET_HOURS_MODE_EXACT,
  CONFIG_TARGET_HOURS_MODE_MAXIMUM,
  CONFIG_TARGET_HOURS_MODE_MINIMUM,
  CONFIG_TARIFF_COMPARISON_MPAN_MPRN,
  CONFIG_TARIFF_COMPARISON_NAME,
  CONFIG_TARIFF_COMPARISON_PRODUCT_CODE,
  CONFIG_TARIFF_COMPARISON_TARIFF_CODE,
  CONFIG_COST_TRACKER_ENTITY_ACCUMULATIVE_VALUE,
  CONFIG_COST_TRACKER_MONTH_DAY_RESET,
  CONFIG_COST_TRACKER_TARGET_ENTITY_ID,
  CONFIG_COST_TRACKER_MPAN,
  CONFIG_COST_TRACKER_NAME,
  CONFIG_COST_TRACKER_WEEKDAY_RESET,
  CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_TARIFF_COMPARISON,
  CONFIG_KIND_COST_TRACKER,
  CONFIG_KIND_TARGET_RATE,
  CONFIG_ACCOUNT_ID,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_TARGET_MAX_RATE,
  CONFIG_TARGET_MIN_RATE,
  CONFIG_TARGET_TYPE_CONTINUOUS,
  CONFIG_TARGET_TYPE_INTERMITTENT,
  CONFIG_TARGET_WEIGHTING,
  CONFIG_VERSION,
  DATA_ACCOUNT,
  DATA_CLIENT,
  DEFAULT_CALORIFIC_VALUE,
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
)
from .config.tariff_comparison import async_validate_tariff_comparison_config, merge_tariff_comparison_config
from .config.rolling_target_rates import merge_rolling_target_rate_config, validate_rolling_target_rate_config

from .utils import get_active_tariff

_LOGGER = logging.getLogger(__name__)

def get_electricity_meters(account_info, now):
  meters = []
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff = get_active_tariff(now, point["agreements"])

      is_export = False
      for meter in point["meters"]:
        if meter["is_export"] == True:
          is_export = True
          break

      if active_tariff is not None:
        meters.append(selector.SelectOptionDict(value=point["mpan"], label= f'{point["mpan"]} ({"Export" if is_export == True else "Import"})'))

  return meters

def get_all_meters(account_info, now):
  meters = []
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff = get_active_tariff(now, point["agreements"])

      is_export = False
      for meter in point["meters"]:
        if meter["is_export"] == True:
          is_export = True
          break

      if active_tariff is not None:
        meters.append(selector.SelectOptionDict(value=point["mpan"], label= f'{point["mpan"]} ({"Export" if is_export == True else "Import"} Electricity)'))

  if account_info is not None and len(account_info["gas_meter_points"]) > 0:
    for point in account_info["gas_meter_points"]:
      active_tariff = get_active_tariff(now, point["agreements"])

      if active_tariff is not None:
        meters.append(selector.SelectOptionDict(value=point["mprn"], label= f'{point["mprn"]} (Gas)'))

  return meters

def get_weekday_options():
  return [
    selector.SelectOptionDict(value="0", label="Monday"),
    selector.SelectOptionDict(value="1", label="Tuesday"),
    selector.SelectOptionDict(value="2", label="Wednesday"),
    selector.SelectOptionDict(value="3", label="Thursday"),
    selector.SelectOptionDict(value="4", label="Friday"),
    selector.SelectOptionDict(value="5", label="Saturday"),
    selector.SelectOptionDict(value="6", label="Sunday"),
  ]

def get_account_ids(hass):
    account_ids: list[str] = []
    for entry in hass.config_entries.async_entries(DOMAIN):
      if CONFIG_KIND in entry.data and entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
        account_id = entry.data[CONFIG_ACCOUNT_ID]
        account_ids.append(account_id)

    return account_ids

class OctopusEnergyConfigFlow(ConfigFlow, domain=DOMAIN): 
  """Config flow."""

  VERSION = CONFIG_VERSION

  async def async_step_account(self, user_input):
    """Setup the initial account based on the provided user input"""
    account_ids = get_account_ids(self.hass)
    errors = await async_validate_main_config(user_input, account_ids) if user_input is not None else {}

    if len(errors) < 1 and user_input is not None:
      user_input[CONFIG_KIND] = CONFIG_KIND_ACCOUNT
      return self.async_create_entry(
        title=user_input[CONFIG_ACCOUNT_ID], 
        data=user_input
      )

    return self.async_show_form(
      step_id="account",
      data_schema=self.add_suggested_values_to_schema(
        DATA_SCHEMA_ACCOUNT,
        user_input if user_input is not None else {}
      ),
      errors=errors
    )
  
  def __capture_account_id__(self, step_id: str):
    account_ids = get_account_ids(self.hass)
    account_id_options = []
    for account_id in account_ids:
      account_id_options.append(selector.SelectOptionDict(value=account_id, label=account_id.upper()))

    return self.async_show_form(
      step_id=step_id,
      data_schema=vol.Schema({
        vol.Required(CONFIG_ACCOUNT_ID): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=account_id_options,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
      })
    )

  async def __async_setup_target_rate_schema__(self, account_id: str):
    account_info: AccountCoordinatorResult | None = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT] if account_id is not None and account_id in self.hass.data[DOMAIN] else None
    if (account_info is None):
      return self.async_abort(reason="account_not_found")

    now = utcnow()
    meters = get_electricity_meters(account_info.account, now)

    return vol.Schema({
      vol.Required(CONFIG_TARGET_NAME): str,
      vol.Required(CONFIG_TARGET_HOURS): str,
      vol.Required(CONFIG_TARGET_HOURS_MODE, default=CONFIG_TARGET_HOURS_MODE_EXACT): selector.SelectSelector(
          selector.SelectSelectorConfig(
              options=[
                selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_EXACT, label="Exact"),
                selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MINIMUM, label="Minimum"),
                selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MAXIMUM, label="Maximum"),
              ],
              mode=selector.SelectSelectorMode.DROPDOWN,
          )
      ),
      vol.Required(CONFIG_TARGET_TYPE, default=CONFIG_TARGET_TYPE_CONTINUOUS): selector.SelectSelector(
          selector.SelectSelectorConfig(
              options=[
                selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_CONTINUOUS, label="Continuous"),
                selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_INTERMITTENT, label="Intermittent"),
              ],
              mode=selector.SelectSelectorMode.DROPDOWN,
          )
      ),
      vol.Required(CONFIG_TARGET_MPAN): selector.SelectSelector(
          selector.SelectSelectorConfig(
              options=meters,
              mode=selector.SelectSelectorMode.DROPDOWN,
          )
      ),
      vol.Optional(CONFIG_TARGET_START_TIME): str,
      vol.Optional(CONFIG_TARGET_END_TIME): str,
      vol.Optional(CONFIG_TARGET_OFFSET): str,
      vol.Required(CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE, default=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST): selector.SelectSelector(
          selector.SelectSelectorConfig(
              options=[
                selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST, label="All existing target rates are in the past"),
                selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST, label="Existing target rates haven't started or finished"),
              ],
              mode=selector.SelectSelectorMode.DROPDOWN,
          )
      ),
      vol.Optional(CONFIG_TARGET_ROLLING_TARGET, default=False): bool,
      vol.Optional(CONFIG_TARGET_LAST_RATES, default=False): bool,
      vol.Optional(CONFIG_TARGET_INVERT_TARGET_RATES, default=False): bool,
      vol.Optional(CONFIG_TARGET_MIN_RATE): str,
      vol.Optional(CONFIG_TARGET_MAX_RATE): str,
      vol.Optional(CONFIG_TARGET_WEIGHTING): str,
      vol.Required(CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING, default=1): cv.positive_float,
    })
  
  async def __async_setup_rolling_target_rate_schema__(self, account_id: str):
    account_info: AccountCoordinatorResult | None = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT] if account_id is not None and account_id in self.hass.data[DOMAIN] else None
    if (account_info is None):
      return self.async_abort(reason="account_not_found")

    now = utcnow()
    meters = get_electricity_meters(account_info.account, now)
    
    return vol.Schema({
      vol.Required(CONFIG_TARGET_NAME): str,
      vol.Required(CONFIG_TARGET_HOURS): str,
      vol.Required(CONFIG_TARGET_HOURS_MODE, default=CONFIG_TARGET_HOURS_MODE_EXACT): selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[
              selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_EXACT, label="Exact"),
              selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MINIMUM, label="Minimum"),
              selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MAXIMUM, label="Maximum"),
            ],
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
      ),
      vol.Required(CONFIG_TARGET_TYPE, default=CONFIG_TARGET_TYPE_CONTINUOUS): selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[
              selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_CONTINUOUS, label="Continuous"),
              selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_INTERMITTENT, label="Intermittent"),
            ],
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
      ),
      vol.Required(CONFIG_TARGET_MPAN): selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=meters,
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
      ),
      vol.Required(CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD): str,
      vol.Optional(CONFIG_TARGET_OFFSET): str,
      vol.Required(CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE, default=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST): selector.SelectSelector(
          selector.SelectSelectorConfig(
              options=[
                selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST, label="All existing target rates are in the past"),
                selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST, label="Existing target rates haven't started or finished"),
                selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS, label="Always"),
              ],
              mode=selector.SelectSelectorMode.DROPDOWN,
          )
      ),
      vol.Optional(CONFIG_TARGET_LAST_RATES): bool,
      vol.Optional(CONFIG_TARGET_INVERT_TARGET_RATES): bool,
      vol.Optional(CONFIG_TARGET_MIN_RATE): str,
      vol.Optional(CONFIG_TARGET_MAX_RATE): str,
      vol.Optional(CONFIG_TARGET_WEIGHTING): str,
      vol.Required(CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING, default=1): cv.positive_float,
    })
  
  async def __async_setup_cost_tracker_schema__(self, account_id: str):

    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT] if account_id is not None and account_id in self.hass.data[DOMAIN] else None
    if (account_info is None):
      return self.async_abort(reason="account_not_found")

    now = utcnow()
    meters = get_electricity_meters(account_info.account, now)

    return vol.Schema({
      vol.Required(CONFIG_COST_TRACKER_NAME): str,
      vol.Required(CONFIG_COST_TRACKER_MPAN): selector.SelectSelector(
          selector.SelectSelectorConfig(
              options=meters,
              mode=selector.SelectSelectorMode.DROPDOWN,
          )
      ),
      vol.Required(CONFIG_COST_TRACKER_TARGET_ENTITY_ID): selector.EntitySelector(
          selector.EntitySelectorConfig(domain="sensor", device_class=[SensorDeviceClass.ENERGY]),
      ),
      vol.Optional(CONFIG_COST_TRACKER_ENTITY_ACCUMULATIVE_VALUE, default=False): bool,
      vol.Required(CONFIG_COST_TRACKER_MANUAL_RESET, default=False): bool,
      vol.Required(CONFIG_COST_TRACKER_WEEKDAY_RESET, default="0"): selector.SelectSelector(
          selector.SelectSelectorConfig(
              options=get_weekday_options(),
              mode=selector.SelectSelectorMode.DROPDOWN,
          )
      ),
      vol.Required(CONFIG_COST_TRACKER_MONTH_DAY_RESET, default=1): cv.positive_int,
    })
  
  async def __async_setup_tariff_comparison_schema__(self, account_id: str):

    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT] if account_id is not None and account_id in self.hass.data[DOMAIN] else None
    if (account_info is None):
      return self.async_abort(reason="account_not_found")

    now = utcnow()
    meters = get_all_meters(account_info.account, now)

    return vol.Schema({
      vol.Required(CONFIG_TARIFF_COMPARISON_NAME): str,
      vol.Required(CONFIG_TARIFF_COMPARISON_MPAN_MPRN): selector.SelectSelector(
          selector.SelectSelectorConfig(
              options=meters,
              mode=selector.SelectSelectorMode.DROPDOWN,
          )
      ),
      vol.Required(CONFIG_TARIFF_COMPARISON_PRODUCT_CODE): str,
      vol.Required(CONFIG_TARIFF_COMPARISON_TARIFF_CODE): str,
    })
  
  async def async_step_target_rate_account(self, user_input):
    if user_input is None or CONFIG_ACCOUNT_ID not in user_input:
      return self.__capture_account_id__("target_rate_account")
    
    self._account_id = user_input[CONFIG_ACCOUNT_ID]
    
    return await self.async_step_target_rate(None)

  async def async_step_target_rate(self, user_input):
    """Setup a target based on the provided user input"""
    account_id = self._account_id

    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if (account_info is None):
      return self.async_abort(reason="account_not_found")

    now = utcnow()
    config = dict(user_input) if user_input is not None else None
    errors = validate_target_rate_config(config, account_info.account, now) if config is not None else {}

    if len(errors) < 1 and user_input is not None:
      config[CONFIG_KIND] = CONFIG_KIND_TARGET_RATE
      config[CONFIG_ACCOUNT_ID] = self._account_id
      # Setup our targets sensor
      return self.async_create_entry(
        title=f"{config[CONFIG_TARGET_NAME]} (target)", 
        data=config
      )

    # Reshow our form with raised logins
    data_schema = await self.__async_setup_target_rate_schema__(self._account_id)
    return self.async_show_form(
      step_id="target_rate",
      data_schema=self.add_suggested_values_to_schema(
        data_schema,
        user_input if user_input is not None else {}
      ),
      errors=errors
    )
  
  async def async_step_rolling_target_rate_account(self, user_input):
    if user_input is None or CONFIG_ACCOUNT_ID not in user_input:
      return self.__capture_account_id__("rolling_target_rate_account")
    
    self._account_id = user_input[CONFIG_ACCOUNT_ID]
    
    return await self.async_step_rolling_target_rate(None)
  
  async def async_step_rolling_target_rate(self, user_input):
    """Setup a target based on the provided user input"""
    account_id = self._account_id

    account_info: AccountCoordinatorResult | None = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if (account_info is None):
      return self.async_abort(reason="account_not_found")

    config = dict(user_input) if user_input is not None else None
    errors = validate_rolling_target_rate_config(config) if config is not None else {}

    if len(errors) < 1 and user_input is not None:
      config[CONFIG_KIND] = CONFIG_KIND_ROLLING_TARGET_RATE
      config[CONFIG_ACCOUNT_ID] = self._account_id
      # Setup our targets sensor
      return self.async_create_entry(
        title=f"{config[CONFIG_TARGET_NAME]} (rolling target)", 
        data=config
      )

    # Reshow our form with raised logins
    data_schema = await self.__async_setup_rolling_target_rate_schema__(self._account_id)
    return self.async_show_form(
      step_id="rolling_target_rate",
      data_schema=self.add_suggested_values_to_schema(
        data_schema,
        user_input if user_input is not None else {}
      ),
      errors=errors
    )
  
  async def async_step_cost_tracker_account(self, user_input):
    if user_input is None or CONFIG_ACCOUNT_ID not in user_input:
      return self.__capture_account_id__("cost_tracker_account")
    
    self._account_id = user_input[CONFIG_ACCOUNT_ID]
    
    return await self.async_step_cost_tracker(None)

  async def async_step_cost_tracker(self, user_input):
    """Setup a target based on the provided user input"""
    account_id = self._account_id

    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if (account_info is None):
      return self.async_abort(reason="account_not_found")

    now = utcnow()
    errors = validate_cost_tracker_config(user_input, account_info.account, now) if user_input is not None else {}

    if len(errors) < 1 and user_input is not None:
      user_input[CONFIG_KIND] = CONFIG_KIND_COST_TRACKER
      user_input[CONFIG_ACCOUNT_ID] = account_id
      return self.async_create_entry(
        title=f"{user_input[CONFIG_COST_TRACKER_NAME]} (cost tracker)", 
        data=user_input
      )

    # Reshow our form with raised logins
    data_schema = await self.__async_setup_cost_tracker_schema__(self._account_id)
    return self.async_show_form(
      step_id="cost_tracker",
      data_schema=self.add_suggested_values_to_schema(
        data_schema,
        user_input if user_input is not None else {}
      ),
      errors=errors
    )

  async def async_step_tariff_comparison_account(self, user_input):
    if user_input is None or CONFIG_ACCOUNT_ID not in user_input:
      return self.__capture_account_id__("tariff_comparison_account")
    
    self._account_id = user_input[CONFIG_ACCOUNT_ID]
    
    return await self.async_step_tariff_comparison(None)
  
  async def async_step_tariff_comparison(self, user_input):
    """Setup a target based on the provided user input"""
    account_id = self._account_id

    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if (account_info is None):
      return self.async_abort(reason="account_not_found")

    now = utcnow()
    errors = await async_validate_tariff_comparison_config(user_input, account_info.account, now, self.hass.data[DOMAIN][account_id][DATA_CLIENT]) if user_input is not None else {}

    if len(errors) < 1 and user_input is not None:
      user_input[CONFIG_KIND] = CONFIG_KIND_TARIFF_COMPARISON
      user_input[CONFIG_ACCOUNT_ID] = account_id
      return self.async_create_entry(
        title=f"{user_input[CONFIG_TARIFF_COMPARISON_NAME]} (tariff comparison)", 
        data=user_input
      )

    # Reshow our form with raised logins
    data_schema = await self.__async_setup_tariff_comparison_schema__(self._account_id)
    return self.async_show_form(
      step_id="tariff_comparison",
      data_schema=self.add_suggested_values_to_schema(
        data_schema,
        user_input if user_input is not None else {}
      ),
      errors=errors
    )
  
  async def async_step_choice(self, user_input):
    """Setup choice menu"""
    return self.async_show_menu(
      step_id="choice", menu_options={
        "account": "New Account",
        "target_rate_account": "Target Rate",
        "rolling_target_rate_account": "Rolling Target Rate",
        "cost_tracker_account": "Cost Tracker",
        "tariff_comparison_account": "Tariff Comparison"
      }
    )

  async def async_step_user(self, user_input):
    """Setup based on user config"""

    is_account_setup = False
    for entry in self._async_current_entries(include_ignore=False):
      if CONFIG_MAIN_API_KEY in entry.data:
        is_account_setup = True
        break

    if user_input is not None:
      if CONFIG_KIND in user_input:
        if user_input[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
          return await self.async_step_account(user_input)
        
        if user_input[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE:
          return await self.async_step_target_rate(user_input)
        
        if user_input[CONFIG_KIND] == CONFIG_KIND_ROLLING_TARGET_RATE:
          return await self.async_step_rolling_target_rate(user_input)
        
        if user_input[CONFIG_KIND] == CONFIG_KIND_COST_TRACKER:
          return await self.async_step_cost_tracker(user_input)
        
        if user_input[CONFIG_KIND] == CONFIG_KIND_TARIFF_COMPARISON:
          return await self.async_step_tariff_comparison(user_input)
        
      return self.async_abort(reason="unexpected_entry")

    if is_account_setup:
      return await self.async_step_choice(user_input)

    return self.async_show_form(
      step_id="account",
      data_schema=DATA_SCHEMA_ACCOUNT
    )

  @staticmethod
  @callback
  def async_get_options_flow(entry):
    return OptionsFlowHandler(entry)

class OptionsFlowHandler(OptionsFlow):
  """Handles options flow for the component."""

  def __init__(self, entry) -> None:
    self._entry = entry

  async def __async_setup_target_rate_schema__(self, config, errors):
    account_id = config[CONFIG_ACCOUNT_ID] if CONFIG_ACCOUNT_ID in config else None

    account_info: AccountCoordinatorResult | None = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT] if account_id is not None and account_id in self.hass.data[DOMAIN] else None
    if account_info is None:
      errors[CONFIG_TARGET_MPAN] = "account_not_found"

    now = utcnow()
    meters = get_electricity_meters(account_info.account, now)

    if (CONFIG_TARGET_MPAN not in config):
      config[CONFIG_TARGET_MPAN] = meters[0]

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
            vol.Required(CONFIG_TARGET_HOURS_MODE, default=CONFIG_TARGET_HOURS_MODE_EXACT): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                      selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_EXACT, label="Exact"),
                      selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MINIMUM, label="Minimum"),
                      selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MAXIMUM, label="Maximum"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(CONFIG_TARGET_TYPE, default=CONFIG_TARGET_TYPE_CONTINUOUS): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                      selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_CONTINUOUS, label="Continuous"),
                      selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_INTERMITTENT, label="Intermittent"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(CONFIG_TARGET_MPAN): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=meters,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(CONFIG_TARGET_START_TIME): str,
            vol.Optional(CONFIG_TARGET_END_TIME): str,
            vol.Optional(CONFIG_TARGET_OFFSET): str,
            vol.Required(CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE): selector.SelectSelector(
              selector.SelectSelectorConfig(
                  options=[
                    selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST, label="All existing target rates are in the past"),
                    selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST, label="Existing target rates haven't started or finished"),
                  ],
                  mode=selector.SelectSelectorMode.DROPDOWN,
              )
            ),
            vol.Optional(CONFIG_TARGET_ROLLING_TARGET): bool,
            vol.Optional(CONFIG_TARGET_LAST_RATES): bool,
            vol.Optional(CONFIG_TARGET_INVERT_TARGET_RATES): bool,
            vol.Optional(CONFIG_TARGET_MIN_RATE): str,
            vol.Optional(CONFIG_TARGET_MAX_RATE): str,
            vol.Optional(CONFIG_TARGET_WEIGHTING): str,
            vol.Required(CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING): cv.positive_float,
          }),
          {
            CONFIG_TARGET_NAME: config[CONFIG_TARGET_NAME],
            CONFIG_TARGET_HOURS: f'{config[CONFIG_TARGET_HOURS]}',
            CONFIG_TARGET_HOURS_MODE: config[CONFIG_TARGET_HOURS_MODE],
            CONFIG_TARGET_TYPE: config[CONFIG_TARGET_TYPE],
            CONFIG_TARGET_MPAN: config[CONFIG_TARGET_MPAN],
            CONFIG_TARGET_START_TIME: config[CONFIG_TARGET_START_TIME] if CONFIG_TARGET_START_TIME in config else None,
            CONFIG_TARGET_END_TIME: config[CONFIG_TARGET_END_TIME] if CONFIG_TARGET_END_TIME in config else None,
            CONFIG_TARGET_OFFSET: config[CONFIG_TARGET_OFFSET] if CONFIG_TARGET_OFFSET in config else None,
            CONFIG_TARGET_ROLLING_TARGET: is_rolling_target,
            CONFIG_TARGET_LAST_RATES: find_last_rates,
            CONFIG_TARGET_INVERT_TARGET_RATES: invert_target_rates,
            CONFIG_TARGET_MIN_RATE: f'{config[CONFIG_TARGET_MIN_RATE]}' if CONFIG_TARGET_MIN_RATE in config and config[CONFIG_TARGET_MIN_RATE] is not None else None,
            CONFIG_TARGET_MAX_RATE: f'{config[CONFIG_TARGET_MAX_RATE]}' if CONFIG_TARGET_MAX_RATE in config and config[CONFIG_TARGET_MAX_RATE] is not None else None,
            CONFIG_TARGET_WEIGHTING: config[CONFIG_TARGET_WEIGHTING] if CONFIG_TARGET_WEIGHTING in config else None,
            CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING: config[CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING] if CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING in config else 1,
            CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE: config[CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE] if CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE in config else CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST,
          }
      ),
      errors=errors
    )
  
  async def __async_setup_rolling_target_rate_schema__(self, config, errors):
    account_id = config[CONFIG_ACCOUNT_ID] if CONFIG_ACCOUNT_ID in config else None

    account_info: AccountCoordinatorResult | None = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT] if account_id is not None and account_id in self.hass.data[DOMAIN] else None
    if account_info is None:
      errors[CONFIG_TARGET_MPAN] = "account_not_found"

    now = utcnow()
    meters = get_electricity_meters(account_info.account, now)

    if (CONFIG_TARGET_MPAN not in config):
      config[CONFIG_TARGET_MPAN] = meters[0]

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
      step_id="rolling_target_rate",
      data_schema=self.add_suggested_values_to_schema(
          vol.Schema({
            vol.Required(CONFIG_TARGET_NAME): str,
            vol.Required(CONFIG_TARGET_HOURS): str,
            vol.Required(CONFIG_TARGET_HOURS_MODE, default=CONFIG_TARGET_HOURS_MODE_EXACT): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                      selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_EXACT, label="Exact"),
                      selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MINIMUM, label="Minimum"),
                      selector.SelectOptionDict(value=CONFIG_TARGET_HOURS_MODE_MAXIMUM, label="Maximum"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(CONFIG_TARGET_TYPE, default=CONFIG_TARGET_TYPE_CONTINUOUS): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                      selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_CONTINUOUS, label="Continuous"),
                      selector.SelectOptionDict(value=CONFIG_TARGET_TYPE_INTERMITTENT, label="Intermittent"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(CONFIG_TARGET_MPAN): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=meters,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD): str,
            vol.Optional(CONFIG_TARGET_OFFSET): str,
            vol.Required(CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE, default=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                      selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST, label="All existing target rates are in the past"),
                      selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST, label="Existing target rates haven't started or finished"),
                      selector.SelectOptionDict(value=CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS, label="Always"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(CONFIG_TARGET_LAST_RATES): bool,
            vol.Optional(CONFIG_TARGET_INVERT_TARGET_RATES): bool,
            vol.Optional(CONFIG_TARGET_MIN_RATE): str,
            vol.Optional(CONFIG_TARGET_MAX_RATE): str,
            vol.Optional(CONFIG_TARGET_WEIGHTING): str,
            vol.Required(CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING): cv.positive_float,
          }),
          {
            CONFIG_TARGET_NAME: config[CONFIG_TARGET_NAME],
            CONFIG_TARGET_HOURS: f'{config[CONFIG_TARGET_HOURS]}',
            CONFIG_TARGET_HOURS_MODE: config[CONFIG_TARGET_HOURS_MODE],
            CONFIG_TARGET_TYPE: config[CONFIG_TARGET_TYPE],
            CONFIG_TARGET_MPAN: config[CONFIG_TARGET_MPAN],
            CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD: f'{config[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD]}',
            CONFIG_TARGET_OFFSET: config[CONFIG_TARGET_OFFSET] if CONFIG_TARGET_OFFSET in config else None,
            CONFIG_TARGET_ROLLING_TARGET: is_rolling_target,
            CONFIG_TARGET_LAST_RATES: find_last_rates,
            CONFIG_TARGET_INVERT_TARGET_RATES: invert_target_rates,
            CONFIG_TARGET_MIN_RATE: f'{config[CONFIG_TARGET_MIN_RATE]}' if CONFIG_TARGET_MIN_RATE in config and config[CONFIG_TARGET_MIN_RATE] is not None else None,
            CONFIG_TARGET_MAX_RATE: f'{config[CONFIG_TARGET_MAX_RATE]}' if CONFIG_TARGET_MAX_RATE in config and config[CONFIG_TARGET_MAX_RATE] is not None else None,
            CONFIG_TARGET_WEIGHTING: config[CONFIG_TARGET_WEIGHTING] if CONFIG_TARGET_WEIGHTING in config else None,            
            CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE: config[CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE] if CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE in config else CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST,
            CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING: config[CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING] if CONFIG_TARGET_FREE_ELECTRICITY_WEIGHTING in config else 1
          }
      ),
      errors=errors
    )
  
  async def __async_setup_main_schema__(self, config, errors):
    supports_live_consumption = False
    if CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in config:
      supports_live_consumption = config[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION]

    live_electricity_consumption_refresh_in_minutes = CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES
    if CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES in config:
      live_electricity_consumption_refresh_in_minutes = config[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES]

    live_gas_consumption_refresh_in_minutes = CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES
    if CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES in config:
      live_gas_consumption_refresh_in_minutes = config[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES]
    
    calorific_value = DEFAULT_CALORIFIC_VALUE
    if CONFIG_MAIN_CALORIFIC_VALUE in config:
      calorific_value = config[CONFIG_MAIN_CALORIFIC_VALUE]
    
    return self.async_show_form(
      step_id="user",
      data_schema=self.add_suggested_values_to_schema(
        vol.Schema({
          vol.Required(CONFIG_MAIN_API_KEY): str,
          vol.Required(CONFIG_MAIN_CALORIFIC_VALUE): cv.positive_float,
          vol.Required(CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION): bool,
          vol.Optional(CONFIG_MAIN_HOME_PRO_ADDRESS): str,
          vol.Optional(CONFIG_MAIN_HOME_PRO_API_KEY): str,
          vol.Required(CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES): cv.positive_int,
          vol.Required(CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES): cv.positive_int,
          vol.Optional(CONFIG_MAIN_ELECTRICITY_PRICE_CAP): cv.positive_float,
          vol.Optional(CONFIG_MAIN_GAS_PRICE_CAP): cv.positive_float,
          vol.Required(CONFIG_FAVOUR_DIRECT_DEBIT_RATES): bool,
        }),
        {
          CONFIG_MAIN_API_KEY: config[CONFIG_MAIN_API_KEY],
          CONFIG_MAIN_CALORIFIC_VALUE: calorific_value,
          CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: supports_live_consumption,
          CONFIG_MAIN_HOME_PRO_ADDRESS: config[CONFIG_MAIN_HOME_PRO_ADDRESS] if CONFIG_MAIN_HOME_PRO_ADDRESS in config else None,
          CONFIG_MAIN_HOME_PRO_API_KEY: config[CONFIG_MAIN_HOME_PRO_API_KEY] if CONFIG_MAIN_HOME_PRO_API_KEY in config else None,
          CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: live_electricity_consumption_refresh_in_minutes,
          CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: live_gas_consumption_refresh_in_minutes,
          CONFIG_MAIN_ELECTRICITY_PRICE_CAP: config[CONFIG_MAIN_ELECTRICITY_PRICE_CAP] if CONFIG_MAIN_ELECTRICITY_PRICE_CAP in config else None,
          CONFIG_MAIN_GAS_PRICE_CAP: config[CONFIG_MAIN_GAS_PRICE_CAP] if CONFIG_MAIN_GAS_PRICE_CAP in config else None,
          CONFIG_FAVOUR_DIRECT_DEBIT_RATES: config[CONFIG_FAVOUR_DIRECT_DEBIT_RATES] if CONFIG_FAVOUR_DIRECT_DEBIT_RATES in config else True
        }
      ),
      errors=errors
    )
  
  async def __async_setup_cost_tracker_schema__(self, config, errors):
    account_id = config[CONFIG_ACCOUNT_ID]

    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if account_info is None:
      errors[CONFIG_TARGET_MPAN] = "account_not_found"

    now = utcnow()
    meters = get_electricity_meters(account_info.account, now)

    return self.async_show_form(
      step_id="cost_tracker",
      data_schema=self.add_suggested_values_to_schema(
        vol.Schema({
          vol.Required(CONFIG_COST_TRACKER_NAME): str,
          vol.Required(CONFIG_COST_TRACKER_MPAN): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=meters,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
          vol.Required(CONFIG_COST_TRACKER_TARGET_ENTITY_ID): selector.EntitySelector(
              selector.EntitySelectorConfig(domain="sensor", device_class=[SensorDeviceClass.ENERGY]),
          ),
          vol.Optional(CONFIG_COST_TRACKER_ENTITY_ACCUMULATIVE_VALUE): bool,
          vol.Required(CONFIG_COST_TRACKER_MANUAL_RESET): bool,
          vol.Required(CONFIG_COST_TRACKER_WEEKDAY_RESET): selector.SelectSelector(
              selector.SelectSelectorConfig(
                  options=get_weekday_options(),
                  mode=selector.SelectSelectorMode.DROPDOWN,
              )
          ),
          vol.Required(CONFIG_COST_TRACKER_MONTH_DAY_RESET): cv.positive_int,
        }),
        {
          CONFIG_COST_TRACKER_NAME: config[CONFIG_COST_TRACKER_NAME],
          CONFIG_COST_TRACKER_MPAN: config[CONFIG_COST_TRACKER_MPAN],
          CONFIG_COST_TRACKER_TARGET_ENTITY_ID: config[CONFIG_COST_TRACKER_TARGET_ENTITY_ID],
          CONFIG_COST_TRACKER_ENTITY_ACCUMULATIVE_VALUE: config[CONFIG_COST_TRACKER_ENTITY_ACCUMULATIVE_VALUE],
          CONFIG_COST_TRACKER_WEEKDAY_RESET: f"{config[CONFIG_COST_TRACKER_WEEKDAY_RESET]}" if CONFIG_COST_TRACKER_WEEKDAY_RESET in config else "0",
          CONFIG_COST_TRACKER_MONTH_DAY_RESET: config[CONFIG_COST_TRACKER_MONTH_DAY_RESET] if CONFIG_COST_TRACKER_MONTH_DAY_RESET in config else 1,
          CONFIG_COST_TRACKER_MANUAL_RESET: config[CONFIG_COST_TRACKER_MANUAL_RESET] if CONFIG_COST_TRACKER_MANUAL_RESET in config else False
        }
      ),
      errors=errors
    )
  
  async def __async_setup_tariff_comparison_schema__(self, config, errors):
    account_id = config[CONFIG_ACCOUNT_ID]

    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if account_info is None:
      errors[CONFIG_TARGET_MPAN] = "account_not_found"

    now = utcnow()
    meters = get_all_meters(account_info.account, now)

    return self.async_show_form(
      step_id="tariff_comparison",
      data_schema=self.add_suggested_values_to_schema(
        vol.Schema({
          vol.Required(CONFIG_TARIFF_COMPARISON_NAME): str,
          vol.Required(CONFIG_TARIFF_COMPARISON_MPAN_MPRN): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=meters,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
          vol.Required(CONFIG_TARIFF_COMPARISON_PRODUCT_CODE): str,
          vol.Required(CONFIG_TARIFF_COMPARISON_TARIFF_CODE): str,
        }),
        {
          CONFIG_TARIFF_COMPARISON_NAME: config[CONFIG_TARIFF_COMPARISON_NAME],
          CONFIG_TARIFF_COMPARISON_MPAN_MPRN: config[CONFIG_TARIFF_COMPARISON_MPAN_MPRN],
          CONFIG_TARIFF_COMPARISON_PRODUCT_CODE: config[CONFIG_TARIFF_COMPARISON_PRODUCT_CODE],
          CONFIG_TARIFF_COMPARISON_TARIFF_CODE: config[CONFIG_TARIFF_COMPARISON_TARIFF_CODE],
        }
      ),
      errors=errors
    )

  async def async_step_init(self, user_input):
    """Manage the options for the custom component."""
    kind = self._entry.data[CONFIG_KIND]
    if (kind == CONFIG_KIND_ACCOUNT):
      config = merge_main_config(self._entry.data, self._entry.options, user_input)
      return await self.__async_setup_main_schema__(config, {})

    if (kind == CONFIG_KIND_TARGET_RATE):
      config = merge_target_rate_config(self._entry.data, self._entry.options, user_input)
      return await self.__async_setup_target_rate_schema__(config, {})
    
    if (kind == CONFIG_KIND_ROLLING_TARGET_RATE):
      config = merge_rolling_target_rate_config(self._entry.data, self._entry.options, user_input)
      return await self.__async_setup_rolling_target_rate_schema__(config, {})

    if (kind == CONFIG_KIND_COST_TRACKER):
      config = merge_cost_tracker_config(self._entry.data, self._entry.options, user_input)
      return await self.__async_setup_cost_tracker_schema__(config, {})
    
    if (kind == CONFIG_KIND_TARIFF_COMPARISON):
      config = merge_tariff_comparison_config(self._entry.data, self._entry.options, user_input)
      return await self.__async_setup_tariff_comparison_schema__(config, {})

    return self.async_abort(reason="not_supported")

  async def async_step_user(self, user_input):
    """Manage the options for the custom component."""

    config = merge_main_config(self._entry.data, self._entry.options, user_input)

    errors = await async_validate_main_config(config)
    
    if (len(errors) > 0):
      return await self.__async_setup_main_schema__(config, errors)

    return self.async_create_entry(title="", data=config)

  async def async_step_target_rate(self, user_input):
    """Manage the options for the custom component."""
    config = merge_target_rate_config(self._entry.data, self._entry.options, user_input)
    account_id = config[CONFIG_ACCOUNT_ID] if CONFIG_ACCOUNT_ID in config else None

    account_info: AccountCoordinatorResult | None = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT] if account_id is not None and account_id in self.hass.data[DOMAIN] else None
    if account_info is None:
      errors[CONFIG_TARGET_MPAN] = "account_not_found"

    now = utcnow()
    errors = validate_target_rate_config(config, account_info.account, now)

    if (len(errors) > 0):
      return await self.__async_setup_target_rate_schema__(config, errors)

    return self.async_create_entry(title="", data=config)
  
  async def async_step_rolling_target_rate(self, user_input):
    """Manage the options for the custom component."""
    config = merge_rolling_target_rate_config(self._entry.data, self._entry.options, user_input)
    account_id = config[CONFIG_ACCOUNT_ID] if CONFIG_ACCOUNT_ID in config else None

    account_info: AccountCoordinatorResult | None = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT] if account_id is not None and account_id in self.hass.data[DOMAIN] else None
    if account_info is None:
      errors[CONFIG_TARGET_MPAN] = "account_not_found"

    errors = validate_rolling_target_rate_config(config)

    if (len(errors) > 0):
      return await self.__async_setup_rolling_target_rate_schema__(config, errors)

    return self.async_create_entry(title="", data=config)
  
  async def async_step_cost_tracker(self, user_input):
    """Manage the options for the custom component."""
    config = merge_cost_tracker_config(self._entry.data, self._entry.options, user_input)
    account_id = config[CONFIG_ACCOUNT_ID] if CONFIG_ACCOUNT_ID in config else None

    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if (account_info is None):
      return self.async_abort(reason="account_not_found")

    now = utcnow()
    errors = validate_cost_tracker_config(config, account_info.account, now)

    if (len(errors) > 0):
      return await self.__async_setup_cost_tracker_schema__(config, errors)

    return self.async_create_entry(title="", data=config)
  
  async def async_step_tariff_comparison(self, user_input):
    """Manage the options for the custom component."""
    config = merge_tariff_comparison_config(self._entry.data, self._entry.options, user_input)
    account_id = config[CONFIG_ACCOUNT_ID] if CONFIG_ACCOUNT_ID in config else None

    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if (account_info is None):
      return self.async_abort(reason="account_not_found")

    now = utcnow()
    errors = await async_validate_tariff_comparison_config(config, account_info.account, now, self.hass.data[DOMAIN][account_id][DATA_CLIENT])

    if (len(errors) > 0):
      return await self.__async_setup_tariff_comparison_schema__(config, errors)

    return self.async_create_entry(title="", data=config)