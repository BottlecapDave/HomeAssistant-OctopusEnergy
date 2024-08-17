from datetime import timedelta
import voluptuous as vol
import logging

from homeassistant.util.dt import (utcnow, now)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform, issue_registry as ir, entity_registry as er
import homeassistant.helpers.config_validation as cv

from .electricity.current_consumption import OctopusEnergyCurrentElectricityConsumption
from .electricity.current_accumulative_consumption import OctopusEnergyCurrentAccumulativeElectricityConsumption
from .electricity.current_accumulative_cost import OctopusEnergyCurrentAccumulativeElectricityCost
from .electricity.current_demand import OctopusEnergyCurrentElectricityDemand
from .electricity.current_rate import OctopusEnergyElectricityCurrentRate
from .electricity.next_rate import OctopusEnergyElectricityNextRate
from .electricity.previous_accumulative_consumption import OctopusEnergyPreviousAccumulativeElectricityConsumption
from .electricity.previous_accumulative_cost import OctopusEnergyPreviousAccumulativeElectricityCost
from .electricity.previous_rate import OctopusEnergyElectricityPreviousRate
from .electricity.standing_charge import OctopusEnergyElectricityCurrentStandingCharge
from .electricity.previous_accumulative_cost_override import OctopusEnergyPreviousAccumulativeElectricityCostOverride
from .electricity.rates_previous_consumption_override import OctopusEnergyElectricityPreviousConsumptionOverrideRates
from .electricity.current_total_consumption import OctopusEnergyCurrentTotalElectricityConsumption
from .gas.current_rate import OctopusEnergyGasCurrentRate
from .gas.next_rate import OctopusEnergyGasNextRate
from .gas.previous_rate import OctopusEnergyGasPreviousRate
from .gas.previous_accumulative_consumption_cubic_meters import OctopusEnergyPreviousAccumulativeGasConsumptionCubicMeters
from .gas.previous_accumulative_consumption_kwh import OctopusEnergyPreviousAccumulativeGasConsumptionKwh
from .gas.previous_accumulative_cost import OctopusEnergyPreviousAccumulativeGasCost
from .gas.current_consumption import OctopusEnergyCurrentGasConsumption
from .gas.current_accumulative_consumption_kwh import OctopusEnergyCurrentAccumulativeGasConsumptionKwh
from .gas.current_accumulative_consumption_cubic_meters import OctopusEnergyCurrentAccumulativeGasConsumptionCubicMeters
from .gas.current_accumulative_cost import OctopusEnergyCurrentAccumulativeGasCost
from .gas.standing_charge import OctopusEnergyGasCurrentStandingCharge
from .gas.previous_accumulative_cost_override import OctopusEnergyPreviousAccumulativeGasCostOverride
from .gas.rates_previous_consumption_override import OctopusEnergyGasPreviousConsumptionOverrideRates
from .gas.current_total_consumption_cubic_meters import OctopusEnergyCurrentTotalGasConsumptionCubicMeters
from .gas.current_total_consumption_kwh import OctopusEnergyCurrentTotalGasConsumptionKwh
from .wheel_of_fortune.electricity_spins import OctopusEnergyWheelOfFortuneElectricitySpins
from .wheel_of_fortune.gas_spins import OctopusEnergyWheelOfFortuneGasSpins
from .cost_tracker.cost_tracker import OctopusEnergyCostTrackerSensor
from .cost_tracker.cost_tracker_week import OctopusEnergyCostTrackerWeekSensor
from .cost_tracker.cost_tracker_month import OctopusEnergyCostTrackerMonthSensor
from .greenness_forecast.current_index import OctopusEnergyGreennessForecastCurrentIndex
from .greenness_forecast.next_index import OctopusEnergyGreennessForecastNextIndex

from .coordinators.current_consumption import async_create_current_consumption_coordinator
from .coordinators.gas_rates import async_setup_gas_rates_coordinator
from .coordinators.previous_consumption_and_rates import async_create_previous_consumption_and_rates_coordinator
from .coordinators.electricity_standing_charges import async_setup_electricity_standing_charges_coordinator
from .coordinators.gas_standing_charges import async_setup_gas_standing_charges_coordinator
from .coordinators.wheel_of_fortune import async_setup_wheel_of_fortune_spins_coordinator
from .coordinators.current_consumption_home_pro import async_create_home_pro_current_consumption_coordinator

from .api_client import OctopusEnergyApiClient
from .utils.tariff_overrides import async_get_tariff_override
from .utils.tariff_cache import async_get_cached_tariff_total_unique_rates, async_save_cached_tariff_total_unique_rates
from .utils.rate_information import get_peak_type, get_unique_rates, has_peak_rates

from .octoplus.points import OctopusEnergyOctoplusPoints

from .utils import (Tariff, get_active_tariff)
from .const import (
  CONFIG_COST_TRACKER_MPAN,
  CONFIG_ACCOUNT_ID,
  CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_DEFAULT_PREVIOUS_CONSUMPTION_OFFSET_IN_DAYS,
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_COST_TRACKER,
  CONFIG_KIND_TARIFF_COMPARISON,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_PREVIOUS_ELECTRICITY_CONSUMPTION_DAYS_OFFSET,
  CONFIG_MAIN_PREVIOUS_GAS_CONSUMPTION_DAYS_OFFSET,
  CONFIG_TARIFF_COMPARISON_MPAN_MPRN,
  DATA_GREENNESS_FORECAST_COORDINATOR,
  DATA_HOME_PRO_CLIENT,
  DATA_PREVIOUS_CONSUMPTION_COORDINATOR_KEY,
  DEFAULT_CALORIFIC_VALUE,
  DOMAIN,
  
  CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION,
  CONFIG_MAIN_CALORIFIC_VALUE,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,

  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DATA_CLIENT,
  DATA_ACCOUNT
)

_LOGGER = logging.getLogger(__name__)

async def get_unique_electricity_rates(hass, client: OctopusEnergyApiClient, tariff: Tariff):
  total_unique_rates = await async_get_cached_tariff_total_unique_rates(hass, tariff.code)
  if total_unique_rates is None:
    _LOGGER.info(f"Retrieving electricity rates '{tariff.code}' to determine number of unique rates")

    current_date = now()
    # Look at yesterdays rates so we have a complete picture
    period_from = current_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    period_to = period_from + timedelta(days=1)
    rates = await client.async_get_electricity_rates(tariff.product, tariff.code, True, period_from, period_to)
    if rates is None:
      raise Exception(f"Failed to retrieve rates for tariff '{tariff.code}'")
    
    total_unique_rates = len(get_unique_rates(current_date - timedelta(days=1), rates))
    if total_unique_rates < 1:
      raise Exception(f"Unique rates for tariff '{tariff.code}' is less than 1")

    await async_save_cached_tariff_total_unique_rates(hass, tariff.code, total_unique_rates)

  return total_unique_rates

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  if config[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
    await async_setup_default_sensors(hass, config, async_add_entities)

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
      "async_refresh_previous_consumption_data"
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

    account_id = config[CONFIG_ACCOUNT_ID]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
    if account_info["octoplus_enrolled"] == True:
      platform.async_register_entity_service(
        "redeem_octoplus_points_into_account_credit",
        vol.All(
          vol.Schema(
            {
              vol.Required("points_to_redeem"): cv.positive_int,
            },
            extra=vol.ALLOW_EXTRA,
          ),
        ),
        "async_redeem_points_into_account_credit",
        # supports_response=SupportsResponse.OPTIONAL
      )
  elif config[CONFIG_KIND] == CONFIG_KIND_COST_TRACKER:
    await async_setup_cost_sensors(hass, entry, config, async_add_entities)

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
      "update_cost_tracker",
      vol.All(
        vol.Schema(
          {
            vol.Required("is_tracking_enabled"): bool,
          },
          extra=vol.ALLOW_EXTRA,
        ),
      ),
      "async_update_cost_tracker_config"
    )

    platform.async_register_entity_service(
      "reset_cost_tracker",
      vol.All(
        vol.Schema(
          {},
          extra=vol.ALLOW_EXTRA,
        ),
      ),
      "async_reset_cost_tracker"
    )

    platform.async_register_entity_service(
      "adjust_accumulative_cost_tracker",
      vol.All(
        vol.Schema(
          {
            vol.Required("date"): cv.date,
            vol.Required("consumption"): cv.positive_float,
            vol.Required("cost"): cv.positive_float,
          },
          extra=vol.ALLOW_EXTRA,
        ),
      ),
      "async_adjust_accumulative_cost_tracker"
    )

    platform.async_register_entity_service(
      "adjust_cost_tracker",
      vol.All(
        vol.Schema(
          {
            vol.Required("datetime"): cv.datetime,
            vol.Required("consumption"): cv.positive_float,
          },
          extra=vol.ALLOW_EXTRA,
        ),
      ),
      "async_adjust_cost_tracker"
    )

  elif config[CONFIG_KIND] == CONFIG_KIND_TARIFF_COMPARISON:
    await async_setup_tariff_comparison_sensors(hass, entry, config, async_add_entities)

async def async_setup_default_sensors(hass: HomeAssistant, config, async_add_entities):
  account_id = config[CONFIG_ACCOUNT_ID]
  
  client = hass.data[DOMAIN][account_id][DATA_CLIENT]
  home_pro_client = hass.data[DOMAIN][account_id][DATA_HOME_PRO_CLIENT] if DATA_HOME_PRO_CLIENT in hass.data[DOMAIN][account_id] else None
  
  account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None

  wheel_of_fortune_coordinator = await async_setup_wheel_of_fortune_spins_coordinator(hass, account_id)
  greenness_forecast_coordinator = hass.data[DOMAIN][account_id][DATA_GREENNESS_FORECAST_COORDINATOR]
  
  entities = [
    OctopusEnergyWheelOfFortuneElectricitySpins(hass, wheel_of_fortune_coordinator, client, account_id),
    OctopusEnergyWheelOfFortuneGasSpins(hass, wheel_of_fortune_coordinator, client, account_id),
    OctopusEnergyGreennessForecastCurrentIndex(hass, greenness_forecast_coordinator, account_id),
    OctopusEnergyGreennessForecastNextIndex(hass, greenness_forecast_coordinator, account_id)
  ]

  entity_ids_to_migrate = []

  if account_info["octoplus_enrolled"] == True:
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
      electricity_tariff = get_active_tariff(now, point["agreements"])
      if electricity_tariff is not None:
        for meter in point["meters"]:
          mpan = point["mpan"]
          serial_number = meter["serial_number"]
          
          _LOGGER.info(f'Adding electricity meter; mpan: {mpan}; serial number: {serial_number}')

          electricity_rate_coordinator = hass.data[DOMAIN][account_id][DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number)]
          electricity_standing_charges_coordinator = await async_setup_electricity_standing_charges_coordinator(hass, account_id, mpan, serial_number)

          entities.append(OctopusEnergyElectricityCurrentRate(hass, electricity_rate_coordinator, meter, point, electricity_price_cap))
          entities.append(OctopusEnergyElectricityPreviousRate(hass, electricity_rate_coordinator, meter, point))
          entities.append(OctopusEnergyElectricityNextRate(hass, electricity_rate_coordinator, meter, point))
          entities.append(OctopusEnergyElectricityCurrentStandingCharge(hass, electricity_standing_charges_coordinator, meter, point))

          tariff_override = await async_get_tariff_override(hass, mpan, serial_number)
          previous_consumption_coordinator = await async_create_previous_consumption_and_rates_coordinator(
            hass,
            account_id,
            client,
            mpan,
            serial_number,
            True,
            meter["is_smart_meter"],
            previous_electricity_consumption_days_offset,
            tariff_override
          )
          entities.append(OctopusEnergyPreviousAccumulativeElectricityConsumption(hass, client, previous_consumption_coordinator, account_id, meter, point))
          entities.append(OctopusEnergyPreviousAccumulativeElectricityCost(hass, previous_consumption_coordinator, meter, point))
          
          # Create a peak override for each available peak type for our tariff
          total_unique_rates = await get_unique_electricity_rates(hass, client, electricity_tariff if tariff_override is None else tariff_override)
          for unique_rate_index in range(0, total_unique_rates):
            peak_type = get_peak_type(total_unique_rates, unique_rate_index)
            if peak_type is not None:
              entities.append(OctopusEnergyPreviousAccumulativeElectricityConsumption(hass, client, previous_consumption_coordinator, account_id, meter, point, peak_type))
              entities.append(OctopusEnergyPreviousAccumulativeElectricityCost(hass, previous_consumption_coordinator, meter, point, peak_type))

          if meter["is_export"] == False:
            if home_pro_client is not None:
              home_pro_consumption_coordinator = await async_create_home_pro_current_consumption_coordinator(hass, account_id, home_pro_client, True)
              entities.append(OctopusEnergyCurrentElectricityDemand(hass, home_pro_consumption_coordinator, meter, point))
              entities.append(OctopusEnergyCurrentTotalElectricityConsumption(hass, home_pro_consumption_coordinator, meter, point))
             
            if (CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in config and config[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True):
              live_consumption_refresh_in_minutes = CONFIG_DEFAULT_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES
              if CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES in config:
                live_consumption_refresh_in_minutes = config[CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES]
  
              if meter["device_id"] is not None and meter["device_id"] != "":
                consumption_coordinator = await async_create_current_consumption_coordinator(hass, account_id, client, meter["device_id"], live_consumption_refresh_in_minutes)
                entities.append(OctopusEnergyCurrentElectricityConsumption(hass, consumption_coordinator, meter, point))
                entities.append(OctopusEnergyCurrentAccumulativeElectricityConsumption(hass, consumption_coordinator, electricity_rate_coordinator, electricity_standing_charges_coordinator, meter, point))
                entities.append(OctopusEnergyCurrentAccumulativeElectricityCost(hass, consumption_coordinator, electricity_rate_coordinator, electricity_standing_charges_coordinator, meter, point))
                
                if home_pro_client is None:
                  entities.append(OctopusEnergyCurrentElectricityDemand(hass, consumption_coordinator, meter, point))
                  entities.append(OctopusEnergyCurrentTotalElectricityConsumption(hass, consumption_coordinator, meter, point))

                # Create a peak override for each available peak type for our tariff
                for unique_rate_index in range(0, total_unique_rates):
                  peak_type = get_peak_type(total_unique_rates, unique_rate_index)
                  if peak_type is not None:
                    entities.append(OctopusEnergyCurrentAccumulativeElectricityConsumption(hass, consumption_coordinator, electricity_rate_coordinator, electricity_standing_charges_coordinator, meter, point, peak_type))
                    entities.append(OctopusEnergyCurrentAccumulativeElectricityCost(hass, consumption_coordinator, electricity_rate_coordinator, electricity_standing_charges_coordinator, meter, point, peak_type))

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

    calorific_value = DEFAULT_CALORIFIC_VALUE
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
      gas_tariff = get_active_tariff(now, point["agreements"])
      if gas_tariff is not None:
        for meter in point["meters"]:
          mprn = point["mprn"]
          serial_number = meter["serial_number"]
          
          _LOGGER.info(f'Adding gas meter; mprn: {mprn}; serial number: {serial_number}')

          gas_rate_coordinator = await async_setup_gas_rates_coordinator(hass, account_id, client, mprn, serial_number)
          gas_standing_charges_coordinator = await async_setup_gas_standing_charges_coordinator(hass, account_id, mprn, serial_number)

          entities.append(OctopusEnergyGasCurrentRate(hass, gas_rate_coordinator, meter, point, gas_price_cap))
          entities.append(OctopusEnergyGasPreviousRate(hass, gas_rate_coordinator, meter, point))
          entities.append(OctopusEnergyGasNextRate(hass, gas_rate_coordinator, meter, point))
          entities.append(OctopusEnergyGasCurrentStandingCharge(hass, gas_standing_charges_coordinator, meter, point))

          tariff_override = await async_get_tariff_override(hass, mprn, serial_number)
          previous_consumption_coordinator = await async_create_previous_consumption_and_rates_coordinator(
            hass,
            account_id,
            client,
            mprn,
            serial_number,
            False,
            None,
            previous_gas_consumption_days_offset,
            tariff_override
          )
          entities.append(OctopusEnergyPreviousAccumulativeGasConsumptionCubicMeters(hass, client, previous_consumption_coordinator, account_id, meter, point, calorific_value))
          entities.append(OctopusEnergyPreviousAccumulativeGasConsumptionKwh(hass, previous_consumption_coordinator, meter, point, calorific_value))
          entities.append(OctopusEnergyPreviousAccumulativeGasCost(hass, previous_consumption_coordinator, meter, point, calorific_value))

          entity_ids_to_migrate.append({
            "old": f"octopus_energy_gas_{serial_number}_{mprn}_previous_accumulative_consumption",
            "new": f"octopus_energy_gas_{serial_number}_{mprn}_previous_accumulative_consumption_m3"
          })

          if home_pro_client is not None:
            home_pro_consumption_coordinator = await async_create_home_pro_current_consumption_coordinator(hass, account_id, home_pro_client, False)
            entities.append(OctopusEnergyCurrentTotalGasConsumptionKwh(hass, home_pro_consumption_coordinator, meter, point, calorific_value))
            entities.append(OctopusEnergyCurrentTotalGasConsumptionCubicMeters(hass, home_pro_consumption_coordinator, meter, point, calorific_value))

          if (CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION in config and config[CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION] == True):
            live_consumption_refresh_in_minutes = CONFIG_DEFAULT_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES
            if CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES in config:
              live_consumption_refresh_in_minutes = config[CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES]
            
            if meter["device_id"] is not None and meter["device_id"] != "":
              consumption_coordinator = await async_create_current_consumption_coordinator(hass, account_id, client, meter["device_id"], live_consumption_refresh_in_minutes)
              entities.append(OctopusEnergyCurrentGasConsumption(hass, consumption_coordinator, meter, point))
              entities.append(OctopusEnergyCurrentAccumulativeGasConsumptionKwh(hass, consumption_coordinator, gas_rate_coordinator, gas_standing_charges_coordinator, meter, point, calorific_value))
              entities.append(OctopusEnergyCurrentAccumulativeGasConsumptionCubicMeters(hass, consumption_coordinator, gas_rate_coordinator, gas_standing_charges_coordinator, meter, point, calorific_value))
              entities.append(OctopusEnergyCurrentAccumulativeGasCost(hass, consumption_coordinator, gas_rate_coordinator, gas_standing_charges_coordinator, meter, point, calorific_value))

              if home_pro_client is None:
                entities.append(OctopusEnergyCurrentTotalGasConsumptionKwh(hass, consumption_coordinator, meter, point, calorific_value))
                entities.append(OctopusEnergyCurrentTotalGasConsumptionCubicMeters(hass, consumption_coordinator, meter, point, calorific_value))

              entity_ids_to_migrate.append({
                "old": f"octopus_energy_gas_{serial_number}_{mprn}_current_accumulative_consumption",
                "new": f"octopus_energy_gas_{serial_number}_{mprn}_current_accumulative_consumption_kwh"
              })

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

  # Migrate entity ids that might have changed
  # for item in entity_ids_to_migrate:
  #   entity_id = registry.async_get_entity_id("sensor", DOMAIN, item["old"])
  #   if entity_id is not None:
  #     try:
  #       _LOGGER.info(f'Migrating entity id and unique id for {item["old"]} to {item["new"]}')
  #       registry.async_update_entity(entity_id, new_entity_id=f'sensor.{item["new"]}'.lower(), new_unique_id=item["new"])
  #     except Exception as e:
  #       _LOGGER.warning(f'Failed to migrate entity id and unique id for {item["old"]} to {item["new"]} - {e}')

  async_add_entities(entities)

async def async_setup_cost_sensors(hass: HomeAssistant, entry, config, async_add_entities):
  account_id = config[CONFIG_ACCOUNT_ID]
  account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None
  client = hass.data[DOMAIN][account_id][DATA_CLIENT]

  mpan = config[CONFIG_COST_TRACKER_MPAN]

  registry = er.async_get(hass)

  now = utcnow()
  for point in account_info["electricity_meter_points"]:
    tariff = get_active_tariff(now, point["agreements"])
    if tariff is not None:
      # For backwards compatibility, pick the first applicable meter
      if point["mpan"] == mpan or mpan is None:
        for meter in point["meters"]:
          serial_number = meter["serial_number"]
          coordinator = hass.data[DOMAIN][account_id][DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number)]

          sensor = OctopusEnergyCostTrackerSensor(hass, coordinator, config)
          sensor_entity_id = registry.async_get_entity_id("sensor", DOMAIN, sensor.unique_id)

          entities = [
            sensor,
            OctopusEnergyCostTrackerWeekSensor(hass, entry, config, sensor_entity_id if sensor_entity_id is not None else sensor.entity_id),
            OctopusEnergyCostTrackerMonthSensor(hass, entry, config, sensor_entity_id if sensor_entity_id is not None else sensor.entity_id),
          ]
          
          tariff_override = await async_get_tariff_override(hass, mpan, serial_number)
          total_unique_rates = await get_unique_electricity_rates(hass, client, tariff if tariff_override is None else tariff_override)
          if has_peak_rates(total_unique_rates):
            for unique_rate_index in range(0, total_unique_rates):
              peak_type = get_peak_type(total_unique_rates, unique_rate_index)
              if peak_type is not None:
                peak_sensor = OctopusEnergyCostTrackerSensor(hass, coordinator, config, peak_type)
                peak_sensor_entity_id = registry.async_get_entity_id("sensor", DOMAIN, peak_sensor.unique_id)
                
                entities.append(peak_sensor)
                entities.append(OctopusEnergyCostTrackerWeekSensor(hass, entry, config, peak_sensor_entity_id if peak_sensor_entity_id is not None else f"sensor.{peak_sensor.unique_id}", peak_type))
                entities.append(OctopusEnergyCostTrackerMonthSensor(hass, entry, config, peak_sensor_entity_id if peak_sensor_entity_id is not None else f"sensor.{peak_sensor.unique_id}", peak_type))

          async_add_entities(entities)
          break

async def async_setup_tariff_comparison_sensors(hass: HomeAssistant, entry, config, async_add_entities):
  account_id = config[CONFIG_ACCOUNT_ID]
  account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None
  client = hass.data[DOMAIN][account_id][DATA_CLIENT]

  mpan_mprn = config[CONFIG_TARIFF_COMPARISON_MPAN_MPRN]

  calorific_value = DEFAULT_CALORIFIC_VALUE
  config_entries = hass.config_entries.async_entries(DOMAIN)
  for entry in config_entries:
    if entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT and entry.data[CONFIG_ACCOUNT_ID] == account_id and CONFIG_MAIN_CALORIFIC_VALUE in config:
      calorific_value = config[CONFIG_MAIN_CALORIFIC_VALUE]

  now = utcnow()
  for point in account_info["electricity_meter_points"]:
    tariff = get_active_tariff(now, point["agreements"])
    if tariff is not None:
      if point["mpan"] == mpan_mprn:
        for meter in point["meters"]:
          serial_number = meter["serial_number"]
          coordinator = hass.data[DOMAIN][account_id][DATA_PREVIOUS_CONSUMPTION_COORDINATOR_KEY.format(mpan_mprn, serial_number)]
          entities = [
            OctopusEnergyPreviousAccumulativeElectricityCostOverride(hass, account_id, coordinator, client, meter, point, config),
            OctopusEnergyElectricityPreviousConsumptionOverrideRates(hass, meter, point, config)
          ]
          
          async_add_entities(entities)
          break

  now = utcnow()
  for point in account_info["gas_meter_points"]:
    tariff = get_active_tariff(now, point["agreements"])
    if tariff is not None:
      if point["mprn"] == mpan_mprn:
        for meter in point["meters"]:
          serial_number = meter["serial_number"]
          coordinator = hass.data[DOMAIN][account_id][DATA_PREVIOUS_CONSUMPTION_COORDINATOR_KEY.format(mpan_mprn, serial_number)]
          entities = [
            OctopusEnergyPreviousAccumulativeGasCostOverride(hass, account_id, coordinator, client, meter, point, calorific_value, config),
            OctopusEnergyGasPreviousConsumptionOverrideRates(hass, meter, point, config)
          ]
          
          async_add_entities(entities)
          break
