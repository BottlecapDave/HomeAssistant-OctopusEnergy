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
  DATA_CLIENT,
  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DATA_ELECTRICITY_RATES_KEY,
  DATA_ACCOUNT,
  DATA_INTELLIGENT_DISPATCHES,
  EVENT_ELECTRICITY_CURRENT_DAY_RATES,
  EVENT_ELECTRICITY_NEXT_DAY_RATES,
  EVENT_ELECTRICITY_PREVIOUS_DAY_RATES,
  REFRESH_RATE_IN_MINUTES_RATES,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.intelligent_dispatches import IntelligentDispatches
from ..coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult
from ..utils import private_rates_to_public_rates
from . import BaseCoordinatorResult, get_electricity_meter_tariff_code, raise_rate_events
from ..intelligent import adjust_intelligent_rates

_LOGGER = logging.getLogger(__name__)

class ElectricityRatesCoordinatorResult(BaseCoordinatorResult):
  rates: list

  def __init__(self, last_retrieved: datetime, request_attempts: int, rates: list):
    super().__init__(last_retrieved, request_attempts, REFRESH_RATE_IN_MINUTES_RATES)
    self.rates = rates

async def async_refresh_electricity_rates_data(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_info,
    target_mpan: str,
    target_serial_number: str,
    is_smart_meter: bool,
    is_export_meter: bool,
    existing_rates_result: ElectricityRatesCoordinatorResult,
    dispatches: IntelligentDispatches,
    fire_event: Callable[[str, "dict[str, Any]"], None],
  ) -> ElectricityRatesCoordinatorResult: 
  if (account_info is not None):
    period_from = as_utc((current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = as_utc((current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0))

    tariff_code = get_electricity_meter_tariff_code(current, account_info, target_mpan, target_serial_number)
    if tariff_code is None:
      return None

    new_rates: list = None
    if (existing_rates_result is None or current >= existing_rates_result.next_refresh):
      try:
        new_rates = await client.async_get_electricity_rates(tariff_code, is_smart_meter, period_from, period_to)
      except Exception as e:
        if isinstance(e, ApiException) == False:
          _LOGGER.error(e)
          raise
        
        _LOGGER.debug(f'Failed to retrieve electricity rates for {target_mpan}/{target_serial_number} ({tariff_code})')
      
      if new_rates is not None:
        _LOGGER.debug(f'Electricity rates retrieved for {target_mpan}/{target_serial_number} ({tariff_code});')
        
        if dispatches is not None and is_export_meter == False:
          new_rates = adjust_intelligent_rates(new_rates, 
                                               dispatches.planned,
                                               dispatches.completed)
          
          _LOGGER.debug(f"Rates adjusted: {new_rates}; dispatches: {dispatches}")

        # Sort our rates again _just in case_
        new_rates.sort(key=lambda rate: rate["start"])
        
        raise_rate_events(current,
                          private_rates_to_public_rates(new_rates),
                          { "mpan": target_mpan, "serial_number": target_serial_number, "tariff_code": tariff_code },
                          fire_event,
                          EVENT_ELECTRICITY_PREVIOUS_DAY_RATES,
                          EVENT_ELECTRICITY_CURRENT_DAY_RATES,
                          EVENT_ELECTRICITY_NEXT_DAY_RATES)
        
        return ElectricityRatesCoordinatorResult(current, 1, new_rates)
      
      result = None
      if (existing_rates_result is not None):
        result = ElectricityRatesCoordinatorResult(existing_rates_result.last_retrieved, existing_rates_result.request_attempts + 1, existing_rates_result.rates)
        _LOGGER.warning(f"Failed to retrieve new electricity rates for {target_mpan}/{target_serial_number} - using cached rates. Next attempt at {result.next_refresh}")
      else:
        # We want to force into our fallback mode
        result = ElectricityRatesCoordinatorResult(current  - timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES), 2, None)
        _LOGGER.warning(f"Failed to retrieve new electricity rates for {target_mpan}/{target_serial_number}. Next attempt at {result.next_refresh}")

      return result
  
  return existing_rates_result

async def async_setup_electricity_rates_coordinator(hass, target_mpan: str, target_serial_number: str, is_smart_meter: bool, is_export_meter: bool):
  key = DATA_ELECTRICITY_RATES_KEY.format(target_mpan, target_serial_number)

  # Reset data rates as we might have new information
  hass.data[DOMAIN][key] = None
  
  async def async_update_electricity_rates_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    account_result = hass.data[DOMAIN][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN] else None
    account_info = account_result.account if account_result is not None else None
    dispatches: IntelligentDispatchesCoordinatorResult = hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES] if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN] else None
    rates = hass.data[DOMAIN][key] if key in hass.data[DOMAIN] else None

    hass.data[DOMAIN][key] = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      target_mpan,
      target_serial_number,
      is_smart_meter,
      is_export_meter,
      rates,
      dispatches.dispatches if dispatches is not None else None,
      hass.bus.async_fire
    )

    return hass.data[DOMAIN][key]

  coordinator_key = DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(target_mpan, target_serial_number)
  hass.data[DOMAIN][coordinator_key] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=key,
    update_method=async_update_electricity_rates_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  await hass.data[DOMAIN][coordinator_key].async_config_entry_first_refresh()