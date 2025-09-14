import logging

from .utils.debug_overrides import async_get_account_debug_override

from .intelligent import get_intelligent_features
from .intelligent.charge_target import OctopusEnergyIntelligentChargeTarget
from .api_client.intelligent_device import IntelligentDevice
from .coordinators.intelligent_device import IntelligentDeviceCoordinatorResult

from .const import (
  CONFIG_ACCOUNT_ID,
  DATA_CLIENT,
  DATA_INTELLIGENT_DEVICES,
  DOMAIN,

  CONFIG_MAIN_API_KEY,

  DATA_INTELLIGENT_SETTINGS_COORDINATOR,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  config = dict(entry.data)

  entities = []

  if CONFIG_MAIN_API_KEY in entry.data:
    entities.extend(await async_setup_intelligent_sensors(hass, config))

  async_add_entities(entities)

  return True

async def async_setup_intelligent_sensors(hass, config):
  _LOGGER.debug('Setting up intelligent sensors')

  entities = []

  account_id = config[CONFIG_ACCOUNT_ID]

  account_debug_override = await async_get_account_debug_override(hass, account_id)

  client = hass.data[DOMAIN][account_id][DATA_CLIENT]
  intelligent_result: IntelligentDeviceCoordinatorResult = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICES] if DATA_INTELLIGENT_DEVICES in hass.data[DOMAIN][account_id] else None
  intelligent_devices: list[IntelligentDevice] = intelligent_result.devices if intelligent_result is not None else []

  for intelligent_device in intelligent_devices:

    intelligent_features = get_intelligent_features(intelligent_device.provider)
    settings_coordinator = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_SETTINGS_COORDINATOR.format(intelligent_device.id)]

    if intelligent_features.charge_limit_supported == True:
      entities.append(OctopusEnergyIntelligentChargeTarget(hass, settings_coordinator, client, intelligent_device, account_id, account_debug_override.mock_intelligent_controls if account_debug_override is not None else False))

  return entities