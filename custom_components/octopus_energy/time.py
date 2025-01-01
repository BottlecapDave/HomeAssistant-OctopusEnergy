import logging

from homeassistant.helpers import issue_registry as ir

from .intelligent.target_time import OctopusEnergyIntelligentTargetTime
from .api_client import OctopusEnergyApiClient
from .intelligent import get_intelligent_features
from .api_client.intelligent_device import IntelligentDevice

from .const import (
  CONFIG_ACCOUNT_ID,
  DATA_CLIENT,
  DATA_INTELLIGENT_DEVICE,
  DOMAIN,

  CONFIG_MAIN_API_KEY,

  DATA_INTELLIGENT_SETTINGS_COORDINATOR
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  if CONFIG_MAIN_API_KEY in config:
    await async_setup_intelligent_sensors(hass, config, async_add_entities)

  return True

async def async_setup_intelligent_sensors(hass, config, async_add_entities):
  _LOGGER.debug('Setting up intelligent sensors')

  entities = []

  account_id = config[CONFIG_ACCOUNT_ID]

  client = hass.data[DOMAIN][account_id][DATA_CLIENT]
  intelligent_device: IntelligentDevice = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE] if DATA_INTELLIGENT_DEVICE in hass.data[DOMAIN][account_id] else None
  if intelligent_device is not None:
    intelligent_features = get_intelligent_features(intelligent_device.provider)
    settings_coordinator = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_SETTINGS_COORDINATOR]
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]

    if intelligent_features.ready_time_supported:
      ir.async_create_issue(
        hass,
        DOMAIN,
        "intelligent_target_time_deprecated",
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key="intelligent_target_time_deprecated",
        translation_placeholders={ "account_id": account_id },
        learn_more_url="https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/1079",
      )

      entities.append(OctopusEnergyIntelligentTargetTime(hass, settings_coordinator, client, intelligent_device, account_id))

  async_add_entities(entities)