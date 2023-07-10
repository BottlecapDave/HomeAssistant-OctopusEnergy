import voluptuous as vol
import homeassistant.helpers.config_validation as cv

DOMAIN = "octopus_energy"

CONFIG_MAIN_API_KEY = "Api key"
CONFIG_MAIN_ACCOUNT_ID = "Account Id"
CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION = "supports_live_consumption"
CONFIG_MAIN_CALORIFIC_VALUE = "calorific_value"
CONFIG_MAIN_ELECTRICITY_PRICE_CAP = "electricity_price_cap"
CONFIG_MAIN_CLEAR_ELECTRICITY_PRICE_CAP = "clear_electricity_price_cap"
CONFIG_MAIN_GAS_PRICE_CAP = "gas_price_cap"
CONFIG_MAIN_CLEAR_GAS_PRICE_CAP = "clear_gas_price_cap"

CONFIG_TARGET_NAME = "Name"
CONFIG_TARGET_HOURS = "Hours"
CONFIG_TARGET_TYPE = "Type"
CONFIG_TARGET_START_TIME = "Start time"
CONFIG_TARGET_END_TIME = "End time"
CONFIG_TARGET_MPAN = "MPAN"
CONFIG_TARGET_OFFSET = "offset"
CONFIG_TARGET_ROLLING_TARGET = "rolling_target"
CONFIG_TARGET_LAST_RATES = "last_rates"

DATA_CONFIG = "CONFIG"
DATA_ELECTRICITY_RATES_COORDINATOR = "ELECTRICITY_RATES_COORDINATOR"
DATA_CLIENT = "CLIENT"
DATA_RATES = "RATES"
DATA_GAS_TARIFF_CODE = "GAS_TARIFF_CODE"
DATA_ACCOUNT_ID = "ACCOUNT_ID"
DATA_ACCOUNT = "ACCOUNT"
DATA_ACCOUNT_COORDINATOR = "ACCOUNT_COORDINATOR"
DATA_SAVING_SESSIONS = "SAVING_SESSIONS"
DATA_SAVING_SESSIONS_COORDINATOR = "SAVING_SESSIONS_COORDINATOR"
DATA_KNOWN_TARIFF = "KNOWN_TARIFF"
DATA_GAS_RATES = "GAS_RATES"
DATA_INTELLIGENT_DISPATCHES = "INTELLIGENT_DISPATCHES"
DATA_INTELLIGENT_DISPATCHES_COORDINATOR = "INTELLIGENT_DISPATCHES_COORDINATOR"
DATA_INTELLIGENT_SETTINGS = "INTELLIGENT_SETTINGS"
DATA_INTELLIGENT_SETTINGS_COORDINATOR = "INTELLIGENT_SETTINGS_COORDINATOR"

STORAGE_COMPLETED_DISPATCHES_NAME = "octopus_energy.{}-completed-intelligent-dispatches.json"

STORAGE_COMPLETED_DISPATCHES_NAME = "octopus_energy.{}-completed-intelligent-dispatches.json"

REGEX_HOURS = "^[0-9]+(\\.[0-9]+)*$"
REGEX_TIME = "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
REGEX_ENTITY_NAME = "^[a-z0-9_]+$"
# According to https://www.guylipman.com/octopus/api_guide.html#s1b, this part should indicate the types of tariff
# However it looks like there are some tariffs that don't fit this mold
REGEX_TARIFF_PARTS = "^((?P<energy>[A-Z])-(?P<rate>[0-9A-Z]+)-)?(?P<product_code>[A-Z0-9-]+)-(?P<region>[A-Z])$"
REGEX_OFFSET_PARTS = "^(-)?([0-1]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$"

DATA_SCHEMA_ACCOUNT = vol.Schema({
  vol.Required(CONFIG_MAIN_API_KEY): str,
  vol.Required(CONFIG_MAIN_ACCOUNT_ID): str,
  vol.Required(CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION): bool,
  vol.Required(CONFIG_MAIN_CALORIFIC_VALUE, default=40.0): cv.positive_float,
  vol.Optional(CONFIG_MAIN_ELECTRICITY_PRICE_CAP): cv.positive_float,
  vol.Optional(CONFIG_MAIN_GAS_PRICE_CAP): cv.positive_float
})
