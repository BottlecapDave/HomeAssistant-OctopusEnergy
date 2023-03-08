from datetime import timedelta
import logging
from .binary_sensors.saving_sessions import OctopusEnergySavingSessions
from .binary_sensors.target_rate import OctopusEnergyTargetRate

import voluptuous as vol

from homeassistant.helpers import config_validation as cv, entity_platform
from .const import (
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_MPAN,

  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_SAVING_SESSIONS_COORDINATOR,
  DATA_ACCOUNT
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_season_sensors(hass, entry, async_add_entities)
  elif CONFIG_TARGET_NAME in entry.data:
    await async_setup_target_sensors(hass, entry, async_add_entities)

  platform = entity_platform.async_get_current_platform()
  platform.async_register_entity_service(
    "update_target_config",
    vol.All(
      vol.Schema(
        {
          vol.Required("target_hours"): str,
          vol.Optional("target_start_time"): str,
          vol.Optional("target_end_time"): str,
          vol.Optional("target_offset"): str,
        },
        extra=vol.ALLOW_EXTRA,
      ),
      cv.has_at_least_one_key(
        "target_hours", "target_start_time", "target_end_time", "target_offset"
      ),
    ),
    "async_update_config",
  )

  return True

async def async_setup_season_sensors(hass, entry, async_add_entities):
  _LOGGER.debug('Setting up Season Saving entity')
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  saving_session_coordinator = hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR]

  await saving_session_coordinator.async_config_entry_first_refresh()

  async_add_entities([OctopusEnergySavingSessions(saving_session_coordinator)], True)

async def async_setup_target_sensors(hass, entry, async_add_entities):
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)
  
  coordinator = hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR]

  account_info = hass.data[DOMAIN][DATA_ACCOUNT]

  mpan = config[CONFIG_TARGET_MPAN]

  is_export = False
  for point in account_info["electricity_meter_points"]:
    if point["mpan"] == mpan:
      for meter in point["meters"]:
        is_export = meter["is_export"]

  entities = [OctopusEnergyTargetRate(coordinator, config, is_export)]
  async_add_entities(entities, True)
