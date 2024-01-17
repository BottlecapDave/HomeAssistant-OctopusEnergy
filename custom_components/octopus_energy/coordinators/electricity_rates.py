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
from ..coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult
from ..utils import private_rates_to_public_rates
from . import BaseCoordinatorResult, get_electricity_meter_tariff_code, raise_rate_events
from ..intelligent import adjust_intelligent_rates

_LOGGER = logging.getLogger(__name__)

class ElectricityRatesCoordinatorResult(BaseCoordinatorResult):
  rates: list
  original_rates: list
  rates_last_adjusted: datetime

  def __init__(self, last_retrieved: datetime, request_attempts: int, rates: list, original_rates: list = None, rates_last_adjusted: datetime = None):
    super().__init__(last_retrieved, request_attempts, REFRESH_RATE_IN_MINUTES_RATES)
    self.rates = rates
    self.original_rates = original_rates if original_rates is not None else rates
    self.rates_last_adjusted = rates_last_adjusted if rates_last_adjusted else last_retrieved

async def async_refresh_electricity_rates_data(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_info,
    target_mpan: str,
    target_serial_number: str,
    is_smart_meter: bool,
    is_export_meter: bool,
    existing_rates_result: ElectricityRatesCoordinatorResult,
    dispatches_result: IntelligentDispatchesCoordinatorResult,
    planned_dispatches_supported: bool,
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
          raise
        
        _LOGGER.debug(f'Failed to retrieve electricity rates for {target_mpan}/{target_serial_number} ({tariff_code})')
      
      if new_rates is not None:
        _LOGGER.debug(f'Electricity rates retrieved for {target_mpan}/{target_serial_number} ({tariff_code});')
        
        original_rates = new_rates.copy()
        original_rates.sort(key=lambda rate: rate["start"])
        
        if dispatches_result is not None and dispatches_result.dispatches is not None and is_export_meter == False:
          new_rates = adjust_intelligent_rates(new_rates,
                                               dispatches_result.dispatches.planned if planned_dispatches_supported else [],
                                               dispatches_result.dispatches.completed)
          
          _LOGGER.debug(f"Rates adjusted: {new_rates}; dispatches: {dispatches_result.dispatches}")

        # Sort our rates again _just in case_
        new_rates.sort(key=lambda rate: rate["start"])
        
        raise_rate_events(current,
                          private_rates_to_public_rates(new_rates),
                          { "mpan": target_mpan, "serial_number": target_serial_number, "tariff_code": tariff_code },
                          fire_event,
                          EVENT_ELECTRICITY_PREVIOUS_DAY_RATES,
                          EVENT_ELECTRICITY_CURRENT_DAY_RATES,
                          EVENT_ELECTRICITY_NEXT_DAY_RATES)
        
        return ElectricityRatesCoordinatorResult(current, 1, new_rates, original_rates, current)
      
      result = None
      if (existing_rates_result is not None):
        result = ElectricityRatesCoordinatorResult(
          existing_rates_result.last_retrieved,
          existing_rates_result.request_attempts + 1,
          existing_rates_result.rates,
          existing_rates_result.original_rates,
          existing_rates_result.rates_last_adjusted
        )
        _LOGGER.warning(f"Failed to retrieve new electricity rates for {target_mpan}/{target_serial_number} - using cached rates. Next attempt at {result.next_refresh}")
      else:
        # We want to force into our fallback mode
        result = ElectricityRatesCoordinatorResult(
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES),
          2,
          None,
          None,
          None
        )
        _LOGGER.warning(f"Failed to retrieve new electricity rates for {target_mpan}/{target_serial_number}. Next attempt at {result.next_refresh}")

      return result
    
    # While we might have updated completed dispatches when planned dispatches isn't supported, 
    # these can wait as they only power previous consumption costs which can be recalculated with a delay
    elif (is_export_meter == False and planned_dispatches_supported == True and existing_rates_result is not None and dispatches_result is not None and dispatches_result.last_retrieved > existing_rates_result.rates_last_adjusted):
      new_rates = adjust_intelligent_rates(existing_rates_result.original_rates,
                                           dispatches_result.dispatches.planned,
                                           dispatches_result.dispatches.completed)
      
      _LOGGER.debug(f"Rates adjusted: {new_rates}; dispatches: {dispatches_result.dispatches}")

      # Sort our rates again _just in case_
      new_rates.sort(key=lambda rate: rate["start"])
      
      raise_rate_events(current,
                        private_rates_to_public_rates(new_rates),
                        { "mpan": target_mpan, "serial_number": target_serial_number, "tariff_code": tariff_code, "intelligent_dispatches_updated": True },
                        fire_event,
                        EVENT_ELECTRICITY_PREVIOUS_DAY_RATES,
                        EVENT_ELECTRICITY_CURRENT_DAY_RATES,
                        EVENT_ELECTRICITY_NEXT_DAY_RATES)
      
      return ElectricityRatesCoordinatorResult(
        existing_rates_result.last_retrieved,
        existing_rates_result.request_attempts,
        new_rates,
        existing_rates_result.original_rates,
        current
      )
  return existing_rates_result

async def async_setup_electricity_rates_coordinator(hass, account_id: str, target_mpan: str, target_serial_number: str, is_smart_meter: bool, is_export_meter: bool, planned_dispatches_supported: bool):
  key = DATA_ELECTRICITY_RATES_KEY.format(target_mpan, target_serial_number)

  # Reset data rates as we might have new information
  hass.data[DOMAIN][account_id][key] = None
  
  async def async_update_electricity_rates_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN][account_id] else None
    account_info = account_result.account if account_result is not None else None
    dispatches: IntelligentDispatchesCoordinatorResult = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES] if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN][account_id] else None
    rates = hass.data[DOMAIN][account_id][key] if key in hass.data[DOMAIN][account_id] else None

    hass.data[DOMAIN][account_id][key] = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      target_mpan,
      target_serial_number,
      is_smart_meter,
      is_export_meter,
      rates,
      dispatches,
      planned_dispatches_supported,
      hass.bus.async_fire
    )

    return hass.data[DOMAIN][account_id][key]

  coordinator_key = DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(target_mpan, target_serial_number)
  hass.data[DOMAIN][account_id][coordinator_key] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=key,
    update_method=async_update_electricity_rates_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )