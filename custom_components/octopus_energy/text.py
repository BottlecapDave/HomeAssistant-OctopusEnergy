from datetime import timedelta
import logging

from homeassistant.util.dt import (utcnow)
from homeassistant.core import HomeAssistant

from .electricity.previous_accumulative_cost_override_tariff import OctopusEnergyPreviousAccumulativeElectricityCostTariffOverride
from .gas.previous_accumulative_cost_override_tariff import OctopusEnergyPreviousAccumulativeGasCostTariffOverride

from .utils import (get_active_tariff_code)
from .const import (
  CONFIG_ACCOUNT_ID,
  DOMAIN,
  
  CONFIG_MAIN_API_KEY,

  DATA_CLIENT,
  DATA_ACCOUNT
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
  
  client = hass.data[DOMAIN][account_id][DATA_CLIENT]

  entities = []
  
  account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
  account_info = account_result.account if account_result is not None else None

  now = utcnow()

  if len(account_info["electricity_meter_points"]) > 0:

    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      electricity_tariff_code = get_active_tariff_code(now, point["agreements"])
      if electricity_tariff_code is not None:
        for meter in point["meters"]:
          _LOGGER.info(f'Adding electricity meter; mpan: {point["mpan"]}; serial number: {meter["serial_number"]}')

          if meter["is_smart_meter"] == True:
            entities.append(OctopusEnergyPreviousAccumulativeElectricityCostTariffOverride(hass, account_id, client, electricity_tariff_code, meter, point))
      else:
        for meter in point["meters"]:
          _LOGGER.info(f'Skipping electricity meter due to no active agreement; mpan: {point["mpan"]}; serial number: {meter["serial_number"]}')
        _LOGGER.info(f'agreements: {point["agreements"]}')
  else:
    _LOGGER.info('No electricity meters available')

  if len(account_info["gas_meter_points"]) > 0:
    for point in account_info["gas_meter_points"]:
      # We only care about points that have active agreements
      gas_tariff_code = get_active_tariff_code(now, point["agreements"])
      if gas_tariff_code is not None:
        for meter in point["meters"]:
          _LOGGER.info(f'Adding gas meter; mprn: {point["mprn"]}; serial number: {meter["serial_number"]}')

          if meter["is_smart_meter"] == True:
            entities.append(OctopusEnergyPreviousAccumulativeGasCostTariffOverride(hass, account_id, client, gas_tariff_code, meter, point))
      else:
        for meter in point["meters"]:
          _LOGGER.info(f'Skipping gas meter due to no active agreement; mprn: {point["mprn"]}; serial number: {meter["serial_number"]}')
        _LOGGER.info(f'agreements: {point["agreements"]}')
  else:
    _LOGGER.info('No gas meters available')

  async_add_entities(entities)
