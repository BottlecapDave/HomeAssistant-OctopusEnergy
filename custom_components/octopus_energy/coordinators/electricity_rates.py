import logging
from datetime import timedelta

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  DOMAIN,
  DATA_CLIENT,
  DATA_ELECTRICITY_RATES_COORDINATOR,
  DATA_RATES,
  DATA_ACCOUNT,
  DATA_INTELLIGENT_DISPATCHES,
)

from ..api_client import OctopusEnergyApiClient

from . import async_get_current_electricity_agreement_tariff_codes
from ..intelligent import adjust_intelligent_rates

_LOGGER = logging.getLogger(__name__)

async def async_setup_electricity_rates_coordinator(hass, account_id: str):
  # Reset data rates as we might have new information
  hass.data[DOMAIN][DATA_RATES] = []

  if DATA_ELECTRICITY_RATES_COORDINATOR in hass.data[DOMAIN]:
    _LOGGER.info("Rates coordinator has already been configured, so skipping")
    return
  
  async def async_update_electricity_rates_data():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    if (DATA_ACCOUNT in hass.data[DOMAIN]):

      tariff_codes = await async_get_current_electricity_agreement_tariff_codes(hass, client, account_id)
      _LOGGER.debug(f'tariff_codes: {tariff_codes}')

      period_from = as_utc(current.replace(hour=0, minute=0, second=0, microsecond=0))
      period_to = as_utc((current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0))

      rates = {}
      dispatches = hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES] if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN] else None
      for ((meter_point, is_smart_meter), tariff_code) in tariff_codes.items():
        key = meter_point

        new_rates = None
        if ((current.minute % 30) == 0 or 
            DATA_RATES not in hass.data[DOMAIN] or
            hass.data[DOMAIN][DATA_RATES] is None or
            key not in hass.data[DOMAIN][DATA_RATES] or
            hass.data[DOMAIN][DATA_RATES][key][-1]["valid_from"] < period_from):
          try:
            new_rates = await client.async_get_electricity_rates(tariff_code, is_smart_meter, period_from, period_to)
          except:
            _LOGGER.debug('Failed to retrieve electricity rates')
        else:
            new_rates = hass.data[DOMAIN][DATA_RATES][key]
          
        if new_rates is not None:
          if dispatches is not None:
            rates[key] = adjust_intelligent_rates(new_rates, 
                                                  dispatches["planned"] if "planned" in dispatches else [],
                                                  dispatches["completed"] if "completed" in dispatches else [])
            
            _LOGGER.debug(f"Rates adjusted: {rates[key]}; dispatches: {dispatches}")
          else:
            rates[key] = new_rates
        elif (DATA_RATES in hass.data[DOMAIN] and key in hass.data[DOMAIN][DATA_RATES]):
          _LOGGER.debug(f"Failed to retrieve new rates for {tariff_code}, so using cached rates")
          rates[key] = hass.data[DOMAIN][DATA_RATES][key]
      
      hass.data[DOMAIN][DATA_RATES] = rates
    
    return hass.data[DOMAIN][DATA_RATES]

  hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="rates",
    update_method=async_update_electricity_rates_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

  await hass.data[DOMAIN][DATA_ELECTRICITY_RATES_COORDINATOR].async_config_entry_first_refresh()