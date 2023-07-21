from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.util.dt import (utcnow)

from .saving_sessions.saving_sessions import OctopusEnergySavingSessions
from .target_rates.target_rate import OctopusEnergyTargetRate
from .intelligent.dispatching import OctopusEnergyIntelligentDispatching
from .api_client import OctopusEnergyApiClient
from .intelligent import async_mock_intelligent_data, is_intelligent_tariff
from .utils import get_active_tariff_code

from .const import (
  DATA_ACCOUNT_ID,
  DATA_CLIENT,
  DATA_INTELLIGENT_DISPATCHES_COORDINATOR,
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_MPAN,

  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_SAVING_SESSIONS_COORDINATOR,
  DATA_ACCOUNT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_saving_session_sensors(hass, entry, async_add_entities)
    await async_setup_intelligent_sensors(hass, async_add_entities)
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

async def async_setup_saving_session_sensors(hass, entry, async_add_entities):
  _LOGGER.debug('Setting up Saving Session entities')
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  saving_session_coordinator = hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR]

  await saving_session_coordinator.async_config_entry_first_refresh()

  async_add_entities([OctopusEnergySavingSessions(hass, saving_session_coordinator)], True)

async def async_setup_intelligent_sensors(hass, async_add_entities):
  _LOGGER.debug('Setting up intelligent sensors')

  account_info = hass.data[DOMAIN][DATA_ACCOUNT]

  now = utcnow()
  has_intelligent_tariff = False
  if len(account_info["electricity_meter_points"]) > 0:

    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      tariff_code = get_active_tariff_code(now, point["agreements"])
      if is_intelligent_tariff(tariff_code):
        has_intelligent_tariff = True
        break

  if has_intelligent_tariff or await async_mock_intelligent_data(hass):
    coordinator = hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES_COORDINATOR]
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]

    device = await client.async_get_intelligent_device(hass.data[DOMAIN][DATA_ACCOUNT_ID])

    async_add_entities([OctopusEnergyIntelligentDispatching(hass, coordinator, device)], True)

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

  entities = [OctopusEnergyTargetRate(hass, coordinator, config, is_export)]
  async_add_entities(entities, True)
