import logging

import voluptuous as vol

from homeassistant.helpers import config_validation as cv, entity_platform, issue_registry as ir
from homeassistant.util.dt import (utcnow)

from .electricity.off_peak import OctopusEnergyElectricityOffPeak
from .octoplus.saving_sessions import OctopusEnergySavingSessions
from .target_rates.target_rate import OctopusEnergyTargetRate
from .intelligent.dispatching import OctopusEnergyIntelligentDispatching
from .greenness_forecast.highlighted import OctopusEnergyGreennessForecastHighlighted
from .utils import get_active_tariff
from .intelligent import get_intelligent_features
from .api_client.intelligent_device import IntelligentDevice
from .target_rates.rolling_target_rate import OctopusEnergyRollingTargetRate
from .octoplus.free_electricity_sessions import OctopusEnergyFreeElectricitySessions

from .const import (
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_ROLLING_TARGET_RATE,
  CONFIG_KIND_TARGET_RATE,
  CONFIG_ACCOUNT_ID,
  CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES,
  CONFIG_MAIN_INTELLIGENT_SETTINGS,
  DATA_FREE_ELECTRICITY_SESSIONS_COORDINATOR,
  DATA_GREENNESS_FORECAST_COORDINATOR,
  DATA_INTELLIGENT_DEVICE,
  DATA_INTELLIGENT_DISPATCHES_COORDINATOR,
  DATA_INTELLIGENT_MPAN,
  DATA_INTELLIGENT_SERIAL_NUMBER,
  DOMAIN,

  CONFIG_TARGET_MPAN,

  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DATA_SAVING_SESSIONS_COORDINATOR,
  DATA_ACCOUNT,
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

  if entry.options:
    config.update(entry.options)

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

  if octoplus_enrolled:
    entities.append(OctopusEnergyFreeElectricitySessions(hass, free_electricity_session_coordinator, account_id))    

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

  intelligent_device: IntelligentDevice = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE] if DATA_INTELLIGENT_DEVICE in hass.data[DOMAIN][account_id] else None
  intelligent_mpan = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_MPAN] if DATA_INTELLIGENT_MPAN in hass.data[DOMAIN][account_id] else None
  intelligent_serial_number = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_SERIAL_NUMBER] if DATA_INTELLIGENT_SERIAL_NUMBER in hass.data[DOMAIN][account_id] else None
  if intelligent_device is not None and intelligent_mpan is not None and intelligent_serial_number is not None:

    if (CONFIG_MAIN_INTELLIGENT_SETTINGS not in config or
        CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES not in config[CONFIG_MAIN_INTELLIGENT_SETTINGS] or
        config[CONFIG_MAIN_INTELLIGENT_SETTINGS][CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES] == True):
      platform = entity_platform.async_get_current_platform()
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

    coordinator = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES_COORDINATOR]
    electricity_rate_coordinator = hass.data[DOMAIN][account_id][DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(intelligent_mpan, intelligent_serial_number)]
    entities.append(OctopusEnergyIntelligentDispatching(hass, coordinator, electricity_rate_coordinator, intelligent_mpan, intelligent_device, account_id))

  if len(entities) > 0:
    async_add_entities(entities)

async def async_setup_target_sensors(hass, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)
  
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
