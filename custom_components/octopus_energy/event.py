import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.util.dt import (utcnow)
from homeassistant.helpers import config_validation as cv, entity_platform

from .utils import get_active_tariff
from .electricity.rates_previous_day import OctopusEnergyElectricityPreviousDayRates
from .electricity.rates_current_day import OctopusEnergyElectricityCurrentDayRates
from .electricity.rates_next_day import OctopusEnergyElectricityNextDayRates
from .electricity.rates_previous_consumption import OctopusEnergyElectricityPreviousConsumptionRates
from .gas.rates_current_day import OctopusEnergyGasCurrentDayRates
from .gas.rates_next_day import OctopusEnergyGasNextDayRates
from .gas.rates_previous_day import OctopusEnergyGasPreviousDayRates
from .gas.rates_previous_consumption import OctopusEnergyGasPreviousConsumptionRates
from .octoplus.saving_sessions_events import OctopusEnergyOctoplusSavingSessionEvents
from .octoplus.free_electricity_sessions_events import OctopusEnergyOctoplusFreeElectricitySessionEvents
from .electricity.rates_previous_consumption_override import OctopusEnergyElectricityPreviousConsumptionOverrideRates
from .gas.rates_previous_consumption_override import OctopusEnergyGasPreviousConsumptionOverrideRates

from .const import (
  CONFIG_ACCOUNT_ID,
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_TARIFF_COMPARISON,
  CONFIG_TARIFF_COMPARISON_MPAN_MPRN,
  DATA_CLIENT,
  DOMAIN,

  DATA_ACCOUNT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  config = dict(entry.data)

  if config[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
    await async_setup_main_sensors(hass, entry, async_add_entities)
  elif config[CONFIG_KIND] == CONFIG_KIND_TARIFF_COMPARISON:
    await async_setup_tariff_comparison_sensors(hass, config, async_add_entities)

  platform = entity_platform.async_get_current_platform()
  platform.async_register_entity_service(
    "join_octoplus_saving_session_event",
    vol.All(
      cv.make_entity_service_schema(
        {
          vol.Required("event_code"): str,
        },
        extra=vol.ALLOW_EXTRA,
      ),
    ),
    "async_join_saving_session_event",
  )

  return True

async def async_setup_main_sensors(hass, entry, async_add_entities):
  _LOGGER.debug('Setting up main sensors')
  config = dict(entry.data)

  account_id = config[CONFIG_ACCOUNT_ID]

  account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None
  client = hass.data[DOMAIN][account_id][DATA_CLIENT]
  octoplus_enrolled = account_info is not None and account_info["octoplus_enrolled"] == True

  now = utcnow()
  entities = [OctopusEnergyOctoplusSavingSessionEvents(hass, client, account_id)]

  if octoplus_enrolled:
    entities.append(OctopusEnergyOctoplusFreeElectricitySessionEvents(hass, account_id))

  if len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      tariff = get_active_tariff(now, point["agreements"])
      if tariff is not None:
        for meter in point["meters"]:
          entities.append(OctopusEnergyElectricityPreviousDayRates(hass, meter, point))
          entities.append(OctopusEnergyElectricityCurrentDayRates(hass, meter, point))
          entities.append(OctopusEnergyElectricityNextDayRates(hass, meter, point))
          entities.append(OctopusEnergyElectricityPreviousConsumptionRates(hass, meter, point))

  if len(account_info["gas_meter_points"]) > 0:
    for point in account_info["gas_meter_points"]:
      # We only care about points that have active agreements
      tariff = get_active_tariff(now, point["agreements"])
      if tariff is not None:
        for meter in point["meters"]:
          entities.append(OctopusEnergyGasPreviousDayRates(hass, meter, point))
          entities.append(OctopusEnergyGasCurrentDayRates(hass, meter, point))
          entities.append(OctopusEnergyGasNextDayRates(hass, meter, point))
          entities.append(OctopusEnergyGasPreviousConsumptionRates(hass, meter, point))

  if len(entities) > 0:
    async_add_entities(entities)

async def async_setup_tariff_comparison_sensors(hass: HomeAssistant, config, async_add_entities):
  account_id = config[CONFIG_ACCOUNT_ID]
  account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None

  mpan_mprn = config[CONFIG_TARIFF_COMPARISON_MPAN_MPRN]

  now = utcnow()
  for point in account_info["electricity_meter_points"]:
    tariff = get_active_tariff(now, point["agreements"])
    if tariff is not None:
      if point["mpan"] == mpan_mprn:
        for meter in point["meters"]:
          entities = [
            OctopusEnergyElectricityPreviousConsumptionOverrideRates(hass, meter, point, config)
          ]
          
          async_add_entities(entities)
          break

  now = utcnow()
  for point in account_info["gas_meter_points"]:
    tariff = get_active_tariff(now, point["agreements"])
    if tariff is not None:
      if point["mprn"] == mpan_mprn:
        for meter in point["meters"]:
          entities = [
            OctopusEnergyGasPreviousConsumptionOverrideRates(hass, meter, point, config)
          ]
          
          async_add_entities(entities)
          break
