from datetime import datetime, timedelta
import logging
from typing import Awaitable, Callable, Any
import asyncio

from custom_components.octopus_energy.utils.attributes import dict_to_typed_dict
from homeassistant.util.dt import (utcnow, now, as_utc, as_local)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from homeassistant.helpers import storage

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_ACCOUNT,
  DATA_INTELLIGENT_DEVICE,
  DATA_PREVIOUS_CONSUMPTION_COORDINATOR_KEY,
  DOMAIN,
  DATA_INTELLIGENT_DISPATCHES,
  EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES,
  EVENT_GAS_PREVIOUS_CONSUMPTION_RATES,
  MINIMUM_CONSUMPTION_DATA_LENGTH,
  REFRESH_RATE_IN_MINUTES_PREVIOUS_CONSUMPTION
)

from ..api_client import (ApiException, OctopusEnergyApiClient)
from ..api_client.intelligent_dispatches import IntelligentDispatches
from ..api_client.intelligent_device import IntelligentDevice
from ..utils import Tariff, private_rates_to_public_rates

from ..intelligent import adjust_intelligent_rates, is_intelligent_product
from ..coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult
from . import BaseCoordinatorResult, get_electricity_meter_tariff, get_gas_meter_tariff
from ..utils.rate_information import get_min_max_average_rates
from ..octoplus import get_saving_session_weekday_dates, get_saving_session_weekend_dates, SavingSessionConsumptionDate

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
  historic_weekday_rates: list
  historic_weekend_rates: list

  def __init__(self,
               last_retrieved: datetime,
               request_attempts: int,
               consumption: list,
               rates: list,
               standing_charge,
               latest_available_timestamp: datetime = None,
               historic_weekday_rates: list = None,
               historic_weekend_rates: list = None):
    super().__init__(last_retrieved, request_attempts, REFRESH_RATE_IN_MINUTES_PREVIOUS_CONSUMPTION)
    self.consumption = consumption
    self.rates = rates
    self.standing_charge = standing_charge
    self.latest_available_timestamp = latest_available_timestamp
    self.historic_weekday_rates = historic_weekday_rates
    self.historic_weekend_rates = historic_weekend_rates

def contains_rate(rates: list, current_rate):
  for rate in rates:
    if rate["start"] == current_rate["start"]:
      return True
  
  return False

def extract_missing_rate_periods(target_consumption_dates: list[SavingSessionConsumptionDate], rates: list):
  new_target_consumption_dates = []
  for consumption_date in target_consumption_dates:
    rates_count = 0
    for rate in rates:
      if rate["start"] >= consumption_date.start and rate["start"] <= consumption_date.end and rate["end"] >= consumption_date.start and rate["end"] <= consumption_date.end:
        rates_count += 1

      if rates_count >= 48:
        break

    if rates_count < 48:
      new_target_consumption_dates.append(consumption_date)

  return new_target_consumption_dates

async def async_get_missing_rates(
    client: OctopusEnergyApiClient,
    identifier: str,
    serial_number: str,
    rates: list,
    consumption_dates: list[SavingSessionConsumptionDate]
  ):
  try:
    requests = []
    for consumption_date in consumption_dates:
      _LOGGER.debug(f"Retrieving historic rates for '{identifier}/{serial_number}' between {consumption_date.start} and {consumption_date.end}")
      requests.append(client.async_get_electricity_consumption(identifier,
                                                               serial_number,
                                                               consumption_date.start,
                                                               consumption_date.end))
    consumption_data_responses = await asyncio.gather(*requests)
    consumption_data = [
      x
      for xs in consumption_data_responses
      for x in xs
    ]

    rates.extend(consumption_data)
    _LOGGER.debug(f"rates: {len(rates)}")
    return rates
  except Exception as e:
    if isinstance(e, ApiException) == False:
      _LOGGER.error(e)
      raise

def remove_old_rates(rates: list, earliest_datetime: datetime):
  _LOGGER.debug(f"earliest_datetime: {earliest_datetime}")
  new_rates = []
  for rate in rates:
    if (rate["start"] >= earliest_datetime):
      new_rates.append(rate)

  return new_rates

async def async_enhance_with_historic_rates(
    current: datetime,
    client: OctopusEnergyApiClient,
    data: PreviousConsumptionCoordinatorResult,
    previous_data: PreviousConsumptionCoordinatorResult | None,
    identifier: str,
    serial_number: str,
    async_load_historic_rates: Callable[[str, str, bool], Awaitable[list]],
    async_save_historic_rates: Callable[[str, str, bool, list], Awaitable[None]]
  ):
  """Fetch the historic rates"""

  if data.rates is None or (previous_data is not None and previous_data.last_retrieved == data.last_retrieved):
    return data

  # Determine what our existing historic rates are
  historic_weekday_rates = previous_data.historic_weekday_rates if previous_data is not None else []
  if historic_weekday_rates is None:
    historic_weekday_rates = await async_load_historic_rates(identifier, serial_number, True)

  previous_weekday_earliest_start = historic_weekday_rates[0]["start"] if historic_weekday_rates is not None and len(historic_weekday_rates) > 0 else None
  previous_weekday_latest_end = historic_weekday_rates[-1]["end"] if historic_weekday_rates is not None and len(historic_weekday_rates) > 0 else None

  historic_weekend_rates = previous_data.historic_weekend_rates if previous_data is not None else []
  if historic_weekend_rates is None:
    historic_weekend_rates = await async_load_historic_rates(identifier, serial_number, False)

  previous_weekend_earliest_start = historic_weekend_rates[0]["start"] if historic_weekend_rates is not None and len(historic_weekend_rates) > 0 else None
  previous_weekend_latest_end = historic_weekend_rates[-1]["end"] if historic_weekend_rates is not None and len(historic_weekend_rates) > 0 else None

  # Add our new rates if they don't already exist
  for rate in data.rates:
    local_start: datetime = as_local(rate["start"])
    is_weekend = local_start.weekday() == 5 or local_start.weekday() == 6
    if is_weekend and contains_rate(historic_weekend_rates, rate):
      historic_weekend_rates.append(rate)
    elif is_weekend == False and contains_rate(historic_weekday_rates, rate):
      historic_weekday_rates.append(rate)

  # Fetch rates that might be missing
  local_start = as_local(current).replace(hour=0, minute=0, second=0, microsecond=0)
  weekday_periods = get_saving_session_weekday_dates(local_start, 15, timedelta(hours=24), [])
  earliest_weekday_start = weekday_periods[-1].start
  missing_weekday_rates = extract_missing_rate_periods(weekday_periods, historic_weekday_rates)

  weekend_periods = get_saving_session_weekend_dates(local_start, 8, timedelta(hours=24), [])
  earliest_weekend_start = weekend_periods[-1].start
  missing_weekend_rates = extract_missing_rate_periods(weekend_periods, historic_weekend_rates)

  historic_weekday_rates = await async_get_missing_rates(client, identifier, serial_number, historic_weekday_rates, missing_weekday_rates)
  historic_weekend_rates = await async_get_missing_rates(client, identifier, serial_number, historic_weekend_rates, missing_weekend_rates)

  historic_weekday_rates = remove_old_rates(historic_weekday_rates, earliest_weekday_start)
  historic_weekend_rates = remove_old_rates(historic_weekend_rates, earliest_weekend_start)

  historic_weekday_rates.sort(key=lambda x: x["start"])
  historic_weekend_rates.sort(key=lambda x: x["start"])

  current_weekday_earliest_start = historic_weekday_rates[0]["start"] if historic_weekday_rates is not None and len(historic_weekday_rates) > 0 else None
  current_weekday_latest_end = historic_weekday_rates[-1]["end"] if historic_weekday_rates is not None and len(historic_weekday_rates) > 0 else None

  current_weekend_earliest_start = historic_weekend_rates[0]["start"] if historic_weekend_rates is not None and len(historic_weekend_rates) > 0 else None
  current_weekend_latest_end = historic_weekend_rates[-1]["end"] if historic_weekend_rates is not None and len(historic_weekend_rates) > 0 else None

  if current_weekday_earliest_start != previous_weekday_earliest_start or current_weekday_latest_end != previous_weekday_latest_end or len(missing_weekday_rates) > 0:
    await async_save_historic_rates(identifier, serial_number, True, historic_weekday_rates)

  if current_weekend_earliest_start != previous_weekend_earliest_start or current_weekend_latest_end != previous_weekend_latest_end or len(missing_weekend_rates) > 0:
    await async_save_historic_rates(identifier, serial_number, False, historic_weekend_rates)

  return PreviousConsumptionCoordinatorResult(
    data.last_retrieved,
    data.request_attempts,
    data.consumption,
    data.rates,
    data.standing_charge,
    data.latest_available_timestamp,
    historic_weekday_rates,
    historic_weekend_rates
  )

async def async_fetch_consumption_and_rates(
  previous_data: PreviousConsumptionCoordinatorResult | None,
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
  intelligent_device: IntelligentDevice | None = None,
  intelligent_dispatches: IntelligentDispatches | None = None,
  tariff_override: Tariff = None

):
  """Fetch the previous consumption and rates"""

  if (account_info is None):
    return previous_data

  if (previous_data == None or 
      current >= previous_data.next_refresh):
    _LOGGER.debug(f"Retrieving previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}...")
    
    try:
      if (is_electricity == True):
        tariff = get_electricity_meter_tariff(period_from, account_info, identifier, serial_number) if tariff_override is None else tariff_override
        if tariff is None:
          _LOGGER.error(f"Could not determine tariff code for previous consumption for electricity {identifier}/{serial_number}")
          return previous_data

        # We'll calculate the wrong value if we don't have our intelligent dispatches
        if is_intelligent_product(tariff.product) and intelligent_device is not None and intelligent_dispatches is None:
          _LOGGER.debug("Dispatches not available for intelligent tariff. Using existing rate information")
          return previous_data

        [consumption_data, latest_consumption_data, rate_data, standing_charge] = await asyncio.gather(
          client.async_get_electricity_consumption(identifier, serial_number, period_from, period_to),
          client.async_get_electricity_consumption(identifier, serial_number, None, None, 1),
          client.async_get_electricity_rates(tariff.product, tariff.code, is_smart_meter, period_from, period_to),
          client.async_get_electricity_standing_charge(tariff.product, tariff.code, period_from, period_to)
        )

        if intelligent_dispatches is not None:
          _LOGGER.debug(f"Adjusting rate data based on intelligent tariff; dispatches: {intelligent_dispatches}")
          rate_data = adjust_intelligent_rates(rate_data,
                                                intelligent_dispatches.planned,
                                                intelligent_dispatches.completed)
      else:
        tariff = get_gas_meter_tariff(period_from, account_info, identifier, serial_number) if tariff_override is None else tariff_override
        if tariff is None:
          _LOGGER.error(f"Could not determine tariff code for previous consumption for gas {identifier}/{serial_number}")
          return previous_data

        [consumption_data, latest_consumption_data, rate_data, standing_charge] = await asyncio.gather(
          client.async_get_gas_consumption(identifier, serial_number, period_from, period_to),
          client.async_get_gas_consumption(identifier, serial_number, None, None, 1),
          client.async_get_gas_rates(tariff.product, tariff.code, period_from, period_to),
          client.async_get_gas_standing_charge(tariff.product, tariff.code, period_from, period_to)
        )
      
      if consumption_data is not None and len(consumption_data) >= MINIMUM_CONSUMPTION_DATA_LENGTH and rate_data is not None and len(rate_data) > 0 and standing_charge is not None:
        _LOGGER.debug(f"Discovered previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}")
        consumption_data = __sort_consumption(consumption_data)

        public_rates = private_rates_to_public_rates(rate_data)
        min_max_average_rates = get_min_max_average_rates(public_rates)

        if (is_electricity == True):
          fire_event(EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES, { "mpan": identifier, "serial_number": serial_number, "tariff_code": tariff.code, "rates": public_rates, "min_rate": min_max_average_rates["min"], "max_rate": min_max_average_rates["max"], "average_rate": min_max_average_rates["average"] })
        else:
          fire_event(EVENT_GAS_PREVIOUS_CONSUMPTION_RATES, { "mprn": identifier, "serial_number": serial_number, "tariff_code": tariff.code, "rates": public_rates, "min_rate": min_max_average_rates["min"], "max_rate": min_max_average_rates["max"], "average_rate": min_max_average_rates["average"] })

        _LOGGER.debug(f"Fired event for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}")

        return PreviousConsumptionCoordinatorResult(
          current,
          1,
          consumption_data,
          rate_data,
          standing_charge["value_inc_vat"],
          latest_consumption_data[-1]["end"] if latest_consumption_data is not None and len(latest_consumption_data) > 0 else None,
          [],
          []
        )
      
      return PreviousConsumptionCoordinatorResult(
        current,
        1,
        previous_data.consumption if previous_data is not None else None,
        previous_data.rates if previous_data is not None else None,
        previous_data.standing_charge if previous_data is not None else None,
        latest_consumption_data[-1]["end"]
        if latest_consumption_data is not None and len(latest_consumption_data) > 0
        else previous_data.latest_available_timestamp if previous_data is not None else None,
        previous_data.historic_weekday_rates if previous_data is not None else None,
        previous_data.historic_weekend_rates if previous_data is not None else None
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
          previous_data.latest_available_timestamp,
          previous_data.historic_weekday_rates,
          previous_data.historic_weekend_rates
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
    tariff_override: Tariff = None):
  """Create reading coordinator"""
  previous_consumption_data_key = f'{identifier}_{serial_number}_previous_consumption_and_rates'

  async def async_load_historic_rates(identifier: str, serial_number: str, is_weekday: bool):
    weekend_weekday_suffix = "weekday" if is_weekday else "weekend"
    store = storage.Store(hass, "1", f"octopus_energy.{identifier}_{serial_number}_{weekend_weekday_suffix}")

    try:
      data = await store.async_load()
      rates = []
      if data is not None:
        for item in data:
          rates.append(dict_to_typed_dict(item))

      return rates
    except:
      return []
    
  async def async_save_historic_rates(identifier: str, serial_number: str, is_weekday: bool, rates: list):
    weekend_weekday_suffix = "weekday" if is_weekday else "weekend"
    store = storage.Store(hass, "1", f"octopus_energy.{identifier}_{serial_number}_{weekend_weekday_suffix}")
    await store.async_save(rates)

  async def async_update_data():
    """Fetch data from API endpoint."""
    period_from = as_utc((now() - timedelta(days=days_offset)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = period_from + timedelta(days=1)
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN][account_id] else None
    account_info = account_result.account if account_result is not None else None
    intelligent_device: IntelligentDevice | None = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE] if DATA_INTELLIGENT_DEVICE in hass.data[DOMAIN][account_id] else None
    dispatches: IntelligentDispatchesCoordinatorResult = hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DISPATCHES] if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN][account_id] else None
    previous_data = hass.data[DOMAIN][account_id][previous_consumption_data_key] if previous_consumption_data_key in hass.data[DOMAIN][account_id] else None
    current = utcnow()

    result = await async_fetch_consumption_and_rates(
      previous_data,
      current,
      account_info,
      client,
      period_from,
      period_to,
      identifier,
      serial_number,
      is_electricity,
      is_smart_meter,
      hass.bus.async_fire,
      intelligent_device,
      dispatches.dispatches if dispatches is not None else None,
      tariff_override
    )

    if (result is not None):
      hass.data[DOMAIN][account_id][previous_consumption_data_key] = result

      if is_electricity:
        # We'll build up historic rate information needed by saving sessions, free electricity, etc at the same time to try
        # and reduce load on the OE APIs. We need to store this locally in 30 minute increments due to the calculations, so
        # statistical data isn't good enough
        hass.data[DOMAIN][account_id][previous_consumption_data_key] = await async_enhance_with_historic_rates(
          current,
          client,
          result,
          previous_data,
          identifier,
          serial_number,
          async_load_historic_rates,
          async_save_historic_rates
        )

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

  hass.data[DOMAIN][account_id][DATA_PREVIOUS_CONSUMPTION_COORDINATOR_KEY.format(identifier, serial_number)] = coordinator

  return coordinator