import logging
from datetime import timedelta

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.components.recorder import get_instance
from homeassistant.util.dt import (utcnow)
from homeassistant.const import (
    EVENT_HOMEASSISTANT_STOP
)
from homeassistant.helpers import issue_registry as ir

from .api_client_home_pro import OctopusEnergyHomeProApiClient
from .coordinators.account import AccountCoordinatorResult, async_setup_account_info_coordinator
from .coordinators.intelligent_dispatches import async_setup_intelligent_dispatches_coordinator
from .coordinators.intelligent_settings import async_setup_intelligent_settings_coordinator
from .coordinators.electricity_rates import async_setup_electricity_rates_coordinator
from .coordinators.saving_sessions import async_setup_saving_sessions_coordinators
from .coordinators.greenness_forecast import async_setup_greenness_forecast_coordinator
from .statistics import get_statistic_ids_to_remove
from .intelligent import async_mock_intelligent_data, get_intelligent_features, is_intelligent_product, mock_intelligent_device

from .config.main import async_migrate_main_config
from .config.target_rates import async_migrate_target_config
from .config.cost_tracker import async_migrate_cost_tracker_config
from .utils import get_active_tariff
from .utils.tariff_overrides import async_get_tariff_override

from .const import (
  CONFIG_FAVOUR_DIRECT_DEBIT_RATES,
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_TARIFF_COMPARISON,
  CONFIG_KIND_COST_TRACKER,
  CONFIG_KIND_TARGET_RATE,
  CONFIG_MAIN_HOME_PRO_ADDRESS,
  CONFIG_MAIN_HOME_PRO_API_KEY,
  CONFIG_MAIN_OLD_API_KEY,
  CONFIG_VERSION,
  DATA_HOME_PRO_CLIENT,
  DATA_INTELLIGENT_DEVICE,
  DATA_INTELLIGENT_MPAN,
  DATA_INTELLIGENT_SERIAL_NUMBER,
  DATA_PREVIOUS_CONSUMPTION_COORDINATOR_KEY,
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  CONFIG_ACCOUNT_ID,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,

  DATA_CLIENT,
  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DATA_ACCOUNT,
  REPAIR_ACCOUNT_NOT_FOUND,
  REPAIR_INVALID_API_KEY,
  REPAIR_UNIQUE_RATES_CHANGED_KEY,
  REPAIR_UNKNOWN_INTELLIGENT_PROVIDER
)

ACCOUNT_PLATFORMS = ["sensor", "binary_sensor", "number", "switch", "text", "time", "event"]
TARGET_RATE_PLATFORMS = ["binary_sensor"]
COST_TRACKER_PLATFORMS = ["sensor"]
TARIFF_COMPARISON_PLATFORMS = ["sensor"]

from .api_client import AuthenticationException, OctopusEnergyApiClient, RequestException

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_remove_config_entry_device(
  hass, config_entry, device_entry
) -> bool:
  """Remove a config entry from a device."""
  return True

async def async_migrate_entry(hass, config_entry):
  """Migrate old entry."""
  if (config_entry.version < CONFIG_VERSION):
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    new_data = None
    new_options = None
    title = config_entry.title
    if CONFIG_MAIN_API_KEY in config_entry.data or CONFIG_MAIN_OLD_API_KEY in config_entry.data or (CONFIG_KIND in config_entry.data and config_entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT):
      new_data = await async_migrate_main_config(config_entry.version, config_entry.data)
      new_options = await async_migrate_main_config(config_entry.version, config_entry.options)
      title = new_data[CONFIG_ACCOUNT_ID]
    elif CONFIG_KIND in config_entry.data and config_entry.data[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE:
      new_data = await async_migrate_target_config(config_entry.version, config_entry.data, hass.config_entries.async_entries)
      new_options = await async_migrate_target_config(config_entry.version, config_entry.options, hass.config_entries.async_entries)
    elif CONFIG_KIND in config_entry.data and config_entry.data[CONFIG_KIND] == CONFIG_KIND_COST_TRACKER:
      new_data = await async_migrate_cost_tracker_config(config_entry.version, config_entry.data, hass.config_entries.async_entries)
      new_options = await async_migrate_cost_tracker_config(config_entry.version, config_entry.options, hass.config_entries.async_entries)
    elif CONFIG_KIND in config_entry.data and config_entry.data[CONFIG_KIND] == CONFIG_KIND_TARIFF_COMPARISON:
      new_data = await async_migrate_cost_tracker_config(config_entry.version, config_entry.data, hass.config_entries.async_entries)
      new_options = await async_migrate_cost_tracker_config(config_entry.version, config_entry.options, hass.config_entries.async_entries)
    
    config_entry.version = CONFIG_VERSION
    hass.config_entries.async_update_entry(config_entry, title=title, data=new_data, options=new_options)

    _LOGGER.debug("Migration to version %s successful", config_entry.version)

  return True

async def _async_close_client(hass, account_id: str):
  if account_id in hass.data[DOMAIN]:
    if DATA_CLIENT in hass.data[DOMAIN][account_id]:
      _LOGGER.debug('Closing client...')
      client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
      await client.async_close()
      _LOGGER.debug('Client closed.')

    if DATA_HOME_PRO_CLIENT in hass.data[DOMAIN][account_id]:
      _LOGGER.debug('Closing home pro client...')
      client: OctopusEnergyHomeProApiClient = hass.data[DOMAIN][account_id][DATA_HOME_PRO_CLIENT]
      await client.async_close()
      _LOGGER.debug('Home pro client closed.')

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""
  hass.data.setdefault(DOMAIN, {})

  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  account_id = config[CONFIG_ACCOUNT_ID]
  hass.data[DOMAIN].setdefault(account_id, {})

  if config[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
    await async_setup_dependencies(hass, config)
    await hass.config_entries.async_forward_entry_setups(entry, ACCOUNT_PLATFORMS)

    async def async_close_connection(_) -> None:
      """Close client."""
      await _async_close_client(hass, account_id)

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_close_connection)
    )

    # If the main account has been reloaded, then reload all other entries to make sure they're referencing
    # the correct references (e.g. rate coordinators)
    child_entries = hass.config_entries.async_entries(DOMAIN)
    for child_entry in child_entries:
      if child_entry.data[CONFIG_KIND] != CONFIG_KIND_ACCOUNT and child_entry.data[CONFIG_ACCOUNT_ID] == account_id:
        await hass.config_entries.async_reload(child_entry.entry_id)
  
  elif config[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE:
    if DOMAIN not in hass.data or account_id not in hass.data[DOMAIN] or DATA_ACCOUNT not in hass.data[DOMAIN][account_id]:
      raise ConfigEntryNotReady("Account has not been setup")
    
    now = utcnow()
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      electricity_tariff = get_active_tariff(now, point["agreements"])
      if electricity_tariff is not None:
        for meter in point["meters"]:
          mpan = point["mpan"]
          serial_number = meter["serial_number"]
          previous_consumption_coordinator_key = DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number)
          if previous_consumption_coordinator_key not in hass.data[DOMAIN][account_id]:
            raise ConfigEntryNotReady(f"Electricity rates have not been setup for {mpan}/{serial_number}")

    await hass.config_entries.async_forward_entry_setups(entry, TARGET_RATE_PLATFORMS)
  
  elif config[CONFIG_KIND] == CONFIG_KIND_COST_TRACKER:
    if DOMAIN not in hass.data or account_id not in hass.data[DOMAIN] or DATA_ACCOUNT not in hass.data[DOMAIN][account_id]:
      raise ConfigEntryNotReady("Account has not been setup")
    
    now = utcnow()
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      electricity_tariff = get_active_tariff(now, point["agreements"])
      if electricity_tariff is not None:
        for meter in point["meters"]:
          mpan = point["mpan"]
          serial_number = meter["serial_number"]
          previous_consumption_coordinator_key = DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number)
          if previous_consumption_coordinator_key not in hass.data[DOMAIN][account_id]:
            raise ConfigEntryNotReady(f"Electricity rates have not been setup for {mpan}/{serial_number}")

    await hass.config_entries.async_forward_entry_setups(entry, COST_TRACKER_PLATFORMS)
  
  elif config[CONFIG_KIND] == CONFIG_KIND_TARIFF_COMPARISON:
    if DOMAIN not in hass.data or account_id not in hass.data[DOMAIN] or DATA_ACCOUNT not in hass.data[DOMAIN][account_id]:
      raise ConfigEntryNotReady("Account has not been setup")
    
    now = utcnow()
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      electricity_tariff = get_active_tariff(now, point["agreements"])
      if electricity_tariff is not None:
        for meter in point["meters"]:
          mpan = point["mpan"]
          serial_number = meter["serial_number"]
          previous_consumption_coordinator_key = DATA_PREVIOUS_CONSUMPTION_COORDINATOR_KEY.format(mpan, serial_number)
          if previous_consumption_coordinator_key not in hass.data[DOMAIN][account_id]:
            raise ConfigEntryNotReady(f"Previous electricity consumption has not been setup for {mpan}/{serial_number}")
          
    for point in account_info["gas_meter_points"]:
      # We only care about points that have active agreements
      gas_tariff = get_active_tariff(now, point["agreements"])
      if gas_tariff is not None:
        for meter in point["meters"]:
          mprn = point["mprn"]
          serial_number = meter["serial_number"]
          previous_consumption_coordinator_key = DATA_PREVIOUS_CONSUMPTION_COORDINATOR_KEY.format(mprn, serial_number)
          if previous_consumption_coordinator_key not in hass.data[DOMAIN][account_id]:
            raise ConfigEntryNotReady(f"Previous gas consumption has not been setup for {mprn}/{serial_number}")

    await hass.config_entries.async_forward_entry_setups(entry, TARIFF_COMPARISON_PLATFORMS)
  
  entry.async_on_unload(entry.add_update_listener(options_update_listener))

  return True

async def async_setup_dependencies(hass, config):
  """Setup the coordinator and api client which will be shared by various entities"""
  account_id = config[CONFIG_ACCOUNT_ID]

  electricity_price_cap = None
  if CONFIG_MAIN_ELECTRICITY_PRICE_CAP in config:
    electricity_price_cap = config[CONFIG_MAIN_ELECTRICITY_PRICE_CAP]

  gas_price_cap = None
  if CONFIG_MAIN_GAS_PRICE_CAP in config:
    gas_price_cap = config[CONFIG_MAIN_GAS_PRICE_CAP]

  favour_direct_debit_rates = True
  if CONFIG_FAVOUR_DIRECT_DEBIT_RATES in config:
    favour_direct_debit_rates = config[CONFIG_FAVOUR_DIRECT_DEBIT_RATES]

  _LOGGER.info(f'electricity_price_cap: {electricity_price_cap}')
  _LOGGER.info(f'gas_price_cap: {gas_price_cap}')

  # Close any existing clients, as our new client may have changed
  await _async_close_client(hass, account_id)
  client = OctopusEnergyApiClient(config[CONFIG_MAIN_API_KEY], electricity_price_cap, gas_price_cap, favour_direct_debit_rates=favour_direct_debit_rates)
  hass.data[DOMAIN][account_id][DATA_CLIENT] = client

  if (CONFIG_MAIN_HOME_PRO_ADDRESS in config and
      config[CONFIG_MAIN_HOME_PRO_ADDRESS] is not None and
      CONFIG_MAIN_HOME_PRO_API_KEY in config and
      config[CONFIG_MAIN_HOME_PRO_API_KEY] is not None):
    home_pro_client = OctopusEnergyHomeProApiClient(config[CONFIG_MAIN_HOME_PRO_ADDRESS], config[CONFIG_MAIN_HOME_PRO_API_KEY])
    hass.data[DOMAIN][account_id][DATA_HOME_PRO_CLIENT] = home_pro_client

  # Delete any issues that may have been previously raised
  ir.async_delete_issue(hass, DOMAIN, REPAIR_UNIQUE_RATES_CHANGED_KEY.format(account_id))
  ir.async_delete_issue(hass, DOMAIN, REPAIR_ACCOUNT_NOT_FOUND.format(account_id))

  try:
    account_info = await client.async_get_account(config[CONFIG_ACCOUNT_ID])
    ir.async_delete_issue(hass, DOMAIN, REPAIR_INVALID_API_KEY.format(account_id))
    if (account_info is None):
      raise ConfigEntryNotReady(f"Failed to retrieve account information")
  except Exception as e:
    if isinstance(e, RequestException) == False:
      raise

    if isinstance(e, AuthenticationException):
      ir.async_create_issue(
        hass,
        DOMAIN,
        REPAIR_INVALID_API_KEY.format(account_id),
        is_fixable=False,
        severity=ir.IssueSeverity.ERROR,
        translation_key="invalid_api_key",
        translation_placeholders={ "account_id": account_id },
      )
    
    raise ConfigEntryNotReady(f"Failed to retrieve account information")

  hass.data[DOMAIN][account_id][DATA_ACCOUNT] = AccountCoordinatorResult(utcnow(), 1, account_info)

  device_registry = dr.async_get(hass)
  now = utcnow()

  if account_info is not None and len(account_info["gas_meter_points"]) > 0:
    for point in account_info["gas_meter_points"]:
      mprn = point["mprn"]
      for meter in point["meters"]:
        serial_number = meter["serial_number"]

        tariff = get_active_tariff(now, point["agreements"])
        if tariff is None:
          gas_device = device_registry.async_get_device(identifiers={(DOMAIN, f"gas_{serial_number}_{mprn}")})
          if gas_device is not None:
            _LOGGER.debug(f'Removed gas device {serial_number}/{mprn} due to no active tariff')
            device_registry.async_remove_device(gas_device.id)

        # Remove gas meter devices which had incorrect identifier
        gas_device = device_registry.async_get_device(identifiers={(DOMAIN, f"electricity_{serial_number}_{mprn}")})
        if gas_device is not None:
          device_registry.async_remove_device(gas_device.id)

  has_intelligent_tariff = False
  intelligent_mpan = None
  intelligent_serial_number = None
  for point in account_info["electricity_meter_points"]:
    mpan = point["mpan"]
    electricity_tariff = get_active_tariff(now, point["agreements"])

    for meter in point["meters"]:  
      serial_number = meter["serial_number"]
      
      if electricity_tariff is not None:
        if meter["is_export"] == False:
          if is_intelligent_product(electricity_tariff.product):
            intelligent_mpan = mpan
            intelligent_serial_number = serial_number
            has_intelligent_tariff = True
      else:
        _LOGGER.debug(f'Removed electricity device {serial_number}/{mpan} due to no active tariff')
        electricity_device = device_registry.async_get_device(identifiers={(DOMAIN, f"electricity_{serial_number}_{mpan}")})
        if electricity_device is not None:
          device_registry.async_remove_device(electricity_device.id)

  should_mock_intelligent_data = await async_mock_intelligent_data(hass, account_id)
  if should_mock_intelligent_data:
    # Pick the first meter if we're mocking our intelligent data
    for point in account_info["electricity_meter_points"]:
      tariff = get_active_tariff(now, point["agreements"])
      if tariff is not None:
        for meter in point["meters"]:
          intelligent_mpan = point["mpan"]
          intelligent_serial_number = meter["serial_number"]
          break

  intelligent_device = None
  if has_intelligent_tariff or should_mock_intelligent_data:
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]

    if should_mock_intelligent_data:
      intelligent_device = mock_intelligent_device()
    else:
      intelligent_device = await client.async_get_intelligent_device(account_id)

    if intelligent_device is not None:
      hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE] = intelligent_device
      hass.data[DOMAIN][account_id][DATA_INTELLIGENT_MPAN] = intelligent_mpan
      hass.data[DOMAIN][account_id][DATA_INTELLIGENT_SERIAL_NUMBER] = intelligent_serial_number

  intelligent_features = get_intelligent_features(intelligent_device.provider)  if intelligent_device is not None else None
  if intelligent_features is not None and intelligent_features.is_default_features == True:
    ir.async_create_issue(
      hass,
      DOMAIN,
      REPAIR_UNKNOWN_INTELLIGENT_PROVIDER.format(intelligent_device.provider),
      is_fixable=False,
      severity=ir.IssueSeverity.WARNING,
      learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/unknown_intelligent_provider",
      translation_key="unknown_intelligent_provider",
      translation_placeholders={ "account_id": account_id, "provider": intelligent_device.provider },
    )

  for point in account_info["electricity_meter_points"]:
    # We only care about points that have active agreements
    electricity_tariff = get_active_tariff(now, point["agreements"])
    if electricity_tariff is not None:
      for meter in point["meters"]:
        mpan = point["mpan"]
        serial_number = meter["serial_number"]
        is_export_meter = meter["is_export"]
        is_smart_meter = meter["is_smart_meter"]
        tariff_override = await async_get_tariff_override(hass, mpan, serial_number)
        planned_dispatches_supported = intelligent_features.planned_dispatches_supported if intelligent_features is not None else True
        await async_setup_electricity_rates_coordinator(hass, account_id, mpan, serial_number, is_smart_meter, is_export_meter, planned_dispatches_supported, tariff_override)

  await async_setup_account_info_coordinator(hass, account_id)

  await async_setup_intelligent_dispatches_coordinator(hass, account_id)

  await async_setup_intelligent_settings_coordinator(hass, account_id)
  
  await async_setup_saving_sessions_coordinators(hass, account_id)

  await async_setup_greenness_forecast_coordinator(hass, account_id)

async def options_update_listener(hass, entry):
  """Handle options update."""
  await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    """Unload a config entry."""

    unload_ok = False
    if entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
      unload_ok = await hass.config_entries.async_unload_platforms(entry, ACCOUNT_PLATFORMS)
      if unload_ok:
        account_id = entry.data[CONFIG_ACCOUNT_ID]
        await _async_close_client(hass, account_id)
        hass.data[DOMAIN].pop(account_id)

    elif entry.data[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE:
      unload_ok = await hass.config_entries.async_unload_platforms(entry, TARGET_RATE_PLATFORMS)
    
    elif entry.data[CONFIG_KIND] == CONFIG_KIND_COST_TRACKER:
      unload_ok = await hass.config_entries.async_unload_platforms(entry, COST_TRACKER_PLATFORMS)

    return unload_ok

def setup(hass, config):
  """Set up is called when Home Assistant is loading our component."""

  def purge_invalid_external_statistic_ids(call):
    """Handle the service call."""

    account_id = None
    for entry in hass.config_entries.async_entries(DOMAIN):
      if CONFIG_KIND in entry.data and entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
        account_id = entry.data[CONFIG_ACCOUNT_ID]

    if account_id is None:
      raise Exception("Failed to find account id")
      
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
    
    external_statistic_ids_to_remove = get_statistic_ids_to_remove(utcnow(), account_info)

    if len(external_statistic_ids_to_remove) > 0:
      get_instance(hass).async_clear_statistics(external_statistic_ids_to_remove)
      _LOGGER.debug(f'Removing the following external statistics: {external_statistic_ids_to_remove}')

  hass.services.register(DOMAIN, "purge_invalid_external_statistic_ids", purge_invalid_external_statistic_ids)

  # Return boolean to indicate that initialization was successful.
  return True