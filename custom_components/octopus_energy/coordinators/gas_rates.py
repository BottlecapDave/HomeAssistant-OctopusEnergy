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
  REFRESH_RATE_IN_MINUTES_RATES,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..utils import private_rates_to_public_rates
from . import BaseCoordinatorResult, get_gas_meter_tariff_code, raise_rate_events

_LOGGER = logging.getLogger(__name__)

class GasRatesCoordinatorResult(BaseCoordinatorResult):
  rates: list

  def __init__(self, last_retrieved: datetime, request_attempts: int, rates: list):
    super().__init__(last_retrieved, request_attempts, REFRESH_RATE_IN_MINUTES_RATES)
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
    
    if (existing_rates_result is None or current >= existing_rates_result.next_refresh):
      try:
        new_rates = await client.async_get_gas_rates(tariff_code, period_from, period_to)
      except Exception as e:
        if isinstance(e, ApiException) == False:
          raise
        
        _LOGGER.debug(f'Failed to retrieve gas rates for {target_mprn}/{target_serial_number} ({tariff_code})')

      # Make sure our rate information doesn't contain any negative values https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/506
      if new_rates is not None:
        for rate in new_rates:
          if rate["value_inc_vat"] < 0:
            new_rates = None
            break
        
      if new_rates is not None:
        _LOGGER.debug(f'Gas rates retrieved for {target_mprn}/{target_serial_number} ({tariff_code});')

        raise_rate_events(current,
                          private_rates_to_public_rates(new_rates),
                          { "mprn": target_mprn, "serial_number": target_serial_number, "tariff_code": tariff_code },
                          fire_event,
                          EVENT_GAS_PREVIOUS_DAY_RATES,
                          EVENT_GAS_CURRENT_DAY_RATES,
                          EVENT_GAS_NEXT_DAY_RATES)
        
        return GasRatesCoordinatorResult(current, 1, new_rates)

      result = None
      if (existing_rates_result is not None):
        result = GasRatesCoordinatorResult(existing_rates_result.last_retrieved, existing_rates_result.request_attempts + 1, existing_rates_result.rates)
        _LOGGER.warning(f"Failed to retrieve new gas rates for {target_mprn}/{target_serial_number} - using cached rates. Next attempt at {result.next_refresh}")
      else:
        # We want to force into our fallback mode
        result = GasRatesCoordinatorResult(current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES), 2, None)
        _LOGGER.warning(f"Failed to retrieve new gas rates for {target_mprn}/{target_serial_number}. Next attempt at {result.next_refresh}")

      return result
  
  return existing_rates_result

async def async_setup_gas_rates_coordinator(hass, account_id: str, client: OctopusEnergyApiClient, target_mprn: str, target_serial_number: str):
  key = DATA_GAS_RATES_KEY.format(target_mprn, target_serial_number)

  # Reset data rates as we might have new information
  hass.data[DOMAIN][account_id][key] = None
  
  async def async_update_gas_rates_data():
    """Fetch data from API endpoint."""
    current = now()
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN][account_id] else None
    account_info = account_result.account if account_result is not None else None
    rates = hass.data[DOMAIN][account_id][key] if key in hass.data[DOMAIN][account_id] else None

    hass.data[DOMAIN][account_id][key] = await async_refresh_gas_rates_data(
      current,
      client,
      account_info,
      target_mprn,
      target_serial_number,
      rates,
      hass.bus.async_fire
    )

    return hass.data[DOMAIN][account_id][key]

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

  return coordinator