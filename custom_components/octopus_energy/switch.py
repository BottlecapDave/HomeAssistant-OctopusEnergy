import logging

import voluptuous as vol

from homeassistant.helpers import entity_platform
import homeassistant.helpers.config_validation as cv

from .utils.debug_overrides import async_get_account_debug_override
from .intelligent.smart_charge import OctopusEnergyIntelligentSmartCharge
from .intelligent.bump_charge import OctopusEnergyIntelligentBumpCharge
from .intelligent import get_intelligent_features
from .api_client.intelligent_device import IntelligentDevice
from .api_client.charge_point import OnboardedChargePoint
from .charge_point import get_mock_charge_point_id
from .charge_point.eco_mode_switch import OctopusEnergyChargePointEcoModeSwitch
from .charge_point.random_delay_switch import OctopusEnergyChargePointRandomDelaySwitch
from .charge_point.cable_auto_lock_switch import OctopusEnergyChargePointCableAutoLockSwitch
from .charge_point.away_mode_switch import OctopusEnergyChargePointAwayModeSwitch
from .charge_point.boost_switch import OctopusEnergyChargePointBoostSwitch
from .coordinators.intelligent_device import IntelligentDeviceCoordinatorResult

from .const import (
  CONFIG_ACCOUNT_ID,
  DATA_CLIENT,
  DATA_INTELLIGENT_DEVICES,
  DOMAIN,

  CONFIG_MAIN_API_KEY,

  DATA_INTELLIGENT_SETTINGS_COORDINATOR,
  DATA_INTELLIGENT_DISPATCHES_COORDINATOR,
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
    dispatches_coordinator = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES_COORDINATOR.format(intelligent_device.id)]

    if intelligent_features.bump_charge_supported:
      entities.append(OctopusEnergyIntelligentSmartCharge(hass, settings_coordinator, client, intelligent_device, account_id, account_debug_override.mock_intelligent_controls if account_debug_override is not None else False))

    if intelligent_features.smart_charge_supported:
      entities.append(OctopusEnergyIntelligentBumpCharge(hass, dispatches_coordinator, client, intelligent_device, account_id, account_debug_override.mock_intelligent_controls if account_debug_override is not None else False))

  entities.extend(get_charge_point_switch_entities(hass, account_id, client, account_debug_override))

  if len(entities) > 0:
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
      "boost_charge_point",
      vol.All(
        cv.make_entity_service_schema(
          {
            vol.Required("hours"): cv.positive_int,
            vol.Required("minutes"): cv.positive_int,
          },
          extra=vol.ALLOW_EXTRA,
        ),
      ),
      "async_boost_charge_point"
    )

  async_add_entities(entities)

def get_charge_point_switch_entities(hass, account_id: str, client, account_debug_override):
  entities = []

  is_mocked = account_debug_override.mock_charge_point if account_debug_override is not None else False
  if is_mocked:
    charge_point_id = get_mock_charge_point_id()
    key = DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY.format(charge_point_id)
    coordinator = hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR.format(charge_point_id)]
    entities.extend(setup_charge_point_switches(hass, coordinator, client, account_id, charge_point_id, hass.data[DOMAIN][account_id][key].data, is_mocked))
  else:
    charge_point_ids = hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_IDS] if DATA_CHARGE_POINT_IDS in hass.data[DOMAIN][account_id] else []
    for charge_point_id in charge_point_ids:
      key = DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY.format(charge_point_id)
      coordinator = hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR.format(charge_point_id)]
      entities.extend(setup_charge_point_switches(hass, coordinator, client, account_id, charge_point_id, hass.data[DOMAIN][account_id][key].data, is_mocked))

  return entities

def setup_charge_point_switches(hass, coordinator, client, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint, is_mocked: bool):
  entities = []

  if charge_point is None:
    return entities

  entities.append(OctopusEnergyChargePointEcoModeSwitch(hass, coordinator, client, account_id, charge_point_id, charge_point, is_mocked))
  entities.append(OctopusEnergyChargePointRandomDelaySwitch(hass, coordinator, client, account_id, charge_point_id, charge_point, is_mocked))
  entities.append(OctopusEnergyChargePointAwayModeSwitch(hass, coordinator, client, account_id, charge_point_id, charge_point, is_mocked))
  entities.append(OctopusEnergyChargePointBoostSwitch(hass, coordinator, client, account_id, charge_point_id, charge_point, is_mocked))

  if charge_point.configuration is not None and charge_point.configuration.isChargeCableAutoLockAvailable:
    entities.append(OctopusEnergyChargePointCableAutoLockSwitch(hass, coordinator, client, account_id, charge_point_id, charge_point, is_mocked))

  return entities