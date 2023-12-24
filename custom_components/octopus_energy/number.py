import logging

from .intelligent import get_intelligent_features
from .intelligent.charge_limit import OctopusEnergyIntelligentChargeLimit

from .const import (
  DATA_CLIENT,
  DATA_INTELLIGENT_DEVICE,
  DOMAIN,

  CONFIG_MAIN_API_KEY,

  DATA_INTELLIGENT_SETTINGS_COORDINATOR,
  DATA_ACCOUNT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_intelligent_sensors(hass, async_add_entities)

  return True

async def async_setup_intelligent_sensors(hass, async_add_entities):
  _LOGGER.debug('Setting up intelligent sensors')

  entities = []

  account_result = hass.data[DOMAIN][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None

  account_id = account_info["id"]
  client = hass.data[DOMAIN][DATA_CLIENT]
  intelligent_device = hass.data[DOMAIN][DATA_INTELLIGENT_DEVICE] if DATA_INTELLIGENT_DEVICE in hass.data[DOMAIN] else None
  if intelligent_device is not None:
    intelligent_features = get_intelligent_features(intelligent_device["provider"])
    settings_coordinator = hass.data[DOMAIN][DATA_INTELLIGENT_SETTINGS_COORDINATOR]

    if intelligent_features.charge_limit_supported == True:
      entities.append(OctopusEnergyIntelligentChargeLimit(hass, settings_coordinator, client, intelligent_device, account_id))

  async_add_entities(entities, True)