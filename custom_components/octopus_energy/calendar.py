import logging

from homeassistant.util.dt import (utcnow)


from .const import (
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_ACCOUNT_ID,
  DATA_FREE_ELECTRICITY_SESSIONS_COORDINATOR,
  DATA_GREENNESS_FORECAST_COORDINATOR,
  DOMAIN,

  DATA_SAVING_SESSIONS_COORDINATOR,
  DATA_ACCOUNT
)

from .octoplus.free_electricity_sessions_calendar import OctopusEnergyFreeElectricitySessionsCalendar
from .octoplus.saving_sessions_calendar import OctopusEnergySavingSessionsCalendar
from .greenness_forecast.greener_nights_calendar import OctopusEnergyGreenerNightsSessionsCalendar

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
  free_electricity_session_coordinator = hass.data[DOMAIN][account_id][DATA_FREE_ELECTRICITY_SESSIONS_COORDINATOR]
  greenness_forecast_coordinator = hass.data[DOMAIN][account_id][DATA_GREENNESS_FORECAST_COORDINATOR]

  now = utcnow()
  entities = [
    OctopusEnergySavingSessionsCalendar(hass, saving_session_coordinator, account_id),
    OctopusEnergyGreenerNightsSessionsCalendar(hass, greenness_forecast_coordinator, account_id),
  ]

  if octoplus_enrolled:
    entities.append(OctopusEnergyFreeElectricitySessionsCalendar(hass, free_electricity_session_coordinator, account_id))    

  if len(entities) > 0:
    async_add_entities(entities)