import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
import homeassistant.helpers.config_validation as cv

from .api_client.heat_pump import HeatPumpResponse
from .heat_pump import get_mock_heat_pump_id
from .heat_pump.zone import OctopusEnergyHeatPumpZone
from .utils.debug_overrides import async_get_account_debug_override

from .const import (
  CONFIG_ACCOUNT_ID,
  DATA_ACCOUNT,
  DATA_CLIENT,
  DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR,
  DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY,
  DOMAIN,

  CONFIG_MAIN_API_KEY
)
from .api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  config = dict(entry.data)

  if entry.options:
    config.update(entry.options)

  if CONFIG_MAIN_API_KEY in config:
    await async_setup_default_sensors(hass, config, async_add_entities)

  return True

async def async_setup_default_sensors(hass, config, async_add_entities):
  _LOGGER.debug('Setting up default sensors')

  entities = []

  account_id = config[CONFIG_ACCOUNT_ID]
  client = hass.data[DOMAIN][account_id][DATA_CLIENT]
  account_debug_override = await async_get_account_debug_override(hass, account_id)
  account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None

  mock_heat_pump = account_debug_override.mock_heat_pump if account_debug_override is not None else False
  if mock_heat_pump:
    heat_pump_id = get_mock_heat_pump_id()
    key = DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY.format(heat_pump_id)
    coordinator = hass.data[DOMAIN][account_id][DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR.format(heat_pump_id)]
    entities.extend(setup_heat_pump_sensors(hass, client, account_id, heat_pump_id, hass.data[DOMAIN][account_id][key].data, coordinator, mock_heat_pump))
  elif "heat_pump_ids" in account_info:
    for heat_pump_id in account_info["heat_pump_ids"]:
      key = DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY.format(heat_pump_id)
      coordinator = hass.data[DOMAIN][account_id][DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR.format(heat_pump_id)]
      entities.extend(setup_heat_pump_sensors(hass, client, account_id, heat_pump_id, hass.data[DOMAIN][account_id][key].data, coordinator, mock_heat_pump))

  if len(entities) > 0:
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
      "boost_heat_pump_zone",
      vol.All(
        cv.make_entity_service_schema(
          {
            vol.Required("hours"): cv.positive_int,
            vol.Required("minutes"): cv.positive_int,
            vol.Optional("target_temperature"): cv.positive_float,
          },
          extra=vol.ALLOW_EXTRA,
        ),
      ),
      "async_boost_heat_pump_zone"
    )
    platform.async_register_entity_service(
      "set_heat_pump_flow_temp_config",
      vol.All(
        cv.make_entity_service_schema(
          {
            vol.Required("weather_comp_enabled"): cv.boolean,
            vol.Required("weather_comp_min_temperature"): cv.positive_float,
            vol.Required("weather_comp_max_temperature"): cv.positive_float,
            vol.Required("fixed_flow_temperature"): cv.positive_float,
          },
          extra=vol.ALLOW_EXTRA,
        ),
      ),
      "async_set_heat_pump_flow_temp_config"
    )

  async_add_entities(entities)

def setup_heat_pump_sensors(hass: HomeAssistant, client: OctopusEnergyApiClient, account_id: str, heat_pump_id: str, heat_pump_response: HeatPumpResponse, coordinator, mock_heat_pump: bool):

  entities = []

  if heat_pump_response is not None and heat_pump_response.octoHeatPumpControllerConfiguration is not None:
    for zone in heat_pump_response.octoHeatPumpControllerConfiguration.zones:
      if zone.configuration is not None:
        if zone.configuration.enabled == False:
          continue

        entities.append(OctopusEnergyHeatPumpZone(
          hass,
          coordinator,
          client,
          account_id,
          heat_pump_id,
          heat_pump_response.octoHeatPumpControllerConfiguration.heatPump,
          zone,
          mock_heat_pump
        ))

  return entities