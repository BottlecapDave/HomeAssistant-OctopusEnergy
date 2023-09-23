import logging

from homeassistant.util.dt import (utcnow)

from .saving_sessions.saving_sessions import OctopusEnergySavingSessions
from .utils import get_active_tariff_code
from .electricity.rates import OctopusEnergyElectricityRates

from .const import (
  DOMAIN,

  CONFIG_MAIN_API_KEY,
  DATA_ACCOUNT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_main_sensors(hass, entry, async_add_entities)

  return True

async def async_setup_main_sensors(hass, entry, async_add_entities):
  _LOGGER.debug('Setting up main sensors')
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  account_info = hass.data[DOMAIN][DATA_ACCOUNT]

  now = utcnow()
  entities = []
  if len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      tariff_code = get_active_tariff_code(now, point["agreements"])
      if tariff_code is not None:
        for meter in point["meters"]:
          entities.append(OctopusEnergyElectricityRates(hass, meter, point))

  if len(entities) > 0:
    async_add_entities(entities, True)
