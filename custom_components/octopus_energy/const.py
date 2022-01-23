import voluptuous as vol

DOMAIN = "octopus_energy"

CONFIG_MAIN_API_KEY = "Api key"
CONFIG_MAIN_ACCOUNT_ID = "Account Id"
CONFIG_SMETS1 = "SMETS1"

CONFIG_TARGET_NAME = "Name"
CONFIG_TARGET_HOURS = "Hours"
CONFIG_TARGET_TYPE = "Type"
CONFIG_TARGET_START_TIME = "Start time"
CONFIG_TARGET_END_TIME = "End time"
CONFIG_TARGET_MPAN = "MPAN"

DATA_CONFIG = "CONFIG"
DATA_ELECTRICITY_RATES_COORDINATOR = "ELECTRICITY_RATES_COORDINATOR"
DATA_CLIENT = "CLIENT"
DATA_RATES = "RATES"
DATA_GAS_TARIFF_CODE = "GAS_TARIFF_CODE"

REGEX_HOURS = "^[0-9]+(\.[0-9]+)*$"
REGEX_TIME = "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
REGEX_ENTITY_NAME = "^[a-z0-9_]+$"
REGEX_TARIFF_PARTS = "^([A-Z])-([0-9A-Z]+)-([A-Z0-9-]+)-([A-Z])$"

DATA_SCHEMA_ACCOUNT = vol.Schema({
  vol.Required(CONFIG_MAIN_API_KEY): str,
  vol.Required(CONFIG_MAIN_ACCOUNT_ID): str,
  vol.Optional(CONFIG_SMETS1): bool,
})

DATA_SCHEMA_TARGET = vol.Schema({
  vol.Required(CONFIG_TARGET_NAME): str,
  vol.Required(CONFIG_TARGET_HOURS): str,
  vol.Required(CONFIG_TARGET_TYPE, default="Continuous"): vol.In({
    "Continuous": "Continuous",
    "Intermittent": "Intermittent"
  }),
  vol.Required(CONFIG_TARGET_MPAN): str,
  vol.Optional(CONFIG_TARGET_START_TIME): str,
  vol.Optional(CONFIG_TARGET_END_TIME): str,
})