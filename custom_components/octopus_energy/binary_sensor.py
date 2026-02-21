import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.helpers import config_validation as cv, entity_platform, issue_registry as ir
from homeassistant.util.dt import (utcnow)
import homeassistant.helpers.config_validation as cv

from .electricity.off_peak import OctopusEnergyElectricityOffPeak
from .octoplus.saving_sessions import OctopusEnergySavingSessions
from .intelligent.dispatching import OctopusEnergyIntelligentDispatching
from .greenness_forecast.highlighted import OctopusEnergyGreennessForecastHighlighted
from .utils import get_active_tariff
from .api_client.intelligent_device import IntelligentDevice
from .octoplus.free_electricity_sessions import OctopusEnergyFreeElectricitySessions
from .coordinators.intelligent_device import IntelligentDeviceCoordinatorResult
from .api_client.heat_pump import HeatPumpResponse
from .heat_pump import get_mock_heat_pump_id
from .heat_pump.weather_compensation_enabled import OctopusEnergyHeatPumpWeatherCompensationEnabled
from .utils.debug_overrides import async_get_account_debug_override

from .const import (
  CONFIG_DEFAULT_MINIMUM_DISPATCH_DURATION_IN_MINUTES,
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_ACCOUNT_ID,
  CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES,
  CONFIG_MAIN_INTELLIGENT_MINIMUM_DISPATCH_DURATION_IN_MINUTES,
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

  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DATA_SAVING_SESSIONS_COORDINATOR,
  DATA_ACCOUNT,
  INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS,
  INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES,
  REPAIR_FREE_ELECTRICITY_SESSION_BINARY_SENSOR_DEPRECATED,
  REPAIR_GREENNESS_FORECAST_BINARY_SENSOR_DEPRECATED,
  REPAIR_SAVING_SESSION_BINARY_SENSOR_DEPRECATED
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
    await async_setup_main_sensors(hass, entry, async_add_entities)

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
      minimum_dispatch_duration_in_minutes = (config[CONFIG_MAIN_INTELLIGENT_SETTINGS][CONFIG_MAIN_INTELLIGENT_MINIMUM_DISPATCH_DURATION_IN_MINUTES] 
                                 if CONFIG_MAIN_INTELLIGENT_SETTINGS in config and CONFIG_MAIN_INTELLIGENT_MINIMUM_DISPATCH_DURATION_IN_MINUTES in config[CONFIG_MAIN_INTELLIGENT_SETTINGS] 
                                 else CONFIG_DEFAULT_MINIMUM_DISPATCH_DURATION_IN_MINUTES)
      entities.append(OctopusEnergyIntelligentDispatching(hass, coordinator, intelligent_device, account_id, intelligent_rate_mode, manually_refresh_dispatches, minimum_dispatch_duration_in_minutes))

  return entities
