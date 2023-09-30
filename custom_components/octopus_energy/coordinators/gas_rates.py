import logging
from datetime import datetime, timedelta
from typing import Callable, Any
from custom_components.octopus_energy.utils import get_active_tariff_code

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,
  DATA_CLIENT,
  DATA_GAS_RATES_COORDINATOR_KEY,
  DATA_GAS_RATES_KEY,
  DATA_ACCOUNT,
  EVENT_GAS_CURRENT_DAY_RATES,
  EVENT_GAS_NEXT_DAY_RATES,
  EVENT_GAS_PREVIOUS_DAY_RATES,
)

from ..api_client import OctopusEnergyApiClient

from . import raise_rate_events
from ..intelligent import adjust_intelligent_rates

_LOGGER = logging.getLogger(__name__)

class GasRatesCoordinatorResult:
  last_retrieved: datetime
  rates: list

  def __init__(self, last_retrieved: datetime, rates: list):
    self.last_retrieved = last_retrieved
    self.rates = rates

def get_tariff_code_and_is_smart_meter(current: datetime, account_info, target_mprn: str, target_serial_number: str):
  if len(account_info["gas_meter_points"]) > 0:
    for point in account_info["gas_meter_points"]:
      active_tariff_code = get_active_tariff_code(current, point["agreements"])
      # The type of meter (ie smart vs dumb) can change the tariff behaviour, so we
      # have to enumerate the different meters being used for each tariff as well.
      for meter in point["meters"]:
        if active_tariff_code is not None and point["mprn"] == target_mprn and meter["serial_number"] == target_serial_number:
           return active_tariff_code
           
  return None

async def async_refresh_gas_rates_data(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_info,
    target_mprn: str,
    target_serial_number: str,
    existing_rates_result: GasRatesCoordinatorResult,
    fire_event: Callable[[str, "dict[str, Any]"], None],
  ) -> GasRatesCoordinatorResult: 
  if (account_info is not None):
    period_from = as_utc((current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = as_utc((current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0))

    tariff_code = get_tariff_code_and_is_smart_meter(current, account_info, target_mprn, target_serial_number)
    if tariff_code is None:
      return None

    new_rates: list = None
    if ((current.minute % 30) == 0 or 
        existing_rates_result is None or
        existing_rates_result.rates[-1]["valid_from"] < period_from):
      try:
        new_rates = await client.async_get_gas_rates(tariff_code, period_from, period_to)
      except:
        _LOGGER.debug(f'Failed to retrieve gas rates for {target_mprn}/{target_serial_number} ({tariff_code})')
      
    if new_rates is not None:
      _LOGGER.debug(f'Gas rates retrieved for {target_mprn}/{target_serial_number} ({tariff_code});')

      raise_rate_events(current,
                        new_rates,
                        { "mprn": target_mprn, "serial_number": target_serial_number, "tariff_code": tariff_code },
                        fire_event,
                        EVENT_GAS_PREVIOUS_DAY_RATES,
                        EVENT_GAS_CURRENT_DAY_RATES,
                        EVENT_GAS_NEXT_DAY_RATES)
      
      return GasRatesCoordinatorResult(current, new_rates)

    elif (existing_rates_result is not None):
      _LOGGER.debug(f"Failed to retrieve new gas rates for {target_mprn}/{target_serial_number}, so using cached rates")
      return existing_rates_result
  
  return existing_rates_result

async def async_setup_gas_rates_coordinator(hass, client: OctopusEnergyApiClient, target_mprn: str, target_serial_number: str):
  key = DATA_GAS_RATES_KEY.format(target_mprn, target_serial_number)

  # Reset data rates as we might have new information
  hass.data[DOMAIN][key] = None
  
  async def async_update_gas_rates_data():
    """Fetch data from API endpoint."""
    current = now()
    account_info = hass.data[DOMAIN][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN] else None
    rates = hass.data[DOMAIN][key] if key in hass.data[DOMAIN] else None

    hass.data[DOMAIN][key] = await async_refresh_gas_rates_data(
      current,
      client,
      account_info,
      target_mprn,
      target_serial_number,
      rates,
      hass.bus.async_fire
    )

    return hass.data[DOMAIN][key]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=key,
    update_method=async_update_gas_rates_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
  )

  await coordinator.async_config_entry_first_refresh()

  return coordinator