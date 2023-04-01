import logging
from datetime import timedelta
import asyncio

from homeassistant.util.dt import (now, as_utc)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from homeassistant.helpers import issue_registry as ir

from .const import (
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ACCOUNT_ID,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,
  
  CONFIG_TARGET_NAME,

  DATA_CLIENT,
  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_RATES,
  DATA_ACCOUNT_ID,
  DATA_ACCOUNT,
  DATA_SAVING_SESSIONS,
  DATA_SAVING_SESSIONS_COORDINATOR
)

from .api_client import OctopusEnergyApiClient

from .utils import (
  get_active_tariff_code
)

from .utils.check_tariff import (async_check_valid_tariff)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""
  hass.data.setdefault(DOMAIN, {})

  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  if CONFIG_MAIN_API_KEY in config:
    await async_setup_dependencies(hass, config)

    # Forward our entry to setup our default sensors
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )
  elif CONFIG_TARGET_NAME in config:
    if DOMAIN not in hass.data or DATA_ELECTRICITY_RATES_COORDINATOR not in hass.data[DOMAIN] or DATA_ACCOUNT not in hass.data[DOMAIN]:
      raise ConfigEntryNotReady

    # Forward our entry to setup our target rate sensors
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )
  
  entry.async_on_unload(entry.add_update_listener(options_update_listener))

  return True

async def async_get_current_electricity_agreement_tariff_codes(hass, client: OctopusEnergyApiClient, account_id: str):
  account_info = None
  try:
    account_info = await client.async_get_account(account_id)
  except:
    # count exceptions as failure to retrieve account
    _LOGGER.debug('Failed to retrieve account')

  if account_info is None:
    ir.async_create_issue(
      hass,
      DOMAIN,
      f"account_not_found_{account_id}",
      is_fixable=False,
      severity=ir.IssueSeverity.ERROR,
      learn_more_url="https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/blob/develop/_docs/repairs/account_not_found.md",
      translation_key="account_not_found",
      translation_placeholders={ "account_id": account_id },
    )
  else:
    ir.async_delete_issue(hass, DOMAIN, f"account_not_found_{account_id}")

  tariff_codes = {}
  current = now()
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff_code = get_active_tariff_code(current, point["agreements"])
      # The type of meter (ie smart vs dumb) can change the tariff behaviour, so we
      # have to enumerate the different meters being used for each tariff as well.
      for meter in point["meters"]:
        is_smart_meter = meter["is_smart_meter"]
        if active_tariff_code != None:
          key = (point["mpan"], is_smart_meter)
          if key not in tariff_codes:
            tariff_codes[(point["mpan"], is_smart_meter)] = active_tariff_code
            await async_check_valid_tariff(hass, client, active_tariff_code, True)
  
  return tariff_codes

async def async_setup_dependencies(hass, config):
  """Setup the coordinator and api client which will be shared by various entities"""

  electricity_price_cap = None
  if CONFIG_MAIN_ELECTRICITY_PRICE_CAP in config:
    electricity_price_cap = config[CONFIG_MAIN_ELECTRICITY_PRICE_CAP]

  gas_price_cap = None
  if CONFIG_MAIN_GAS_PRICE_CAP in config:
    gas_price_cap = config[CONFIG_MAIN_GAS_PRICE_CAP]

  _LOGGER.info(f'electricity_price_cap: {electricity_price_cap}')
  _LOGGER.info(f'gas_price_cap: {gas_price_cap}')

  client = OctopusEnergyApiClient(config[CONFIG_MAIN_API_KEY], electricity_price_cap, gas_price_cap)
  hass.data[DOMAIN][DATA_CLIENT] = client
  hass.data[DOMAIN][DATA_ACCOUNT_ID] = config[CONFIG_MAIN_ACCOUNT_ID]

  setup_rates_coordinator(hass, config[CONFIG_MAIN_ACCOUNT_ID])

  setup_saving_sessions_coordinators(hass)

  account_info = await client.async_get_account(config[CONFIG_MAIN_ACCOUNT_ID])

  hass.data[DOMAIN][DATA_ACCOUNT] = account_info

def setup_rates_coordinator(hass, account_id: str):
  # Reset data rates as we might have new information
  hass.data[DOMAIN][DATA_RATES] = []

  if DATA_ELECTRICITY_RATES_COORDINATOR in hass.data[DOMAIN]:
    _LOGGER.info("Rates coordinator has already been configured, so skipping")
    return
  
  async def async_update_electricity_rates_data():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    if (DATA_RATES not in hass.data[DOMAIN] or (current.minute % 30) == 0 or len(hass.data[DOMAIN][DATA_RATES]) == 0):

      tariff_codes = await async_get_current_electricity_agreement_tariff_codes(hass, client, account_id)
      _LOGGER.debug(f'tariff_codes: {tariff_codes}')

      period_from = as_utc(current.replace(hour=0, minute=0, second=0, microsecond=0))
      period_to = as_utc((current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0))

      rates = {}
      for ((meter_point, is_smart_meter), tariff_code) in tariff_codes.items():
        key = meter_point
        new_rates = await client.async_get_electricity_rates(tariff_code, is_smart_meter, period_from, period_to)
        if new_rates != None:
          rates[key] = new_rates
        elif (DATA_RATES in hass.data[DOMAIN] and key in hass.data[DOMAIN][DATA_RATES]):
          _LOGGER.debug(f"Failed to retrieve new rates for {tariff_code}, so using cached rates")
          rates[key] = hass.data[DOMAIN][DATA_RATES][key]
      
      hass.data[DOMAIN][DATA_RATES] = rates
    
    return hass.data[DOMAIN][DATA_RATES]

  hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="rates",
    update_method=async_update_electricity_rates_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

def setup_saving_sessions_coordinators(hass):
  if DATA_SAVING_SESSIONS_COORDINATOR in hass.data[DOMAIN]:
    return

  async def async_update_saving_sessions():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    if DATA_SAVING_SESSIONS not in hass.data[DOMAIN] or current.minute % 30 == 0:
      savings = await client.async_get_saving_sessions(hass.data[DOMAIN][DATA_ACCOUNT_ID])
      
      hass.data[DOMAIN][DATA_SAVING_SESSIONS] = savings
    
    return hass.data[DOMAIN][DATA_SAVING_SESSIONS]

  hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="saving_sessions",
    update_method=async_update_saving_sessions,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

async def options_update_listener(hass, entry):
  """Handle options update."""
  await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    if CONFIG_MAIN_API_KEY in entry.data:
      target_domain = "sensor"
    elif CONFIG_TARGET_NAME in entry.data:
      target_domain = "binary_sensor"

    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, target_domain)]
        )
    )

    return unload_ok