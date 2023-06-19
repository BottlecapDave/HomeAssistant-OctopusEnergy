from datetime import timedelta
import logging
from homeassistant.util.dt import (utcnow)
from homeassistant.core import HomeAssistant

from .electricity.current_consumption import OctopusEnergyCurrentElectricityConsumption
from .electricity.current_demand import OctopusEnergyCurrentElectricityDemand
from .electricity.current_rate import OctopusEnergyElectricityCurrentRate
from .electricity.next_rate import OctopusEnergyElectricityNextRate
from .electricity.previous_accumulative_consumption import OctopusEnergyPreviousAccumulativeElectricityConsumption
from .electricity.previous_accumulative_consumption_off_peak import OctopusEnergyPreviousAccumulativeElectricityConsumptionOffPeak
from .electricity.previous_accumulative_consumption_peak import OctopusEnergyPreviousAccumulativeElectricityConsumptionPeak
from .electricity.previous_accumulative_cost import OctopusEnergyPreviousAccumulativeElectricityCost
from .electricity.previous_accumulative_cost_off_peak import OctopusEnergyPreviousAccumulativeElectricityCostOffPeak
from .electricity.previous_accumulative_cost_peak import OctopusEnergyPreviousAccumulativeElectricityCostPeak
from .electricity.previous_accumulative_cost_override import OctopusEnergyPreviousAccumulativeElectricityCostOverride
from .electricity.previous_rate import OctopusEnergyElectricityPreviousRate
from .electricity.standing_charge import OctopusEnergyElectricityCurrentStandingCharge
from .gas.current_rate import OctopusEnergyGasCurrentRate
from .gas.previous_accumulative_consumption import OctopusEnergyPreviousAccumulativeGasConsumption
from .gas.previous_accumulative_consumption_kwh import OctopusEnergyPreviousAccumulativeGasConsumptionKwh
from .gas.previous_accumulative_cost import OctopusEnergyPreviousAccumulativeGasCost
from .gas.current_consumption import OctopusEnergyCurrentGasConsumption
from .gas.standing_charge import OctopusEnergyGasCurrentStandingCharge
from .gas.previous_accumulative_cost_override import OctopusEnergyPreviousAccumulativeGasCostOverride

from .coordinators.current_consumption import async_create_current_consumption_coordinator
from .coordinators.gas_rates import async_create_gas_rate_coordinator
from .coordinators.previous_consumption_and_rates import async_create_previous_consumption_and_rates_coordinator

from .saving_sessions.points import OctopusEnergySavingSessionPoints

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
  DATA_ACCOUNT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_default_sensors(hass, entry, async_add_entities)

async def async_setup_default_sensors(hass: HomeAssistant, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)
  
  client = hass.data[DOMAIN][DATA_CLIENT]
  
  electricity_rate_coordinator = hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR]

  await electricity_rate_coordinator.async_config_entry_first_refresh()

  saving_session_coordinator = hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR]

  await saving_session_coordinator.async_config_entry_first_refresh()

  entities = [OctopusEnergySavingSessionPoints(hass, saving_session_coordinator)]
  
  account_info = hass.data[DOMAIN][DATA_ACCOUNT]

  now = utcnow()

  if len(account_info["electricity_meter_points"]) > 0:
    electricity_price_cap = None
    if CONFIG_MAIN_ELECTRICITY_PRICE_CAP in config:
      electricity_price_cap = config[CONFIG_MAIN_ELECTRICITY_PRICE_CAP]

    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      electricity_tariff_code = get_active_tariff_code(now, point["agreements"])
      if electricity_tariff_code is not None:
        for meter in point["meters"]:
          _LOGGER.info(f'Adding electricity meter; mpan: {point["mpan"]}; serial number: {meter["serial_number"]}')
          entities.append(OctopusEnergyElectricityCurrentRate(hass, electricity_rate_coordinator, meter, point, electricity_price_cap))
          entities.append(OctopusEnergyElectricityPreviousRate(hass, electricity_rate_coordinator, meter, point))
          entities.append(OctopusEnergyElectricityNextRate(hass, electricity_rate_coordinator, meter, point))
          entities.append(OctopusEnergyElectricityCurrentStandingCharge(hass, client, electricity_tariff_code, meter, point))

          previous_consumption_coordinator = await async_create_previous_consumption_and_rates_coordinator(
            hass,
            client,
            point["mpan"],
            meter["serial_number"],
            True,
            electricity_tariff_code,
            meter["is_smart_meter"]
          )
          entities.append(OctopusEnergyPreviousAccumulativeElectricityConsumption(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityConsumptionPeak(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityConsumptionOffPeak(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityCost(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityCostPeak(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityCostOffPeak(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityCostOverride(hass, previous_consumption_coordinator, client, electricity_tariff_code, meter, point))

          if meter["is_export"] == False and CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in config and config[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True:
            consumption_coordinator = await async_create_current_consumption_coordinator(hass, client, meter["device_id"], True)
            entities.append(OctopusEnergyCurrentElectricityConsumption(hass, consumption_coordinator, meter, point))
            entities.append(OctopusEnergyCurrentElectricityDemand(hass, consumption_coordinator, meter, point))
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
      if gas_tariff_code is not None:
        for meter in point["meters"]:
          _LOGGER.info(f'Adding gas meter; mprn: {point["mprn"]}; serial number: {meter["serial_number"]}')
          rate_coordinator = await async_create_gas_rate_coordinator(hass, client, gas_tariff_code)
          entities.append(OctopusEnergyGasCurrentRate(hass, rate_coordinator, gas_tariff_code, meter, point, gas_price_cap))
          entities.append(OctopusEnergyGasCurrentStandingCharge(hass, client, gas_tariff_code, meter, point))

          previous_consumption_coordinator = await async_create_previous_consumption_and_rates_coordinator(
            hass,
            client,
            point["mprn"],
            meter["serial_number"],
            False,
            gas_tariff_code,
            None
          )
          entities.append(OctopusEnergyPreviousAccumulativeGasConsumption(hass, previous_consumption_coordinator, gas_tariff_code, meter, point, calorific_value))
          entities.append(OctopusEnergyPreviousAccumulativeGasConsumptionKwh(hass, previous_consumption_coordinator, gas_tariff_code, meter, point, calorific_value))
          entities.append(OctopusEnergyPreviousAccumulativeGasCost(hass, previous_consumption_coordinator, gas_tariff_code, meter, point, calorific_value))
          entities.append(OctopusEnergyPreviousAccumulativeGasCostOverride(hass, previous_consumption_coordinator, client, gas_tariff_code, meter, point, calorific_value))

          if CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in config and config[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True:
            consumption_coordinator = await async_create_current_consumption_coordinator(hass, client, meter["device_id"], False)
            entities.append(OctopusEnergyCurrentGasConsumption(hass, consumption_coordinator, meter, point))
      else:
        for meter in point["meters"]:
          _LOGGER.info(f'Skipping gas meter due to no active agreement; mprn: {point["mprn"]}; serial number: {meter["serial_number"]}')
        _LOGGER.info(f'agreements: {point["agreements"]}')
  else:
    _LOGGER.info('No gas meters available')

  async_add_entities(entities, True)
