import logging

from homeassistant.core import HomeAssistant

from .home_pro.screen_text import OctopusEnergyHomeProScreenText

from .const import (
  CONFIG_ACCOUNT_ID,
  DATA_HOME_PRO_CLIENT,
  DOMAIN,
  
  CONFIG_MAIN_API_KEY
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""
  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  if CONFIG_MAIN_API_KEY in config:
    await async_setup_default_sensors(hass, config, async_add_entities)

async def async_setup_default_sensors(hass: HomeAssistant, config, async_add_entities):
  account_id = config[CONFIG_ACCOUNT_ID]
  
  home_pro_client = hass.data[DOMAIN][account_id][DATA_HOME_PRO_CLIENT] if DATA_HOME_PRO_CLIENT in hass.data[DOMAIN][account_id] else None

  entities = []

  if home_pro_client is not None:
    entities.append(OctopusEnergyHomeProScreenText(hass, account_id, home_pro_client))

  async_add_entities(entities)