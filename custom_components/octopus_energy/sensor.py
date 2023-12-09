from custom_components.octopus_energy.coordinators.wheel_of_fortune import async_setup_wheel_of_fortune_spins_coordinator
import voluptuous as vol
import logging

from homeassistant.util.dt import (utcnow)
from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.helpers import entity_platform, issue_registry as ir

from .electricity.current_consumption import OctopusEnergyCurrentElectricityConsumption
from .electricity.current_accumulative_consumption import OctopusEnergyCurrentAccumulativeElectricityConsumption
from .electricity.current_accumulative_cost import OctopusEnergyCurrentAccumulativeElectricityCost
from .electricity.current_accumulative_consumption_off_peak import OctopusEnergyCurrentAccumulativeElectricityConsumptionOffPeak
from .electricity.current_accumulative_consumption_peak import OctopusEnergyCurrentAccumulativeElectricityConsumptionPeak
from .electricity.current_accumulative_cost_off_peak import OctopusEnergyCurrentAccumulativeElectricityCostOffPeak
from .electricity.current_accumulative_cost_peak import OctopusEnergyCurrentAccumulativeElectricityCostPeak
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
from .gas.next_rate import OctopusEnergyGasNextRate
from .gas.previous_rate import OctopusEnergyGasPreviousRate
from .gas.previous_accumulative_consumption import OctopusEnergyPreviousAccumulativeGasConsumption
from .gas.previous_accumulative_consumption_kwh import OctopusEnergyPreviousAccumulativeGasConsumptionKwh
from .gas.previous_accumulative_cost import OctopusEnergyPreviousAccumulativeGasCost
from .gas.current_consumption import OctopusEnergyCurrentGasConsumption
from .gas.current_accumulative_consumption import OctopusEnergyCurrentAccumulativeGasConsumption
from .gas.current_accumulative_cost import OctopusEnergyCurrentAccumulativeGasCost
from .gas.standing_charge import OctopusEnergyGasCurrentStandingCharge
from .gas.previous_accumulative_cost_override import OctopusEnergyPreviousAccumulativeGasCostOverride
from .wheel_of_fortune.electricity_spins import OctopusEnergyWheelOfFortuneElectricitySpins
from .wheel_of_fortune.gas_spins import OctopusEnergyWheelOfFortuneGasSpins

from .coordinators.current_consumption import async_create_current_consumption_coordinator
from .coordinators.gas_rates import async_setup_gas_rates_coordinator
from .coordinators.previous_consumption_and_rates import async_create_previous_consumption_and_rates_coordinator
from .coordinators.electricity_standing_charges import async_setup_electricity_standing_charges_coordinator
from .coordinators.gas_standing_charges import async_setup_gas_standing_charges_coordinator

from .octoplus.points import OctopusEnergyOctoplusPoints

from .utils import (get_active_tariff_code)
from .const import (
  CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_DEFAULT_PREVIOUS_CONSUMPTION_OFFSET_IN_DAYS,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET,
  CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET,
  DATA_ACCOUNT_ID,
  DATA_OCTOPLUS_SUPPORTED,
  DOMAIN,
  
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION,
  CONFIG_MAIN_CALORIFIC_VALUE,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,

  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DATA_SAVING_SESSIONS_COORDINATOR,
  DATA_CLIENT,
  DATA_ACCOUNT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_default_sensors(hass, entry, async_add_entities)

  platform = entity_platform.async_get_current_platform()
  platform.async_register_entity_service(
    "refresh_previous_consumption_data",
    vol.All(
      vol.Schema(
        {
          vol.Optional("start_time"): str,
        },
        extra=vol.ALLOW_EXTRA,
      ),
    ),
    "async_refresh_previous_consumption_data",
  )

  platform.async_register_entity_service(
    "spin_wheel_of_fortune",
    vol.All(
      vol.Schema(
        {},
        extra=vol.ALLOW_EXTRA,
      ),
    ),
    "async_spin_wheel",
    # supports_response=SupportsResponse.OPTIONAL
  )

async def async_setup_default_sensors(hass: HomeAssistant, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)
  
  client = hass.data[DOMAIN][DATA_CLIENT]

  saving_session_coordinator = hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR]
  await saving_session_coordinator.async_config_entry_first_refresh()
  
  account_result = hass.data[DOMAIN][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None
  account_id = hass.data[DOMAIN][DATA_ACCOUNT_ID]

  wheel_of_fortune_coordinator = await async_setup_wheel_of_fortune_spins_coordinator(hass, account_id)
  
  entities = [
    OctopusEnergyWheelOfFortuneElectricitySpins(hass, wheel_of_fortune_coordinator, client, account_id),
    OctopusEnergyWheelOfFortuneGasSpins(hass, wheel_of_fortune_coordinator, client, account_id)
  ]

  if hass.data[DOMAIN][DATA_OCTOPLUS_SUPPORTED]:
    entities.append(OctopusEnergyOctoplusPoints(hass, client, account_id))

  now = utcnow()

  if len(account_info["electricity_meter_points"]) > 0:
    electricity_price_cap = None
    if CONFIG_MAIN_ELECTRICITY_PRICE_CAP in config:
      electricity_price_cap = config[CONFIG_MAIN_ELECTRICITY_PRICE_CAP]

    previous_electricity_consumption_days_offset = CONFIG_DEFAULT_PREVIOUS_CONSUMPTION_OFFSET_IN_DAYS
    if CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET in config:
      previous_electricity_consumption_days_offset = config[CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET]

    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      electricity_tariff_code = get_active_tariff_code(now, point["agreements"])
      if electricity_tariff_code is not None:
        for meter in point["meters"]:
          mpan = point["mpan"]
          serial_number = meter["serial_number"]
          
          _LOGGER.info(f'Adding electricity meter; mpan: {mpan}; serial number: {serial_number}')

          electricity_rate_coordinator = hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number)]
          electricity_standing_charges_coordinator = await async_setup_electricity_standing_charges_coordinator(hass, mpan, serial_number)

          entities.append(OctopusEnergyElectricityCurrentRate(hass, electricity_rate_coordinator, meter, point, electricity_tariff_code, electricity_price_cap))
          entities.append(OctopusEnergyElectricityPreviousRate(hass, electricity_rate_coordinator, meter, point))
          entities.append(OctopusEnergyElectricityNextRate(hass, electricity_rate_coordinator, meter, point))
          entities.append(OctopusEnergyElectricityCurrentStandingCharge(hass, electricity_standing_charges_coordinator, electricity_tariff_code, meter, point))

          previous_consumption_coordinator = await async_create_previous_consumption_and_rates_coordinator(
            hass,
            client,
            mpan,
            serial_number,
            True,
            electricity_tariff_code,
            meter["is_smart_meter"],
            previous_electricity_consumption_days_offset
          )
          entities.append(OctopusEnergyPreviousAccumulativeElectricityConsumption(hass, client, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityConsumptionPeak(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityConsumptionOffPeak(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityCost(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityCostPeak(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityCostOffPeak(hass, previous_consumption_coordinator, electricity_tariff_code, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityCostOverride(hass, previous_consumption_coordinator, client, electricity_tariff_code, meter, point))

          if meter["is_export"] == False and CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in config and config[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True:
            live_consumption_refresh_in_minutes = CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES
            if CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES in config:
              live_consumption_refresh_in_minutes = config[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES]

            if meter["device_id"] is not None and meter["device_id"] != "":
              consumption_coordinator = await async_create_current_consumption_coordinator(hass, client, meter["device_id"], live_consumption_refresh_in_minutes)
              entities.append(OctopusEnergyCurrentElectricityConsumption(hass, consumption_coordinator, meter, point))
              entities.append(OctopusEnergyCurrentAccumulativeElectricityConsumption(hass, consumption_coordinator, electricity_rate_coordinator, electricity_standing_charges_coordinator, electricity_tariff_code, meter, point))
              entities.append(OctopusEnergyCurrentAccumulativeElectricityConsumptionPeak(hass, consumption_coordinator, electricity_rate_coordinator, electricity_standing_charges_coordinator, electricity_tariff_code, meter, point))
              entities.append(OctopusEnergyCurrentAccumulativeElectricityConsumptionOffPeak(hass, consumption_coordinator, electricity_rate_coordinator, electricity_standing_charges_coordinator, electricity_tariff_code, meter, point))
              entities.append(OctopusEnergyCurrentAccumulativeElectricityCost(hass, consumption_coordinator, electricity_rate_coordinator, electricity_standing_charges_coordinator, electricity_tariff_code, meter, point))
              entities.append(OctopusEnergyCurrentAccumulativeElectricityCostPeak(hass, consumption_coordinator, electricity_rate_coordinator, electricity_standing_charges_coordinator, electricity_tariff_code, meter, point))
              entities.append(OctopusEnergyCurrentAccumulativeElectricityCostOffPeak(hass, consumption_coordinator, electricity_rate_coordinator, electricity_standing_charges_coordinator, electricity_tariff_code, meter, point))
              entities.append(OctopusEnergyCurrentElectricityDemand(hass, consumption_coordinator, meter, point))

              ir.async_delete_issue(hass, DOMAIN, f"octopus_mini_not_valid_electricity_{mpan}_{serial_number}")
            else:
              ir.async_create_issue(
                hass,
                DOMAIN,
                f"octopus_mini_not_valid_electricity_{mpan}_{serial_number}",
                is_fixable=False,
                severity=ir.IssueSeverity.ERROR,
                learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/octopus_mini_not_valid",
                translation_key="octopus_mini_not_valid",
                translation_placeholders={ "type": "electricity", "account_id": account_id, "mpan_mprn": mpan, "serial_number": serial_number },
              )
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
    
    previous_gas_consumption_days_offset = CONFIG_DEFAULT_PREVIOUS_CONSUMPTION_OFFSET_IN_DAYS
    if CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET in config:
      previous_gas_consumption_days_offset = config[CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET]

    for point in account_info["gas_meter_points"]:
      # We only care about points that have active agreements
      gas_tariff_code = get_active_tariff_code(now, point["agreements"])
      if gas_tariff_code is not None:
        for meter in point["meters"]:
          mprn = point["mprn"]
          serial_number = meter["serial_number"]
          
          _LOGGER.info(f'Adding gas meter; mprn: {mprn}; serial number: {serial_number}')

          gas_rate_coordinator = await async_setup_gas_rates_coordinator(hass, client, mprn, serial_number)
          gas_standing_charges_coordinator = await async_setup_gas_standing_charges_coordinator(hass, mprn, serial_number)

          entities.append(OctopusEnergyGasCurrentRate(hass, gas_rate_coordinator, gas_tariff_code, meter, point, gas_price_cap))
          entities.append(OctopusEnergyGasPreviousRate(hass, gas_rate_coordinator, meter, point))
          entities.append(OctopusEnergyGasNextRate(hass, gas_rate_coordinator, meter, point))
          entities.append(OctopusEnergyGasCurrentStandingCharge(hass, gas_standing_charges_coordinator, gas_tariff_code, meter, point))

          previous_consumption_coordinator = await async_create_previous_consumption_and_rates_coordinator(
            hass,
            client,
            mprn,
            serial_number,
            False,
            gas_tariff_code,
            None,
            previous_gas_consumption_days_offset
          )
          entities.append(OctopusEnergyPreviousAccumulativeGasConsumption(hass, client, previous_consumption_coordinator, gas_tariff_code, meter, point, calorific_value))
          entities.append(OctopusEnergyPreviousAccumulativeGasConsumptionKwh(hass, previous_consumption_coordinator, gas_tariff_code, meter, point, calorific_value))
          entities.append(OctopusEnergyPreviousAccumulativeGasCost(hass, previous_consumption_coordinator, gas_tariff_code, meter, point, calorific_value))
          entities.append(OctopusEnergyPreviousAccumulativeGasCostOverride(hass, previous_consumption_coordinator, client, gas_tariff_code, meter, point, calorific_value))

          if CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in config and config[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True:
            live_consumption_refresh_in_minutes = CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES
            if CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES in config:
              live_consumption_refresh_in_minutes = config[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES]
            
            if meter["device_id"] is not None and meter["device_id"] != "":
              consumption_coordinator = await async_create_current_consumption_coordinator(hass, client, meter["device_id"], live_consumption_refresh_in_minutes)
              entities.append(OctopusEnergyCurrentGasConsumption(hass, consumption_coordinator, meter, point))
              entities.append(OctopusEnergyCurrentAccumulativeGasConsumption(hass, consumption_coordinator, gas_rate_coordinator, gas_standing_charges_coordinator, gas_tariff_code, meter, point, calorific_value))
              entities.append(OctopusEnergyCurrentAccumulativeGasCost(hass, consumption_coordinator, gas_rate_coordinator, gas_standing_charges_coordinator, gas_tariff_code, meter, point, calorific_value))
              
              ir.async_delete_issue(hass, DOMAIN, f"octopus_mini_not_valid_gas_{mprn}_{serial_number}")
            else:
              ir.async_create_issue(
                hass,
                DOMAIN,
                f"octopus_mini_not_valid_gas_{mprn}_{serial_number}",
                is_fixable=False,
                severity=ir.IssueSeverity.ERROR,
                learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/octopus_mini_not_valid",
                translation_key="octopus_mini_not_valid",
                translation_placeholders={ "type": "gas", "account_id": account_id, "mpan_mprn": mprn, "serial_number": serial_number },
              )
      else:
        for meter in point["meters"]:
          _LOGGER.info(f'Skipping gas meter due to no active agreement; mprn: {point["mprn"]}; serial number: {meter["serial_number"]}')
        _LOGGER.info(f'agreements: {point["agreements"]}')
  else:
    _LOGGER.info('No gas meters available')

  async_add_entities(entities, True)
