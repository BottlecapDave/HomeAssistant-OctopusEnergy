import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.util.dt import (utcnow)
import homeassistant.helpers.config_validation as cv

from .electricity.off_peak import OctopusEnergyElectricityOffPeak
from .intelligent.dispatching import OctopusEnergyIntelligentDispatching
from .utils import get_active_tariff
from .api_client.intelligent_device import IntelligentDevice
from .coordinators.intelligent_device import IntelligentDeviceCoordinatorResult
from .api_client.heat_pump import HeatPumpResponse
from .heat_pump import get_mock_heat_pump_id
from .heat_pump.weather_compensation_enabled import OctopusEnergyHeatPumpWeatherCompensationEnabled
from .api_client.charge_point import OnboardedChargePoint
from .charge_point import get_mock_charge_point_id
from .charge_point.connected import OctopusEnergyChargePointConnected
from .utils.debug_overrides import async_get_account_debug_override

from .const import (
  CONFIG_DEFAULT_MINIMUM_DISPATCH_DURATION_IN_MINUTES,
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_ACCOUNT_ID,
  CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES,
  CONFIG_MAIN_INTELLIGENT_MINIMUM_DISPATCH_DURATION_IN_MINUTES,
  CONFIG_MAIN_INTELLIGENT_RATE_MODE,
  CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES,
  CONFIG_MAIN_INTELLIGENT_SETTINGS,
  DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR,
  DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY,
  DATA_HEAT_PUMP_IDS,
  DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR,
  DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY,
  DATA_CHARGE_POINT_IDS,
  DATA_INTELLIGENT_DEVICES,
  DATA_INTELLIGENT_DISPATCHES_COORDINATOR,
  DOMAIN,

  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DATA_ACCOUNT,
  INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS,
  INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES,
)

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

  now = utcnow()
  entities = []

  if len(account_info["electricity_meter_points"]) > 0:

    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      tariff_code = get_active_tariff(now, point["agreements"])
      if tariff_code is not None:
        for meter in point["meters"]:
          mpan = point["mpan"]
          serial_number = meter["serial_number"]
          electricity_rate_coordinator = hass.data[DOMAIN][account_id][DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number)]
          
          entities.append(OctopusEnergyElectricityOffPeak(hass, electricity_rate_coordinator, meter, point))

  entities.extend(get_intelligent_entities(hass, account_id, config))

  account_debug_override = await async_get_account_debug_override(hass, account_id)
  mock_heat_pump = account_debug_override.mock_heat_pump if account_debug_override is not None else False
  if mock_heat_pump:
    heat_pump_id = get_mock_heat_pump_id()
    key = DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY.format(heat_pump_id)
    coordinator = hass.data[DOMAIN][account_id][DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR.format(heat_pump_id)]
    entities.extend(setup_heat_pump_sensors(hass, account_id, heat_pump_id, hass.data[DOMAIN][account_id][key].data, coordinator))
  else:
    heat_pump_ids = hass.data[DOMAIN][account_id][DATA_HEAT_PUMP_IDS] if DATA_HEAT_PUMP_IDS in hass.data[DOMAIN][account_id] else []
    for heat_pump_id in heat_pump_ids:
      key = DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY.format(heat_pump_id)
      coordinator = hass.data[DOMAIN][account_id][DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR.format(heat_pump_id)]
      entities.extend(setup_heat_pump_sensors(hass, account_id, heat_pump_id, hass.data[DOMAIN][account_id][key].data, coordinator))

  mock_charge_point = account_debug_override.mock_charge_point if account_debug_override is not None else False
  if mock_charge_point:
    charge_point_id = get_mock_charge_point_id()
    key = DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY.format(charge_point_id)
    coordinator = hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR.format(charge_point_id)]
    entities.extend(setup_charge_point_sensors(hass, account_id, charge_point_id, hass.data[DOMAIN][account_id][key].data, coordinator))
  else:
    charge_point_ids = hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_IDS] if DATA_CHARGE_POINT_IDS in hass.data[DOMAIN][account_id] else []
    for charge_point_id in charge_point_ids:
      key = DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY.format(charge_point_id)
      coordinator = hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR.format(charge_point_id)]
      entities.extend(setup_charge_point_sensors(hass, account_id, charge_point_id, hass.data[DOMAIN][account_id][key].data, coordinator))

  if len(entities) > 0:
    async_add_entities(entities)

def setup_heat_pump_sensors(hass: HomeAssistant, account_id: str, heat_pump_id: str, heat_pump_response: HeatPumpResponse, coordinator):

  entities = []

  if heat_pump_response is None:
    return entities

  if heat_pump_response.heatPumpControllerConfiguration is not None:
    entities.append(OctopusEnergyHeatPumpWeatherCompensationEnabled(
        hass,
        coordinator,
        heat_pump_id,
        heat_pump_response.heatPumpControllerConfiguration.heatPump
      ))

  return entities

def setup_charge_point_sensors(hass: HomeAssistant, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint, coordinator):

  entities = []

  if charge_point is None:
    return entities

  # Random delay, eco mode, away mode and cable auto lock all have an
  # equivalent switch (see switch.py) that already shows its own on/off
  # state - no need for a separate read-only binary_sensor duplicating the
  # same value (matches the IOG precedent: e.g. the smart_charge switch has
  # no matching binary_sensor either). Connected has no switch counterpart
  # (nothing to control - it's just a status flag), so it stays here.
  entities.append(OctopusEnergyChargePointConnected(hass, coordinator, charge_point_id, charge_point))

  return entities

def get_intelligent_entities(hass, account_id: str, config: dict):
  entities = []

  intelligent_result: IntelligentDeviceCoordinatorResult = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICES] if DATA_INTELLIGENT_DEVICES in hass.data[DOMAIN][account_id] else None
  intelligent_devices: list[IntelligentDevice] = intelligent_result.devices if intelligent_result is not None else []
  intelligent_rate_mode = (config[CONFIG_MAIN_INTELLIGENT_SETTINGS][CONFIG_MAIN_INTELLIGENT_RATE_MODE] 
                           if CONFIG_MAIN_INTELLIGENT_SETTINGS in config and CONFIG_MAIN_INTELLIGENT_RATE_MODE in config[CONFIG_MAIN_INTELLIGENT_SETTINGS] 
                           else CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES)
  manually_refresh_dispatches = (config[CONFIG_MAIN_INTELLIGENT_SETTINGS][CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES] == True
                           if CONFIG_MAIN_INTELLIGENT_SETTINGS in config and CONFIG_MAIN_INTELLIGENT_MANUAL_DISPATCHES in config[CONFIG_MAIN_INTELLIGENT_SETTINGS] 
                           else False)

  for intelligent_device in intelligent_devices:

    if intelligent_device.device_type == INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES or intelligent_device.device_type == INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS:

      platform = entity_platform.async_get_current_platform()
      if (manually_refresh_dispatches):
        platform.async_register_entity_service(
          "refresh_intelligent_dispatches",
          vol.All(
            cv.make_entity_service_schema(
              {},
              extra=vol.ALLOW_EXTRA,
            ),
          ),
          "async_refresh_dispatches"
        )

      platform.async_register_entity_service(
        "get_point_in_time_intelligent_dispatch_history",
        vol.All(
          cv.make_entity_service_schema(
          {
            vol.Required("point_in_time"): cv.datetime
          },
          extra=vol.ALLOW_EXTRA,
        ),
        ),
        "async_get_point_in_time_intelligent_dispatch_history",
        supports_response=SupportsResponse.ONLY
      )

      coordinator = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES_COORDINATOR.format(intelligent_device.id)]
      minimum_dispatch_duration_in_minutes = (config[CONFIG_MAIN_INTELLIGENT_SETTINGS][CONFIG_MAIN_INTELLIGENT_MINIMUM_DISPATCH_DURATION_IN_MINUTES] 
                                 if CONFIG_MAIN_INTELLIGENT_SETTINGS in config and CONFIG_MAIN_INTELLIGENT_MINIMUM_DISPATCH_DURATION_IN_MINUTES in config[CONFIG_MAIN_INTELLIGENT_SETTINGS] 
                                 else CONFIG_DEFAULT_MINIMUM_DISPATCH_DURATION_IN_MINUTES)
      entities.append(OctopusEnergyIntelligentDispatching(hass, coordinator, intelligent_device, account_id, intelligent_rate_mode, manually_refresh_dispatches, minimum_dispatch_duration_in_minutes))

  return entities
