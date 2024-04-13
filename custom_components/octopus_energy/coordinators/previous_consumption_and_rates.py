from datetime import datetime, timedelta
import logging
from typing import Callable, Any
import asyncio

from homeassistant.util.dt import (utcnow, now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_ACCOUNT,
  DOMAIN,
  DATA_INTELLIGENT_DISPATCHES,
  EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES,
  EVENT_GAS_PREVIOUS_CONSUMPTION_RATES,
  MINIMUM_CONSUMPTION_DATA_LENGTH,
  REFRESH_RATE_IN_MINUTES_PREVIOUS_CONSUMPTION
)

from ..api_client import (ApiException, OctopusEnergyApiClient)
from ..api_client.intelligent_dispatches import IntelligentDispatches
from ..utils import private_rates_to_public_rates

from ..intelligent import adjust_intelligent_rates, is_intelligent_tariff
from ..coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult
from . import BaseCoordinatorResult, get_electricity_meter_tariff_code, get_gas_meter_tariff_code
from ..utils.rate_information import get_min_max_average_rates

_LOGGER = logging.getLogger(__name__)

def __get_interval_end(item):
    return item["end"]

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_interval_end)
  return sorted

class PreviousConsumptionCoordinatorResult(BaseCoordinatorResult):
  consumption: list
  rates: list
  latest_available_timestamp: datetime
  standing_charge: float

  def __init__(self, last_retrieved: datetime, request_attempts: int, consumption: list, rates: list, standing_charge, latest_available_timestamp: datetime = None):
    super().__init__(last_retrieved, request_attempts, REFRESH_RATE_IN_MINUTES_PREVIOUS_CONSUMPTION)
    self.consumption = consumption
    self.rates = rates
    self.standing_charge = standing_charge
    self.latest_available_timestamp = latest_available_timestamp

async def async_fetch_consumption_and_rates(
  previous_data: PreviousConsumptionCoordinatorResult,
  current: datetime,
  account_info,
  client: OctopusEnergyApiClient,
  period_from: datetime,
  period_to: datetime,
  identifier: str,
  serial_number: str,
  is_electricity: bool,
  is_smart_meter: bool,
  fire_event: Callable[[str, "dict[str, Any]"], None],
  intelligent_dispatches: IntelligentDispatches = None,
  tariff_override = None

):
  """Fetch the previous consumption and rates"""

  if (account_info is None):
    return previous_data

  if (previous_data == None or 
      current >= previous_data.next_refresh):
    _LOGGER.debug(f"Retrieving previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}...")
    
    try:
      if (is_electricity == True):
        tariff_code = get_electricity_meter_tariff_code(period_from, account_info, identifier, serial_number) if tariff_override is None else None
        if tariff_code is None:
          _LOGGER.error(f"Could not determine tariff code for previous consumption for electricity {identifier}/{serial_number}")
          return previous_data

        # We'll calculate the wrong value if we don't have our intelligent dispatches
        if is_intelligent_tariff(tariff_code) and intelligent_dispatches is None:
          return previous_data

        [consumption_data, latest_consumption_data, rate_data, standing_charge] = await asyncio.gather(
          client.async_get_electricity_consumption(identifier, serial_number, period_from, period_to),
          client.async_get_electricity_consumption(identifier, serial_number, None, None, 1),
          client.async_get_electricity_rates(tariff_code, is_smart_meter, period_from, period_to),
          client.async_get_electricity_standing_charge(tariff_code, period_from, period_to)
        )

        if intelligent_dispatches is not None:
          _LOGGER.debug(f"Adjusting rate data based on intelligent tariff; dispatches: {intelligent_dispatches}")
          rate_data = adjust_intelligent_rates(rate_data,
                                                intelligent_dispatches.planned,
                                                intelligent_dispatches.completed)
      else:
        tariff_code = get_gas_meter_tariff_code(period_from, account_info, identifier, serial_number) if tariff_override is None else None
        if tariff_code is None:
          _LOGGER.error(f"Could not determine tariff code for previous consumption for gas {identifier}/{serial_number}")
          return previous_data

        [consumption_data, latest_consumption_data, rate_data, standing_charge] = await asyncio.gather(
          client.async_get_gas_consumption(identifier, serial_number, period_from, period_to),
          client.async_get_gas_consumption(identifier, serial_number, None, None, 1),
          client.async_get_gas_rates(tariff_code, period_from, period_to),
          client.async_get_gas_standing_charge(tariff_code, period_from, period_to)
        )
      
      if consumption_data is not None and len(consumption_data) >= MINIMUM_CONSUMPTION_DATA_LENGTH and rate_data is not None and len(rate_data) > 0 and standing_charge is not None:
        _LOGGER.debug(f"Discovered previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}")
        consumption_data = __sort_consumption(consumption_data)

        public_rates = private_rates_to_public_rates(rate_data)
        min_max_average_rates = get_min_max_average_rates(public_rates)

        if (is_electricity == True):
          fire_event(EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES, { "mpan": identifier, "serial_number": serial_number, "tariff_code": tariff_code, "rates": public_rates, "min_rate": min_max_average_rates["min"], "max_rate": min_max_average_rates["max"], "average_rate": min_max_average_rates["average"] })
        else:
          fire_event(EVENT_GAS_PREVIOUS_CONSUMPTION_RATES, { "mprn": identifier, "serial_number": serial_number, "tariff_code": tariff_code, "rates": public_rates, "min_rate": min_max_average_rates["min"], "max_rate": min_max_average_rates["max"], "average_rate": min_max_average_rates["average"] })

        _LOGGER.debug(f"Fired event for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}")

        return PreviousConsumptionCoordinatorResult(
          current,
          1,
          consumption_data,
          rate_data,
          standing_charge["value_inc_vat"],
          latest_consumption_data[-1]["end"] if latest_consumption_data is not None and len(latest_consumption_data) > 0 else None
        )
      
      return PreviousConsumptionCoordinatorResult(
        current,
        1,
        previous_data.consumption if previous_data is not None else None,
        previous_data.rates if previous_data is not None else None,
        previous_data.standing_charge if previous_data is not None else None,
        latest_consumption_data[-1]["end"]
        if latest_consumption_data is not None and len(latest_consumption_data) > 0
        else previous_data.latest_available_timestamp if previous_data is not None else None
      )
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      
      result = None
      if previous_data is not None:
        result =  PreviousConsumptionCoordinatorResult(
          previous_data.last_retrieved,
          previous_data.request_attempts + 1,
          previous_data.consumption,
          previous_data.rates,
          previous_data.standing_charge,
          previous_data.latest_available_timestamp
        )
        _LOGGER.warning(f"Failed to retrieve previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number} - using cached data. Next attempt at {result.next_refresh}")
      else:
        result = PreviousConsumptionCoordinatorResult(
          # We want to force into our fallback mode
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_PREVIOUS_CONSUMPTION),
          2,
          None,
          None,
          None,
          None
        )
        _LOGGER.warning(f"Failed to retrieve previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}. Next attempt at {result.next_refresh}")

      return result

  return previous_data 

async def async_create_previous_consumption_and_rates_coordinator(
    hass,
    account_id: str,
    client: OctopusEnergyApiClient,
    identifier: str,
    serial_number: str,
    is_electricity: bool,
    is_smart_meter: bool,
    days_offset: int,
    tariff_override = None):
  """Create reading coordinator"""
  previous_consumption_data_key = f'{identifier}_{serial_number}_previous_consumption_and_rates'

  async def async_update_data():
    """Fetch data from API endpoint."""
    period_from = as_utc((now() - timedelta(days=days_offset)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = period_from + timedelta(days=1)
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN][account_id] else None
    account_info = account_result.account if account_result is not None else None
    dispatches: IntelligentDispatchesCoordinatorResult = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES] if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN][account_id] else None
    
    result = await async_fetch_consumption_and_rates(
      hass.data[DOMAIN][account_id][previous_consumption_data_key] if previous_consumption_data_key in hass.data[DOMAIN][account_id] else None,
      utcnow(),
      account_info,
      client,
      period_from,
      period_to,
      identifier,
      serial_number,
      is_electricity,
      is_smart_meter,
      hass.bus.async_fire,
      dispatches.dispatches if dispatches is not None else None
    )

    if (result is not None):
      hass.data[DOMAIN][account_id][previous_consumption_data_key] = result

    if previous_consumption_data_key in hass.data[DOMAIN][account_id]:
      return hass.data[DOMAIN][account_id][previous_consumption_data_key] 
    else:
      return None

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=previous_consumption_data_key,
    update_method=async_update_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  hass.data[DOMAIN][account_id][f'{identifier}_{serial_number}_previous_consumption_and_cost_coordinator'] = coordinator

  return coordinator