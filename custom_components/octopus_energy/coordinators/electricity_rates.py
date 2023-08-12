import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  DOMAIN,
  DATA_CLIENT,
  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_ELECTRICITY_RATES,
  DATA_ACCOUNT,
  DATA_INTELLIGENT_DISPATCHES,
)

from ..api_client import OctopusEnergyApiClient

from . import get_current_electricity_agreement_tariff_codes
from ..intelligent import adjust_intelligent_rates

_LOGGER = logging.getLogger(__name__)

async def async_refresh_electricity_rates_data(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_info,
    existing_rates: list,
    dispatches: list
  ):
  if (account_info is not None):
    tariff_codes = get_current_electricity_agreement_tariff_codes(current, account_info)

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
          new_rates = await client.async_get_electricity_rates(tariff_code, is_smart_meter, period_from, period_to)
          _LOGGER.debug(f'Electricity rates retrieved for {tariff_code}')
        except:
          _LOGGER.debug('Failed to retrieve electricity rates')
      else:
          new_rates = existing_rates[key]
        
      if new_rates is not None:
        if dispatches is not None:
          rates[key] = adjust_intelligent_rates(new_rates, 
                                                dispatches["planned"] if "planned" in dispatches else [],
                                                dispatches["completed"] if "completed" in dispatches else [])
          
          _LOGGER.debug(f"Rates adjusted: {rates[key]}; dispatches: {dispatches}")
        else:
          rates[key] = new_rates
      elif (existing_rates is not None and key in existing_rates):
        _LOGGER.debug(f"Failed to retrieve new electricity rates for {tariff_code}, so using cached rates")
        rates[key] = existing_rates[key]

    return rates
  
  return existing_rates

async def async_setup_electricity_rates_coordinator(hass, account_id: str):
  # Reset data rates as we might have new information
  hass.data[DOMAIN][DATA_ELECTRICITY_RATES] = []
  
  async def async_update_electricity_rates_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    account_info = hass.data[DOMAIN][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN] else None
    dispatches = hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES] if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN] else None
    rates = hass.data[DOMAIN][DATA_ELECTRICITY_RATES] if DATA_ELECTRICITY_RATES in hass.data[DOMAIN] else {}

    hass.data[DOMAIN][DATA_ELECTRICITY_RATES] = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      rates,
      dispatches
    )

    return hass.data[DOMAIN][DATA_ELECTRICITY_RATES]

  hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="electricity_rates",
    update_method=async_update_electricity_rates_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

  await hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR].async_config_entry_first_refresh()