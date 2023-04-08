from datetime import timedelta
import logging

from .utils.check_tariff import async_check_valid_tariff
from .sensors.electricity.current_consumption import OctopusEnergyCurrentElectricityConsumption
from .sensors.electricity.current_demand import OctopusEnergyCurrentElectricityDemand
from .sensors.electricity.current_rate import OctopusEnergyElectricityCurrentRate
from .sensors.electricity.next_rate import OctopusEnergyElectricityNextRate
from .sensors.electricity.previous_accumulative_consumption import OctopusEnergyPreviousAccumulativeElectricityConsumption
from .sensors.electricity.previous_accumulative_cost import OctopusEnergyPreviousAccumulativeElectricityCost
from .sensors.electricity.previous_rate import OctopusEnergyElectricityPreviousRate
from .sensors.electricity.standing_charge import OctopusEnergyElectricityCurrentStandingCharge
from .sensors.gas.current_rate import OctopusEnergyGasCurrentRate
from .sensors.gas.previous_accumulative_consumption import OctopusEnergyPreviousAccumulativeGasConsumption
from .sensors.gas.previous_accumulative_consumption_kwh import OctopusEnergyPreviousAccumulativeGasConsumptionKwh
from .sensors.gas.previous_accumulative_cost import OctopusEnergyPreviousAccumulativeGasCost
from .sensors.gas.current_consumption import OctopusEnergyCurrentGasConsumption
from .sensors.gas.standing_charge import OctopusEnergyGasCurrentStandingCharge

from .sensors.saving_sessions.points import OctopusEnergySavingSessionPoints

from homeassistant.util.dt import (utcnow, now, as_utc, parse_datetime)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from .sensors import (
  async_get_consumption_data,
  async_get_live_consumption
)

from .utils import (get_active_tariff_code)
from .const import (
  DOMAIN,
  
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION,
  CONFIG_MAIN_CALORIFIC_VALUE,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,

  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_SAVING_SESSIONS_COORDINATOR,
  DATA_CLIENT,
  DATA_ACCOUNT,
  DATA_GAS_RATES
)

from .api_client import (OctopusEnergyApiClient)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

def create_reading_coordinator(hass, client: OctopusEnergyApiClient, is_electricity: bool, identifier: str, serial_number: str):
  """Create reading coordinator"""

  async def async_update_data():
    """Fetch data from API endpoint."""

    previous_consumption_key = f'{identifier}_{serial_number}_previous_consumption'
    previous_data = None
    if previous_consumption_key in hass.data[DOMAIN]:
      previous_data = hass.data[DOMAIN][previous_consumption_key]

    period_from = as_utc((now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = as_utc(now().replace(hour=0, minute=0, second=0, microsecond=0))

    data = await async_get_consumption_data(
      client,
      previous_data,
      utcnow(),
      period_from,
      period_to,
      identifier,
      serial_number,
      is_electricity
    )

    if data != None and len(data) > 0:
      hass.data[DOMAIN][previous_consumption_key] = data
      return data

    return []

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"rates_{identifier}_{serial_number}",
    update_method=async_update_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

  hass.data[DOMAIN][f'{identifier}_{serial_number}_consumption_coordinator'] = coordinator

  return coordinator

def create_current_consumption_coordinator(hass, client: OctopusEnergyApiClient, device_id: str, is_electricity: bool):
  """Create current consumption coordinator"""

  async def async_update_data():
    """Fetch data from API endpoint."""
    previous_current_consumption_date_key = f'{device_id}_previous_current_consumption_date'
    last_date = None
    if previous_current_consumption_date_key in hass.data[DOMAIN]:
      last_date = hass.data[DOMAIN][previous_current_consumption_date_key]
    elif is_electricity == False:
      last_date = (now() - timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    data = await async_get_live_consumption(client, device_id, utcnow(), last_date)
    if data is not None:
      hass.data[DOMAIN][previous_current_consumption_date_key] = data["startAt"]

    return data

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"current_consumption_{device_id}",
    update_method=async_update_data,
    update_interval=timedelta(minutes=1),
  )

  return coordinator

def create_gas_rate_coordinator(hass, client: OctopusEnergyApiClient, tariff_code: str):
  """Create gas rate coordinator"""

  async def async_update_data():
    """Fetch data from API endpoint."""
    current = utcnow()
    
    rate_key = f'{DATA_GAS_RATES}_{tariff_code}'
    if (rate_key not in hass.data[DOMAIN] or (current.minute % 30) == 0 or len(hass.data[DOMAIN][rate_key]) == 0):
      period_from = as_utc(parse_datetime(current.strftime("%Y-%m-%dT00:00:00Z")))
      period_to = as_utc(parse_datetime((current + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")))

      hass.data[DOMAIN][rate_key] = await client.async_get_gas_rates(tariff_code, period_from, period_to)
      await async_check_valid_tariff(hass, client, tariff_code, False)

    return hass.data[DOMAIN][rate_key]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"gas_rates_{tariff_code}",
    update_method=async_update_data,
    update_interval=timedelta(minutes=1),
  )

  return coordinator

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_default_sensors(hass, entry, async_add_entities)

async def async_setup_default_sensors(hass, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)
  
  client = hass.data[DOMAIN][DATA_CLIENT]
  
  rate_coordinator = hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR]

  await rate_coordinator.async_config_entry_first_refresh()

  saving_session_coordinator = hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR]

  await saving_session_coordinator.async_config_entry_first_refresh()

  entities = [OctopusEnergySavingSessionPoints(saving_session_coordinator)]
  
  account_info = hass.data[DOMAIN][DATA_ACCOUNT]

  now = utcnow()

  if len(account_info["electricity_meter_points"]) > 0:
    electricity_price_cap = None
    if CONFIG_MAIN_ELECTRICITY_PRICE_CAP in config:
      electricity_price_cap = config[CONFIG_MAIN_ELECTRICITY_PRICE_CAP]

    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      electricity_tariff_code = get_active_tariff_code(now, point["agreements"])
      if electricity_tariff_code != None:
        for meter in point["meters"]:
          _LOGGER.info(f'Adding electricity meter; mpan: {point["mpan"]}; serial number: {meter["serial_number"]}')
          entities.append(OctopusEnergyElectricityCurrentRate(rate_coordinator, meter, point, electricity_price_cap))
          entities.append(OctopusEnergyElectricityPreviousRate(rate_coordinator, meter, point))
          entities.append(OctopusEnergyElectricityNextRate(rate_coordinator, meter, point))
          entities.append(OctopusEnergyElectricityCurrentStandingCharge(client, electricity_tariff_code, meter, point))

          if meter["is_smart_meter"] == True:
            coordinator = create_reading_coordinator(hass, client, True, point["mpan"], meter["serial_number"])
            entities.append(OctopusEnergyPreviousAccumulativeElectricityConsumption(coordinator, meter, point))
            entities.append(OctopusEnergyPreviousAccumulativeElectricityCost(coordinator, client, electricity_tariff_code, meter, point))

            if meter["is_export"] == False and CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in config and config[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True:
              consumption_coordinator = create_current_consumption_coordinator(hass, client, meter["device_id"], True)
              entities.append(OctopusEnergyCurrentElectricityConsumption(consumption_coordinator, meter, point))
              entities.append(OctopusEnergyCurrentElectricityDemand(consumption_coordinator, meter, point))
      else:
        for meter in point["meters"]:
          _LOGGER.info(f'Skipping electricity meter due to no active agreement; mpan: {point["mpan"]}; serial number: {meter["serial_number"]}')
        _LOGGER.info(f'agreements: {point["agreements"]}')
  else:
    _LOGGER.info('No electricity meters available')

  if len(account_info["gas_meter_points"]) > 0:

    calorific_value = 40
    if CONFIG_MAIN_CALORIFIC_VALUE in config:
      calorific_value = config[CONFIG_MAIN_CALORIFIC_VALUE]

    gas_price_cap = None
    if CONFIG_MAIN_GAS_PRICE_CAP in config:
      gas_price_cap = config[CONFIG_MAIN_GAS_PRICE_CAP]

    for point in account_info["gas_meter_points"]:
      # We only care about points that have active agreements
      gas_tariff_code = get_active_tariff_code(now, point["agreements"])
      if gas_tariff_code != None:
        for meter in point["meters"]:
          _LOGGER.info(f'Adding gas meter; mprn: {point["mprn"]}; serial number: {meter["serial_number"]}')
          rate_coordinator = create_gas_rate_coordinator(hass, client, gas_tariff_code)
          entities.append(OctopusEnergyGasCurrentRate(rate_coordinator, gas_tariff_code, meter, point, gas_price_cap))
          entities.append(OctopusEnergyGasCurrentStandingCharge(client, gas_tariff_code, meter, point))

          if meter["is_smart_meter"] == True:
            previous_consumption_coordinator = create_reading_coordinator(hass, client, False, point["mprn"], meter["serial_number"])
            entities.append(OctopusEnergyPreviousAccumulativeGasConsumption(previous_consumption_coordinator, meter, point, calorific_value))
            entities.append(OctopusEnergyPreviousAccumulativeGasConsumptionKwh(previous_consumption_coordinator, meter, point, calorific_value))
            entities.append(OctopusEnergyPreviousAccumulativeGasCost(previous_consumption_coordinator, client, gas_tariff_code, meter, point, calorific_value))

            if CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in config and config[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True:
              consumption_coordinator = create_current_consumption_coordinator(hass, client, meter["device_id"], False)
              entities.append(OctopusEnergyCurrentGasConsumption(consumption_coordinator, meter, point))
      else:
        for meter in point["meters"]:
          _LOGGER.info(f'Skipping gas meter due to no active agreement; mprn: {point["mprn"]}; serial number: {meter["serial_number"]}')
        _LOGGER.info(f'agreements: {point["agreements"]}')
  else:
    _LOGGER.info('No gas meters available')

  async_add_entities(entities, True)
