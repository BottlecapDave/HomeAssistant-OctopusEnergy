import logging
from datetime import datetime, timedelta
from typing import Callable, Any

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,
  DATA_GAS_RATES_KEY,
  DATA_ACCOUNT,
  EVENT_GAS_CURRENT_DAY_RATES,
  EVENT_GAS_NEXT_DAY_RATES,
  EVENT_GAS_PREVIOUS_DAY_RATES,
)

from ..api_client import OctopusEnergyApiClient
from ..utils import private_rates_to_public_rates
from . import get_gas_meter_tariff_code, raise_rate_events

_LOGGER = logging.getLogger(__name__)

class GasRatesCoordinatorResult:
  last_retrieved: datetime
  rates: list

  def __init__(self, last_retrieved: datetime, rates: list):
    self.last_retrieved = last_retrieved
    self.rates = rates

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

    tariff_code = get_gas_meter_tariff_code(current, account_info, target_mprn, target_serial_number)
    if tariff_code is None:
      return None

    new_rates: list = None
    if ((current.minute % 30) == 0 or 
        existing_rates_result is None or
        existing_rates_result.rates is None or
        len(existing_rates_result.rates) < 1 or
        existing_rates_result.rates[-1]["start"] < period_from):
      try:
        new_rates = await client.async_get_gas_rates(tariff_code, period_from, period_to)
      except:
        _LOGGER.debug(f'Failed to retrieve gas rates for {target_mprn}/{target_serial_number} ({tariff_code})')
      
    if new_rates is not None:
      _LOGGER.debug(f'Gas rates retrieved for {target_mprn}/{target_serial_number} ({tariff_code});')

      raise_rate_events(current,
                        private_rates_to_public_rates(new_rates),
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
    always_update=True
  )

  await coordinator.async_config_entry_first_refresh()

  return coordinator