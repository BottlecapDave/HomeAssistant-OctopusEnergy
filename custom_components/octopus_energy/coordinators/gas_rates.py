from datetime import datetime, timedelta
import logging

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  DATA_ACCOUNT,
  DOMAIN,
  DATA_GAS_RATES
)

from ..api_client import (OctopusEnergyApiClient)

from . import get_current_gas_agreement_tariff_codes

_LOGGER = logging.getLogger(__name__)

async def async_refresh_gas_rates_data(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_info,
    existing_rates: list
  ):
  if (account_info is not None):
    tariff_codes = get_current_gas_agreement_tariff_codes(current, account_info)

    period_from = as_utc((current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = as_utc((current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0))

    rates = {}
    for ((meter_point, is_smart_meter), tariff_code) in tariff_codes.items():
      key = meter_point

      new_rates = None
      if ((current.minute % 30) == 0 or 
          existing_rates is None or
          key not in existing_rates or
          existing_rates[key][-1]["valid_from"] < period_from):
        try:
          new_rates = await client.async_get_gas_rates(tariff_code, period_from, period_to)
          _LOGGER.debug(f'Gas rates retrieved for {tariff_code}')
        except:
          _LOGGER.debug('Failed to retrieve gas rates')
      else:
          new_rates = existing_rates[key]
        
      if new_rates is not None:
        rates[key] = new_rates
      elif (existing_rates is not None and key in existing_rates):
        _LOGGER.debug(f"Failed to retrieve new gas rates for {tariff_code}, so using cached rates")
        rates[key] = existing_rates[key]

    return rates
  
  return existing_rates

async def async_create_gas_rate_coordinator(hass, client: OctopusEnergyApiClient):
  """Create gas rate coordinator"""
  # Reset data rates as we might have new information
  hass.data[DOMAIN][DATA_GAS_RATES] = []

  async def async_update_data():
    """Fetch data from API endpoint."""
    current = now()
    account_info = hass.data[DOMAIN][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN] else None
    rates = hass.data[DOMAIN][DATA_GAS_RATES] if DATA_GAS_RATES in hass.data[DOMAIN] else {}

    hass.data[DOMAIN][DATA_GAS_RATES] = await async_refresh_gas_rates_data(
      current,
      client,
      account_info,
      rates
    )

    return hass.data[DOMAIN][DATA_GAS_RATES]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"gas_rates",
    update_method=async_update_data,
    update_interval=timedelta(minutes=1),
  )
  
  await coordinator.async_config_entry_first_refresh()

  return coordinator