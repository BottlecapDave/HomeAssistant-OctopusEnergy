import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.helpers import config_validation as cv, entity_platform, issue_registry as ir
from homeassistant.util.dt import (utcnow)
import homeassistant.helpers.config_validation as cv

from .electricity.off_peak import OctopusEnergyElectricityOffPeak
from .octoplus.saving_sessions import OctopusEnergySavingSessions
from .target_rates.target_rate import OctopusEnergyTargetRate
from .intelligent.dispatching import OctopusEnergyIntelligentDispatching
from .greenness_forecast.highlighted import OctopusEnergyGreennessForecastHighlighted
from .utils import get_active_tariff
from .api_client.intelligent_device import IntelligentDevice
from .target_rates.rolling_target_rate import OctopusEnergyRollingTargetRate
from .octoplus.free_electricity_sessions import OctopusEnergyFreeElectricitySessions
from .coordinators.intelligent_device import IntelligentDeviceCoordinatorResult
from .api_client.heat_pump import HeatPumpResponse
from .heat_pump import get_mock_heat_pump_id
from .heat_pump.weather_compensation_enabled import OctopusEnergyHeatPumpWeatherCompensationEnabled
from .utils.debug_overrides import async_get_account_debug_override

from .const import (
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_ROLLING_TARGET_RATE,
  CONFIG_KIND_TARGET_RATE,
  CONFIG_ACCOUNT_ID,
  CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES,
  CONFIG_MAIN_INTELLIGENT_RATE_MODE,
  CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES,
  CONFIG_MAIN_INTELLIGENT_SETTINGS,
  DATA_FREE_ELECTRICITY_SESSIONS_COORDINATOR,
  DATA_GREENNESS_FORECAST_COORDINATOR,
  DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR,
  DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY,
  DATA_INTELLIGENT_DEVICES,
  DATA_INTELLIGENT_DISPATCHES_COORDINATOR,
  DOMAIN,

  CONFIG_TARGET_MPAN,

  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DATA_SAVING_SESSIONS_COORDINATOR,
  DATA_ACCOUNT,
  INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS,
  INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES,
  REPAIR_FREE_ELECTRICITY_SESSION_BINARY_SENSOR_DEPRECATED,
  REPAIR_GREENNESS_FORECAST_BINARY_SENSOR_DEPRECATED,
  REPAIR_SAVING_SESSION_BINARY_SENSOR_DEPRECATED,
  REPAIR_TARGET_RATE_REMOVAL_PROPOSAL
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
    await async_setup_main_sensors(hass, entry, async_add_entities)
  elif entry.data[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE or entry.data[CONFIG_KIND] == CONFIG_KIND_ROLLING_TARGET_RATE:
    await async_setup_target_sensors(hass, entry, async_add_entities)

    ir.async_create_issue(
      hass,
      DOMAIN,
      REPAIR_TARGET_RATE_REMOVAL_PROPOSAL,
      is_fixable=False,
      severity=ir.IssueSeverity.WARNING,
      learn_more_url="https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions/1305",
      translation_key="target_rate_removal_proposal",
    )

    platform = entity_platform.async_get_current_platform()

    if entry.data[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE:
      platform.async_register_entity_service(
        "update_target_config",
        vol.All(
          cv.make_entity_service_schema(
            {
              vol.Optional("target_hours"): str,
              vol.Optional("target_start_time"): str,
              vol.Optional("target_end_time"): str,
              vol.Optional("target_offset"): str,
              vol.Optional("target_minimum_rate"): str,
              vol.Optional("target_maximum_rate"): str,
              vol.Optional("target_weighting"): str,
              vol.Optional("persist_changes"): bool,
            },
            extra=vol.ALLOW_EXTRA,
          ),
          cv.has_at_least_one_key(
            "target_hours", "target_start_time", "target_end_time", "target_offset", "target_minimum_rate", "target_maximum_rate"
          ),
        ),
        "async_update_target_rate_config",
      )
    else:
      platform.async_register_entity_service(
        "update_rolling_target_config",
        vol.All(
          cv.make_entity_service_schema(
            {
              vol.Optional("target_hours"): str,
              vol.Optional("target_look_ahead_hours"): str,
              vol.Optional("target_offset"): str,
              vol.Optional("target_minimum_rate"): str,
              vol.Optional("target_maximum_rate"): str,
              vol.Optional("target_weighting"): str,
              vol.Optional("persist_changes"): bool,
            },
            extra=vol.ALLOW_EXTRA,
          ),
          cv.has_at_least_one_key(
            "target_hours", "target_look_ahead_hours", "target_offset", "target_minimum_rate", "target_maximum_rate"
          ),
        ),
        "async_update_rolling_target_rate_config",
      )

  return True

async def async_setup_main_sensors(hass, entry, async_add_entities):
  _LOGGER.debug('Setting up main sensors')
  config = dict(entry.data)

  account_id = config[CONFIG_ACCOUNT_ID]
  account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None
  octoplus_enrolled = account_info is not None and account_info["octoplus_enrolled"] == True

  saving_session_coordinator = hass.data[DOMAIN][account_id][DATA_SAVING_SESSIONS_COORDINATOR]
  greenness_forecast_coordinator = hass.data[DOMAIN][account_id][DATA_GREENNESS_FORECAST_COORDINATOR]
  free_electricity_session_coordinator = hass.data[DOMAIN][account_id][DATA_FREE_ELECTRICITY_SESSIONS_COORDINATOR]

  now = utcnow()
  entities = [
    OctopusEnergySavingSessions(hass, saving_session_coordinator, account_id),
    OctopusEnergyGreennessForecastHighlighted(hass, greenness_forecast_coordinator, account_id)
  ]

  ir.async_create_issue(
    hass,
    DOMAIN,
    REPAIR_SAVING_SESSION_BINARY_SENSOR_DEPRECATED,
    is_fixable=False,
    severity=ir.IssueSeverity.WARNING,
    learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/architecture_decision_records/0003_move_to_calendar_entities_for_octoplus_events",
    translation_key="saving_session_binary_sensor_deprecated",
  )

  ir.async_create_issue(
    hass,
    DOMAIN,
    REPAIR_GREENNESS_FORECAST_BINARY_SENSOR_DEPRECATED,
    is_fixable=False,
    severity=ir.IssueSeverity.WARNING,
    translation_key="greenness_forecast_binary_sensor_deprecated",
  )

  if octoplus_enrolled:
    entities.append(OctopusEnergyFreeElectricitySessions(hass, free_electricity_session_coordinator, account_id))   
    ir.async_create_issue(
      hass,
      DOMAIN,
      REPAIR_FREE_ELECTRICITY_SESSION_BINARY_SENSOR_DEPRECATED,
      is_fixable=False,
      severity=ir.IssueSeverity.WARNING,
      learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/architecture_decision_records/0003_move_to_calendar_entities_for_octoplus_events",
      translation_key="free_electricity_session_binary_sensor_deprecated",
    ) 

  if len(account_info["electricity_meter_points"]) > 0:

    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      tariff_code = get_active_tariff(now, point["agreements"])
      if tariff_code is not None:
        for meter in point["meters"]:
          mpan = point["mpan"]
          serial_number = meter["serial_number"]
          electricity_rate_coordinator = hass.data[DOMAIN][account_id][DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number)]
          
          entities.append(OctopusEnergyElectricityOffPeak(hass, electricity_rate_coordinator, meter, point))

  entities.extend(get_intelligent_entities(hass, account_id, config))

  account_debug_override = await async_get_account_debug_override(hass, account_id)
  mock_heat_pump = account_debug_override.mock_heat_pump if account_debug_override is not None else False
  if mock_heat_pump:
    heat_pump_id = get_mock_heat_pump_id()
    key = DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY.format(heat_pump_id)
    coordinator = hass.data[DOMAIN][account_id][DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR.format(heat_pump_id)]
    entities.extend(setup_heat_pump_sensors(hass, account_id, heat_pump_id, hass.data[DOMAIN][account_id][key].data, coordinator))
  elif "heat_pump_ids" in account_info:
    for heat_pump_id in account_info["heat_pump_ids"]:
      key = DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY.format(heat_pump_id)
      coordinator = hass.data[DOMAIN][account_id][DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR.format(heat_pump_id)]
      entities.extend(setup_heat_pump_sensors(hass, account_id, heat_pump_id, hass.data[DOMAIN][account_id][key].data, coordinator))

  if len(entities) > 0:
    async_add_entities(entities)

def setup_heat_pump_sensors(hass: HomeAssistant, account_id: str, heat_pump_id: str, heat_pump_response: HeatPumpResponse, coordinator):

  entities = []

  if heat_pump_response is None:
    return entities

  if heat_pump_response.octoHeatPumpControllerConfiguration is not None:
    entities.append(OctopusEnergyHeatPumpWeatherCompensationEnabled(
        hass,
        coordinator,
        heat_pump_id,
        heat_pump_response.octoHeatPumpControllerConfiguration.heatPump
      ))

  return entities

def get_intelligent_entities(hass, account_id: str, config: dict):
  entities = []

  intelligent_result: IntelligentDeviceCoordinatorResult = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICES] if DATA_INTELLIGENT_DEVICES in hass.data[DOMAIN][account_id] else None
  intelligent_devices: list[IntelligentDevice] = intelligent_result.devices if intelligent_result is not None else []
  intelligent_rate_mode = (config[CONFIG_MAIN_INTELLIGENT_SETTINGS][CONFIG_MAIN_INTELLIGENT_RATE_MODE] 
                           if CONFIG_MAIN_INTELLIGENT_SETTINGS in config and CONFIG_MAIN_INTELLIGENT_RATE_MODE in config[CONFIG_MAIN_INTELLIGENT_SETTINGS] 
                           else CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES)
  manually_refresh_dispatches = (config[CONFIG_MAIN_INTELLIGENT_SETTINGS][CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES] == True
                           if CONFIG_MAIN_INTELLIGENT_SETTINGS in config and CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES in config[CONFIG_MAIN_INTELLIGENT_SETTINGS] 
                           else False)

  for intelligent_device in intelligent_devices:

    if intelligent_device.device_type == INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES or intelligent_device.device_type == INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS:
      
      platform = entity_platform.async_get_current_platform()
      if (manually_refresh_dispatches):
        platform.async_register_entity_service(
          "refresh_intelligent_dispatches",
          vol.All(
            cv.make_entity_service_schema(
              {},
              extra=vol.ALLOW_EXTRA,
            ),
          ),
          "async_refresh_dispatches"
        )

      platform.async_register_entity_service(
        "get_point_in_time_intelligent_dispatch_history",
        vol.All(
          cv.make_entity_service_schema(
          {
            vol.Required("point_in_time"): cv.datetime
          },
          extra=vol.ALLOW_EXTRA,
        ),
        ),
        "async_get_point_in_time_intelligent_dispatch_history",
        supports_response=SupportsResponse.ONLY
      )

      coordinator = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES_COORDINATOR.format(intelligent_device.id)]
      entities.append(OctopusEnergyIntelligentDispatching(hass, coordinator, intelligent_device, account_id, intelligent_rate_mode, manually_refresh_dispatches))

  return entities

async def async_setup_target_sensors(hass, entry, async_add_entities):
  config = dict(entry.data)
  
  account_id = config[CONFIG_ACCOUNT_ID]
  account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None

  mpan = config[CONFIG_TARGET_MPAN]

  now = utcnow()
  is_export = False
  for point in account_info["electricity_meter_points"]:
    tariff_code = get_active_tariff(now, point["agreements"])
    if tariff_code is not None:
      # For backwards compatibility, pick the first applicable meter
      if point["mpan"] == mpan or mpan is None:
        for meter in point["meters"]:
          is_export = meter["is_export"]
          serial_number = meter["serial_number"]
          coordinator = hass.data[DOMAIN][account_id][DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number)]
          free_electricity_coordinator = hass.data[DOMAIN][account_id][DATA_FREE_ELECTRICITY_SESSIONS_COORDINATOR]
          entities = []

          if config[CONFIG_KIND] == CONFIG_KIND_TARGET_RATE:
            entities.append(OctopusEnergyTargetRate(hass, account_id, entry, config, is_export, coordinator, free_electricity_coordinator))
          else:
            entities.append(OctopusEnergyRollingTargetRate(hass, account_id, entry, config, is_export, coordinator, free_electricity_coordinator))

          async_add_entities(entities)
          return
