import logging

from homeassistant.util.dt import (utcnow)


from .const import (
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_ACCOUNT_ID,
  CONFIG_MAIN_LEGACY_SAVING_SESSIONS_FREE_ELECTRICITY_PRESENT,
  DOMAIN,

  DATA_POWER_UP_DOWN_COORDINATOR,
  DATA_ACCOUNT
)

from .octoplus.free_electricity_sessions_calendar import OctopusEnergyFreeElectricitySessionsCalendar
from .octoplus.saving_sessions_calendar import OctopusEnergySavingSessionsCalendar
from .octoplus.power_up_calendar import OctopusEnergyPowerUpCalendar
from .octoplus.power_down_calendar import OctopusEnergyPowerDownCalendar

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
  legacy_saving_sessions_free_electricity_present = config[CONFIG_MAIN_LEGACY_SAVING_SESSIONS_FREE_ELECTRICITY_PRESENT] if CONFIG_MAIN_LEGACY_SAVING_SESSIONS_FREE_ELECTRICITY_PRESENT in config else False

  power_up_down_coordinator = hass.data[DOMAIN][account_id][DATA_POWER_UP_DOWN_COORDINATOR]

  entities = [
    OctopusEnergyPowerDownCalendar(hass, power_up_down_coordinator, account_id),
  ]

  if legacy_saving_sessions_free_electricity_present:
    entities.append(OctopusEnergySavingSessionsCalendar(hass, power_up_down_coordinator, account_id))

  if octoplus_enrolled:
    if legacy_saving_sessions_free_electricity_present:
      entities.append(OctopusEnergyFreeElectricitySessionsCalendar(hass, power_up_down_coordinator, account_id))
    entities.append(OctopusEnergyPowerUpCalendar(hass, power_up_down_coordinator, account_id))

  if len(entities) > 0:
    async_add_entities(entities)