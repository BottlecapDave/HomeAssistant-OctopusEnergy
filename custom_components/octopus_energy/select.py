import logging

from .utils.debug_overrides import async_get_account_debug_override
from .intelligent.target_time_select import OctopusEnergyIntelligentTargetTimeSelect
from .api_client import OctopusEnergyApiClient
from .api_client.charge_point import OnboardedChargePoint
from .charge_point import get_mock_charge_point_id
from .charge_point.control_mode_select import OctopusEnergyChargePointControlModeSelect
from .intelligent import get_intelligent_features
from .api_client.intelligent_device import IntelligentDevice
from .coordinators.intelligent_device import IntelligentDeviceCoordinatorResult

from .const import (
  CONFIG_ACCOUNT_ID,
  DATA_CLIENT,
  DATA_INTELLIGENT_DEVICES,
  DOMAIN,

  CONFIG_MAIN_API_KEY,

  DATA_INTELLIGENT_SETTINGS_COORDINATOR,
  DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR,
  DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY,
  DATA_CHARGE_POINT_IDS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  config = dict(entry.data)

  if CONFIG_MAIN_API_KEY in config:
    await async_setup_intelligent_sensors(hass, config, async_add_entities)

  return True

async def async_setup_intelligent_sensors(hass, config, async_add_entities):
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

    if intelligent_features.ready_time_supported:
      entities.append(OctopusEnergyIntelligentTargetTimeSelect(hass, settings_coordinator, client, intelligent_device, account_id, account_debug_override.mock_intelligent_controls if account_debug_override is not None else False))

  is_mocked = account_debug_override.mock_charge_point if account_debug_override is not None else False
  if is_mocked:
    charge_point_id = get_mock_charge_point_id()
    key = DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY.format(charge_point_id)
    coordinator = hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR.format(charge_point_id)]
    entities.extend(setup_charge_point_selects(hass, coordinator, client, account_id, charge_point_id, hass.data[DOMAIN][account_id][key].data, is_mocked))
  else:
    charge_point_ids = hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_IDS] if DATA_CHARGE_POINT_IDS in hass.data[DOMAIN][account_id] else []
    for charge_point_id in charge_point_ids:
      key = DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY.format(charge_point_id)
      coordinator = hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR.format(charge_point_id)]
      entities.extend(setup_charge_point_selects(hass, coordinator, client, account_id, charge_point_id, hass.data[DOMAIN][account_id][key].data, is_mocked))

  async_add_entities(entities)

def setup_charge_point_selects(hass, coordinator, client, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint, is_mocked: bool):
  entities = []

  if charge_point is None:
    return entities

  entities.append(OctopusEnergyChargePointControlModeSelect(hass, coordinator, client, account_id, charge_point_id, charge_point, is_mocked))

  return entities