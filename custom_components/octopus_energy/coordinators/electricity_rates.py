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
  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DATA_ELECTRICITY_RATES_KEY,
  DATA_ACCOUNT,
  DATA_INTELLIGENT_DISPATCHES,
  EVENT_ELECTRICITY_CURRENT_DAY_RATES,
  EVENT_ELECTRICITY_NEXT_DAY_RATES,
  EVENT_ELECTRICITY_PREVIOUS_DAY_RATES,
)

from ..api_client import OctopusEnergyApiClient

from . import raise_rate_events
from ..intelligent import adjust_intelligent_rates

_LOGGER = logging.getLogger(__name__)

class ElectricityRatesCoordinatorResult:
  last_retrieved: datetime
  rates: list

  def __init__(self, last_retrieved: datetime, rates: list):
    self.last_retrieved = last_retrieved
    self.rates = rates

def get_tariff_code_and_is_smart_meter(current: datetime, account_info, target_mpan: str, target_serial_number: str):
  if len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff_code = get_active_tariff_code(current, point["agreements"])
      # The type of meter (ie smart vs dumb) can change the tariff behaviour, so we
      # have to enumerate the different meters being used for each tariff as well.
      for meter in point["meters"]:
        if active_tariff_code is not None and point["mpan"] == target_mpan and meter["serial_number"] == target_serial_number:
           return (active_tariff_code, meter["is_smart_meter"])
           
  return None

async def async_refresh_electricity_rates_data(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_info,
    target_mpan: str,
    target_serial_number: str,
    existing_rates_result: ElectricityRatesCoordinatorResult,
    dispatches: list,
    fire_event: Callable[[str, "dict[str, Any]"], None],
  ) -> ElectricityRatesCoordinatorResult: 
  if (account_info is not None):
    period_from = as_utc((current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = as_utc((current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0))

    result = get_tariff_code_and_is_smart_meter(current, account_info, target_mpan, target_serial_number)
    if result is None:
      return None

    new_rates: list = None
    if ((current.minute % 30) == 0 or 
        existing_rates_result is None or
        existing_rates_result.rates[-1]["valid_from"] < period_from):
      try:
        new_rates = await client.async_get_electricity_rates(result[0], result[1], period_from, period_to)
      except:
        _LOGGER.debug(f'Failed to retrieve electricity rates for {target_mpan}/{target_serial_number} ({result[0]})')
      
    if new_rates is not None:
      _LOGGER.debug(f'Electricity rates retrieved for {target_mpan}/{target_serial_number} ({result[0]});')
      
      if dispatches is not None:
        new_rates = adjust_intelligent_rates(new_rates, 
                                             dispatches["planned"] if "planned" in dispatches else [],
                                             dispatches["completed"] if "completed" in dispatches else [])
        
        _LOGGER.debug(f"Rates adjusted: {new_rates}; dispatches: {dispatches}")

      raise_rate_events(current,
                        new_rates,
                        { "mpan": target_mpan, "serial_number": target_serial_number, "tariff_code": result[0] },
                        fire_event,
                        EVENT_ELECTRICITY_PREVIOUS_DAY_RATES,
                        EVENT_ELECTRICITY_CURRENT_DAY_RATES,
                        EVENT_ELECTRICITY_NEXT_DAY_RATES)
      
      return ElectricityRatesCoordinatorResult(current, new_rates)

    elif (existing_rates_result is not None):
      _LOGGER.debug(f"Failed to retrieve new electricity rates for {target_mpan}/{target_serial_number}, so using cached rates")
  
  return existing_rates_result

async def async_setup_electricity_rates_coordinator(hass, target_mpan: str, target_serial_number: str):
  key = DATA_ELECTRICITY_RATES_KEY.format(target_mpan, target_serial_number)

  # Reset data rates as we might have new information
  hass.data[DOMAIN][key] = None
  
  async def async_update_electricity_rates_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    account_info = hass.data[DOMAIN][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN] else None
    dispatches = hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES] if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN] else None
    rates = hass.data[DOMAIN][key] if key in hass.data[DOMAIN] else None

    hass.data[DOMAIN][key] = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      target_mpan,
      target_serial_number,
      rates,
      dispatches,
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
  )

  await hass.data[DOMAIN][coordinator_key].async_config_entry_first_refresh()