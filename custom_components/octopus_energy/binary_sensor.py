import logging

import voluptuous as vol

from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.util.dt import (utcnow)

from .electricity.off_peak import OctopusEnergyElectricityOffPeak
from .saving_sessions.saving_sessions import OctopusEnergySavingSessions
from .target_rates.target_rate import OctopusEnergyTargetRate
from .intelligent.dispatching import OctopusEnergyIntelligentDispatching
from .api_client import OctopusEnergyApiClient
from .intelligent import async_mock_intelligent_data, is_intelligent_tariff, mock_intelligent_device
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
    await async_setup_main_sensors(hass, entry, async_add_entities)
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

async def async_setup_main_sensors(hass, entry, async_add_entities):
  _LOGGER.debug('Setting up main sensors')
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  saving_session_coordinator = hass.data[DOMAIN][DATA_SAVING_SESSIONS_COORDINATOR]

  await saving_session_coordinator.async_config_entry_first_refresh()

  account_info = hass.data[DOMAIN][DATA_ACCOUNT]

  electricity_rate_coordinator = hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR]

  now = utcnow()
  has_intelligent_tariff = False
  intelligent_mpan = None
  entities = [OctopusEnergySavingSessions(hass, saving_session_coordinator)]
  if len(account_info["electricity_meter_points"]) > 0:
    electricity_rate_coordinator = hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR]
    await electricity_rate_coordinator.async_config_entry_first_refresh()

    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      tariff_code = get_active_tariff_code(now, point["agreements"])
      if tariff_code is not None:
        for meter in point["meters"]:
          entities.append(OctopusEnergyElectricityOffPeak(hass, electricity_rate_coordinator, meter, point))
          if meter["is_export"] == False:
            intelligent_mpan = point["mpan"]

      if is_intelligent_tariff(tariff_code):
        has_intelligent_tariff = True
        break

  should_mock_intelligent_data = await async_mock_intelligent_data(hass)
  if has_intelligent_tariff or should_mock_intelligent_data:
    coordinator = hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES_COORDINATOR]
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]

    account_id = hass.data[DOMAIN][DATA_ACCOUNT_ID]
    if should_mock_intelligent_data:
      device = mock_intelligent_device()
    else:
      device = await client.async_get_intelligent_device(account_id)

    entities.append(OctopusEnergyIntelligentDispatching(hass, coordinator, electricity_rate_coordinator, intelligent_mpan, device))

  if len(entities) > 0:
    async_add_entities(entities, True)

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
