import voluptuous as vol
import logging

from homeassistant.util.dt import (utcnow)
from homeassistant.config_entries import (ConfigFlow)
import homeassistant.helpers.config_validation as cv
from homeassistant.data_entry_flow import section
from homeassistant.helpers import selector
from homeassistant.components.sensor import (
  SensorDeviceClass,
)
from homeassistant.helpers.typing import DiscoveryInfoType

from .coordinators.account import AccountCoordinatorResult
from .config.cost_tracker import validate_cost_tracker_config
from .config.target_rates import validate_target_rate_config
from .config.main import async_validate_main_config
from .const import (
  CONFIG_COST_TRACKER_DISCOVERY_ACCOUNT_ID,
  CONFIG_COST_TRACKER_DISCOVERY_NAME,
  CONFIG_COST_TRACKER_MANUAL_RESET,
  CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_KIND_ROLLING_TARGET_RATE,
  CONFIG_MAIN_AUTO_DISCOVER_COST_TRACKERS,
  CONFIG_MAIN_CALORIFIC_VALUE,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_FAVOUR_DIRECT_DEBIT_RATES,
  CONFIG_MAIN_GAS_PRICE_CAP,
  CONFIG_MAIN_HOME_MINI_SETTINGS,
  CONFIG_MAIN_HOME_PRO_ADDRESS,
  CONFIG_MAIN_HOME_PRO_API_KEY,
  CONFIG_MAIN_HOME_PRO_SETTINGS,
  CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES,
  CONFIG_MAIN_INTELLIGENT_RATE_MODE,
  CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES,
  CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY,
  CONFIG_MAIN_INTELLIGENT_SETTINGS,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_PRICE_CAP_SETTINGS,
  CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION,
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
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_TARIFF_COMPARISON,
  CONFIG_KIND_COST_TRACKER,
  CONFIG_KIND_TARGET_RATE,
  CONFIG_ACCOUNT_ID,
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
)
from .config.tariff_comparison import async_validate_tariff_comparison_config
from .config.rolling_target_rates import validate_rolling_target_rate_config

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
    for entry in hass.config_entries.async_entries(DOMAIN, include_ignore=False):
      if CONFIG_KIND in entry.data and entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
        account_id = entry.data[CONFIG_ACCOUNT_ID]
        account_ids.append(account_id)

    return account_ids

class OctopusEnergyConfigFlow(ConfigFlow, domain=DOMAIN): 
  """Config flow."""

  VERSION = CONFIG_VERSION

  _target_entity_id = None

  async def async_step_integration_discovery(
    self,
    discovery_info: DiscoveryInfoType,
  ):
    """Handle integration discovery."""
    _LOGGER.debug("Starting discovery flow: %s", discovery_info)

    if discovery_info[CONFIG_KIND] == CONFIG_KIND_COST_TRACKER:
      self._target_entity_id = discovery_info[CONFIG_COST_TRACKER_TARGET_ENTITY_ID]
      self._account_id = discovery_info[CONFIG_COST_TRACKER_DISCOVERY_ACCOUNT_ID]
      self.context["title_placeholders"] = {
        "name": discovery_info[CONFIG_COST_TRACKER_DISCOVERY_NAME],
      }

      unique_id = f"octopus_energy_ct_{self._account_id}_{self._target_entity_id}"
      await self.async_set_unique_id(unique_id)
      self._abort_if_unique_id_configured()
      
      return await self.async_step_cost_tracker(None)
    
    return self.async_abort(reason="unexpected_discovery")
  
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
  
  def __setup_account_schema__(self, include_account_id = True):
    schema = {
      vol.Required(CONFIG_ACCOUNT_ID): str,
      vol.Required(CONFIG_MAIN_API_KEY): str,
      vol.Required(CONFIG_MAIN_CALORIFIC_VALUE, default=DEFAULT_CALORIFIC_VALUE): cv.positive_float,
      vol.Required(CONFIG_MAIN_FAVOUR_DIRECT_DEBIT_RATES): bool,
      vol.Required(CONFIG_MAIN_AUTO_DISCOVER_COST_TRACKERS): bool,
      vol.Required(CONFIG_MAIN_HOME_MINI_SETTINGS): section(
        vol.Schema(
            {
                vol.Required(CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION): bool,
                vol.Required(CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES, default=CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES): cv.positive_int,
                vol.Required(CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES, default=CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES): cv.positive_int,
            }
        ),
        {"collapsed": True},
      ),
      vol.Required(CONFIG_MAIN_HOME_PRO_SETTINGS): section(
        vol.Schema(
            {
                vol.Optional(CONFIG_MAIN_HOME_PRO_ADDRESS): str,
                vol.Optional(CONFIG_MAIN_HOME_PRO_API_KEY): str,
            }
        ),
        {"collapsed": True},
      ),
      vol.Required(CONFIG_MAIN_PRICE_CAP_SETTINGS): section(
        vol.Schema(
            {
                vol.Optional(CONFIG_MAIN_ELECTRICITY_PRICE_CAP): cv.positive_float,
                vol.Optional(CONFIG_MAIN_GAS_PRICE_CAP): cv.positive_float,
            }
        ),
        {"collapsed": True},
      ),
      vol.Required(CONFIG_MAIN_INTELLIGENT_SETTINGS): section(
        vol.Schema(
            {
                vol.Required(CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES): bool,
                vol.Required(CONFIG_MAIN_INTELLIGENT_RATE_MODE): selector.SelectSelector(
                  selector.SelectSelectorConfig(
                      options=[
                        selector.SelectOptionDict(value=CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES, label="Planned and started dispatches will turn into off peak rates"),
                        selector.SelectOptionDict(value=CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY, label="Only started dispatches will turn into off peak rates"),
                      ],
                      mode=selector.SelectSelectorMode.DROPDOWN,
                  )
                ),
            }
        ),
        {"collapsed": True},
      ),
    }

    if (include_account_id == False):
      del schema[CONFIG_ACCOUNT_ID]

    return vol.Schema(schema)
  
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
        self.__setup_account_schema__(),
        user_input if user_input is not None else {}
      ),
      errors=errors
    )
  
  async def async_step_reconfigure_account(self, user_input):
    """Setup the initial account based on the provided user input"""
    config = dict()
    config.update(self._get_reconfigure_entry().data)

    if user_input is not None:
      config.update(user_input)

    account_ids = []
    errors = await async_validate_main_config(config, account_ids)

    if len(errors) < 1 and user_input is not None:
      return self.async_update_reload_and_abort(
        self._get_reconfigure_entry(),
        data_updates=config,
      )

    return self.async_show_form(
      step_id="reconfigure_account",
      data_schema=self.add_suggested_values_to_schema(
        self.__setup_account_schema__(False),
        config
      ),
      errors=errors
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
  
  async def async_step_reconfigure_target_rate(self, user_input):
    """Setup a target based on the provided user input"""
    config = dict()
    config.update(self._get_reconfigure_entry().data)

    account_id = config[CONFIG_ACCOUNT_ID]
    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if (account_info is None):
      return self.async_abort(reason="account_not_found")
    
    if user_input is not None:
      config.update(user_input)

    now = utcnow()
    errors = validate_target_rate_config(config, account_info.account, now)

    if len(errors) < 1 and user_input is not None:
      return self.async_update_reload_and_abort(
        self._get_reconfigure_entry(),
        data_updates=config,
      )

    # Reshow our form with raised logins
    data_schema = await self.__async_setup_target_rate_schema__(account_id)
    return self.async_show_form(
      step_id="reconfigure_target_rate",
      data_schema=self.add_suggested_values_to_schema(
        data_schema,
        config
      ),
      errors=errors
    )
  
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
  
  async def async_step_reconfigure_rolling_target_rate(self, user_input):
    """Setup a target based on the provided user input"""
    config = dict()
    config.update(self._get_reconfigure_entry().data)

    account_id = config[CONFIG_ACCOUNT_ID]
    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if (account_info is None):
      return self.async_abort(reason="account_not_found")
    
    if user_input is not None:
      config.update(user_input)

    errors = validate_rolling_target_rate_config(config)

    if len(errors) < 1 and user_input is not None:
      return self.async_update_reload_and_abort(
        self._get_reconfigure_entry(),
        data_updates=config,
      )

    # Reshow our form with raised logins
    data_schema = await self.__async_setup_rolling_target_rate_schema__(account_id)
    return self.async_show_form(
      step_id="reconfigure_rolling_target_rate",
      data_schema=self.add_suggested_values_to_schema(
        data_schema,
        config
      ),
      errors=errors
    )
  
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
      vol.Required(CONFIG_COST_TRACKER_WEEKDAY_RESET): selector.SelectSelector(
          selector.SelectSelectorConfig(
              options=get_weekday_options(),
              mode=selector.SelectSelectorMode.DROPDOWN,
          )
      ),
      vol.Required(CONFIG_COST_TRACKER_MONTH_DAY_RESET, default=1): cv.positive_int,
    })

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

    if user_input is None and self._target_entity_id is not None:
      user_input = {
        CONFIG_COST_TRACKER_TARGET_ENTITY_ID: self._target_entity_id
      }

    # Reshow our form with raised logins
    data_schema = await self.__async_setup_cost_tracker_schema__(self._account_id)
    return self.async_show_form(
      step_id="cost_tracker",
      data_schema=self.add_suggested_values_to_schema(
        data_schema,
        {
          **(user_input if user_input is not None else {}),
          CONFIG_COST_TRACKER_WEEKDAY_RESET: f"{user_input[CONFIG_COST_TRACKER_WEEKDAY_RESET]}" if user_input is not None and CONFIG_COST_TRACKER_WEEKDAY_RESET in user_input else "0",
        }
      ),
      errors=errors
    )
  
  async def async_step_reconfigure_cost_tracker(self, user_input):
    """Setup a target based on the provided user input"""
    config = dict()
    config.update(self._get_reconfigure_entry().data)

    account_id = config[CONFIG_ACCOUNT_ID]
    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if (account_info is None):
      return self.async_abort(reason="account_not_found")
    
    if user_input is not None:
      config.update(user_input)

    now = utcnow()
    errors = validate_cost_tracker_config(config, account_info.account, now)

    if len(errors) < 1 and user_input is not None:
      return self.async_update_reload_and_abort(
        self._get_reconfigure_entry(),
        data_updates=config,
      )

    # Reshow our form with raised logins
    data_schema = await self.__async_setup_cost_tracker_schema__(account_id)
    return self.async_show_form(
      step_id="reconfigure_cost_tracker",
      data_schema=self.add_suggested_values_to_schema(
        data_schema,
        {
          **config,
          CONFIG_COST_TRACKER_WEEKDAY_RESET: f"{config[CONFIG_COST_TRACKER_WEEKDAY_RESET]}" if config is not None and CONFIG_COST_TRACKER_WEEKDAY_RESET in config else "0",
        }
      ),
      errors=errors
    )
  
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
  
  async def async_step_reconfigure_tariff_comparison(self, user_input):
    """Setup a target based on the provided user input"""
    config = dict()
    config.update(self._get_reconfigure_entry().data)

    account_id = config[CONFIG_ACCOUNT_ID]
    account_info: AccountCoordinatorResult = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    if (account_info is None):
      return self.async_abort(reason="account_not_found")
    
    if user_input is not None:
      config.update(user_input)

    now = utcnow()
    client = self.hass.data[DOMAIN][account_id][DATA_CLIENT]
    errors = await async_validate_tariff_comparison_config(config, account_info.account, now, client)

    if len(errors) < 1 and user_input is not None:
      return self.async_update_reload_and_abort(
        self._get_reconfigure_entry(),
        data_updates=config,
      )

    # Reshow our form with raised logins
    data_schema = await self.__async_setup_tariff_comparison_schema__(account_id)
    return self.async_show_form(
      step_id="reconfigure_tariff_comparison",
      data_schema=self.add_suggested_values_to_schema(
        data_schema,
        config
      ),
      errors=errors
    )
  
  async def async_step_choice(self, user_input):
    """Setup choice menu"""
    return self.async_show_menu(
      step_id="choice", menu_options={
        "account": "Additional Account",
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
      data_schema=self.__setup_account_schema__(),
    )
  
  async def async_step_reconfigure(self, user_input):
    """Manage the options for the custom component."""
    kind = self._get_reconfigure_entry().data[CONFIG_KIND]

    if (kind == CONFIG_KIND_ACCOUNT):
      return await self.async_step_reconfigure_account(user_input)

    if (kind == CONFIG_KIND_TARGET_RATE):
      return await self.async_step_reconfigure_target_rate(user_input)
    
    if (kind == CONFIG_KIND_ROLLING_TARGET_RATE):
      return await self.async_step_reconfigure_rolling_target_rate(user_input)

    if (kind == CONFIG_KIND_COST_TRACKER):
      return await self.async_step_reconfigure_cost_tracker(user_input)
    
    if (kind == CONFIG_KIND_TARIFF_COMPARISON):
      return await self.async_step_reconfigure_tariff_comparison(user_input)

    return self.async_abort(reason="reconfigure_not_supported")