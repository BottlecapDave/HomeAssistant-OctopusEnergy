import voluptuous as vol
import homeassistant.helpers.config_validation as cv

DOMAIN = "octopus_energy"

CONFIG_KIND = "kind"
CONFIG_MAIN_API_KEY = "Api key"
CONFIG_MAIN_ACCOUNT_ID = "Account Id"
CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION = "supports_live_consumption"
CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES = "live_electricity_consumption_refresh_in_minutes"
CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES = "live_gas_consumption_refresh_in_minutes"
CONFIG_MAIN_CALORIFIC_VALUE = "calorific_value"
CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET = "previous_electricity_consumption_days_offset"
CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET = "previous_gas_consumption_days_offset"
CONFIG_MAIN_ELECTRICITY_PRICE_CAP = "electricity_price_cap"
CONFIG_MAIN_CLEAR_ELECTRICITY_PRICE_CAP = "clear_electricity_price_cap"
CONFIG_MAIN_GAS_PRICE_CAP = "gas_price_cap"
CONFIG_MAIN_CLEAR_GAS_PRICE_CAP = "clear_gas_price_cap"

CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES = 1
CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES = 2
CONFIG_DEFAULT_PREVIOUS_CONSUMPTION_OFFSET_IN_DAYS = 1

CONFIG_TARGET_NAME = "Name"
CONFIG_TARGET_HOURS = "Hours"
CONFIG_TARGET_TYPE = "Type"
CONFIG_TARGET_START_TIME = "Start time"
CONFIG_TARGET_END_TIME = "End time"
CONFIG_TARGET_MPAN = "MPAN"
CONFIG_TARGET_OFFSET = "offset"
CONFIG_TARGET_ROLLING_TARGET = "rolling_target"
CONFIG_TARGET_LAST_RATES = "last_rates"
CONFIG_TARGET_INVERT_TARGET_RATES = "target_invert_target_rates"

DATA_CONFIG = "CONFIG"
DATA_ELECTRICITY_RATES_COORDINATOR_KEY = "ELECTRICITY_RATES_COORDINATOR_{}_{}"
DATA_ELECTRICITY_RATES_KEY = "ELECTRICITY_RATES_{}_{}"
DATA_CLIENT = "CLIENT"
DATA_GAS_TARIFF_CODE = "GAS_TARIFF_CODE"
DATA_ACCOUNT_ID = "ACCOUNT_ID"
DATA_ACCOUNT = "ACCOUNT"
DATA_ACCOUNT_COORDINATOR = "ACCOUNT_COORDINATOR"
DATA_SAVING_SESSIONS = "SAVING_SESSIONS"
DATA_SAVING_SESSIONS_COORDINATOR = "SAVING_SESSIONS_COORDINATOR"
DATA_KNOWN_TARIFF = "KNOWN_TARIFF"
DATA_GAS_RATES_COORDINATOR_KEY = "DATA_GAS_RATES_COORDINATOR_{}_{}"
DATA_GAS_RATES_KEY = "GAS_RATES_{}_{}"
DATA_INTELLIGENT_DISPATCHES = "INTELLIGENT_DISPATCHES"
DATA_INTELLIGENT_DISPATCHES_COORDINATOR = "INTELLIGENT_DISPATCHES_COORDINATOR"
DATA_INTELLIGENT_SETTINGS = "INTELLIGENT_SETTINGS"
DATA_INTELLIGENT_SETTINGS_COORDINATOR = "INTELLIGENT_SETTINGS_COORDINATOR"

DATA_ELECTRICITY_STANDING_CHARGE_KEY = "ELECTRICITY_STANDING_CHARGES_{}_{}"

DATA_GAS_STANDING_CHARGES_COORDINATOR = "GAS_STANDING_CHARGES_COORDINATOR"
DATA_GAS_STANDING_CHARGES = "GAS_STANDING_CHARGES"

STORAGE_COMPLETED_DISPATCHES_NAME = "octopus_energy.{}-completed-intelligent-dispatches.json"

STORAGE_COMPLETED_DISPATCHES_NAME = "octopus_energy.{}-completed-intelligent-dispatches.json"

REGEX_HOURS = "^[0-9]+(\\.[0-9]+)*$"
REGEX_TIME = "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
REGEX_ENTITY_NAME = "^[a-z0-9_]+$"
# According to https://www.guylipman.com/octopus/api_guide.html#s1b, this part should indicate the types of tariff
# However it looks like there are some tariffs that don't fit this mold
REGEX_TARIFF_PARTS = "^((?P<energy>[A-Z])-(?P<rate>[0-9A-Z]+)-)?(?P<product_code>[A-Z0-9-]+)-(?P<region>[A-Z])$"
REGEX_OFFSET_PARTS = "^(-)?([0-1]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$"
REGEX_DATE = "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"

DATA_SCHEMA_ACCOUNT = vol.Schema({
  vol.Required(CONFIG_MAIN_API_KEY): str,
  vol.Required(CONFIG_MAIN_ACCOUNT_ID): str,
  vol.Required(CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION): bool,
  vol.Required(CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES, default=CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES): cv.positive_int,
  vol.Required(CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES, default=CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES): cv.positive_int,
  vol.Required(CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET, default=CONFIG_DEFAULT_PREVIOUS_CONSUMPTION_OFFSET_IN_DAYS): cv.positive_int,
  vol.Required(CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET, default=CONFIG_DEFAULT_PREVIOUS_CONSUMPTION_OFFSET_IN_DAYS): cv.positive_int,
  vol.Required(CONFIG_MAIN_CALORIFIC_VALUE, default=40.0): cv.positive_float,
  vol.Optional(CONFIG_MAIN_ELECTRICITY_PRICE_CAP): cv.positive_float,
  vol.Optional(CONFIG_MAIN_GAS_PRICE_CAP): cv.positive_float
})

EVENT_ELECTRICITY_PREVIOUS_DAY_RATES = "octopus_energy_electricity_previous_day_rates"
EVENT_ELECTRICITY_CURRENT_DAY_RATES = "octopus_energy_electricity_current_day_rates"
EVENT_ELECTRICITY_NEXT_DAY_RATES = "octopus_energy_electricity_next_day_rates"
EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES = "octopus_energy_electricity_previous_consumption_rates"
EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_OVERRIDE_RATES = "octopus_energy_electricity_previous_consumption_override_rates"

EVENT_GAS_PREVIOUS_DAY_RATES = "octopus_energy_gas_previous_day_rates"
EVENT_GAS_CURRENT_DAY_RATES = "octopus_energy_gas_current_day_rates"
EVENT_GAS_NEXT_DAY_RATES = "octopus_energy_gas_next_day_rates"
EVENT_GAS_PREVIOUS_CONSUMPTION_RATES = "octopus_energy_gas_previous_consumption_rates"
EVENT_GAS_PREVIOUS_CONSUMPTION_OVERRIDE_RATES = "octopus_energy_gas_previous_consumption_override_rates"

# During BST, two records are returned before the rest of the data is available
MINIMUM_CONSUMPTION_DATA_LENGTH = 3

COORDINATOR_REFRESH_IN_SECONDS = 60