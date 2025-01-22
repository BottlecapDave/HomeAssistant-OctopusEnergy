from datetime import datetime, timedelta
import logging
from typing import Awaitable, Callable, Any
import asyncio

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
from ..octoplus import get_octoplus_session_weekday_dates, get_octoplus_session_weekend_dates, OctoplusSessionConsumptionDate

_LOGGER = logging.getLogger(__name__)

def __get_interval_end(item):
    return (item["end"].timestamp(), item["end"].fold)

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_interval_end)
  return sorted

class PreviousConsumptionCoordinatorResult(BaseCoordinatorResult):
  consumption: list
  rates: list
  standing_charge: float
  historic_weekday_consumption: list
  historic_weekend_consumption: list

  def __init__(self,
               last_evaluated: datetime,
               request_attempts: int,
               consumption: list,
               rates: list,
               standing_charge,
               historic_weekday_consumption: list = None,
               historic_weekend_consumption: list = None,
               last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_PREVIOUS_CONSUMPTION, None, last_error)
    self.consumption = consumption
    self.rates = rates
    self.standing_charge = standing_charge
    self.historic_weekday_consumption = historic_weekday_consumption
    self.historic_weekend_consumption = historic_weekend_consumption

def contains_consumption(consumptions: list, current_consumption):
  for consumption in consumptions:
    if consumption["start"] == current_consumption["start"]:
      return True
  
  return False

def extract_missing_consumption_periods(target_consumption_dates: list[OctoplusSessionConsumptionDate], consumptions: list):
  new_target_consumption_dates = []
  for consumption_date in target_consumption_dates:
    consumption_count = 0
    for consumption in consumptions:
      if consumption["start"] >= consumption_date.start and consumption["start"] <= consumption_date.end and consumption["end"] >= consumption_date.start and consumption["end"] <= consumption_date.end:
        consumption_count += 1

      if consumption_count >= 48:
        break

    if consumption_count < 48:
      new_target_consumption_dates.append(consumption_date)

  return new_target_consumption_dates

async def async_get_missing_consumption(
    client: OctopusEnergyApiClient,
    identifier: str,
    serial_number: str,
    consumptions: list,
    consumption_dates: list[OctoplusSessionConsumptionDate]
  ):
  try:
    requests = []
    for consumption_date in consumption_dates:
      _LOGGER.debug(f"Retrieving historic consumption for '{identifier}/{serial_number}' between {consumption_date.start} and {consumption_date.end}")
      requests.append(client.async_get_electricity_consumption(identifier,
                                                               serial_number,
                                                               consumption_date.start,
                                                               consumption_date.end))
    consumption_data_responses = await asyncio.gather(*requests)
    for response in consumption_data_responses:
      for response_consumption in response:
        if contains_consumption(consumptions, response_consumption) == False:
          consumptions.append(response_consumption)

    return consumptions
  except Exception as e:
    if isinstance(e, ApiException) == False:
      _LOGGER.error(e)
      raise

def remove_old_consumptions(consumptions: list, earliest_datetime: datetime):
  new_rates = []
  if consumptions is not None:
    for consumption in consumptions:
      if (consumption["start"] >= earliest_datetime):
        new_rates.append(consumption)

  return new_rates

async def async_enhance_with_historic_consumption(
    current: datetime,
    client: OctopusEnergyApiClient,
    data: PreviousConsumptionCoordinatorResult,
    previous_data: PreviousConsumptionCoordinatorResult | None,
    identifier: str,
    serial_number: str,
    async_load_historic_consumptions: Callable[[str, str, bool], Awaitable[list]],
    async_save_historic_consumptions: Callable[[str, str, bool, list], Awaitable[None]]
  ):
  """Fetch the historic rates"""

  if data.consumption is None or (previous_data is not None and previous_data.last_evaluated == data.last_evaluated):
    return data

  # Determine what our existing historic rates are
  historic_weekday_consumptions = previous_data.historic_weekday_consumption if previous_data is not None else None
  if historic_weekday_consumptions is None:
    historic_weekday_consumptions = await async_load_historic_consumptions(identifier, serial_number, True)

  previous_weekday_earliest_start = historic_weekday_consumptions[0]["start"] if historic_weekday_consumptions is not None and len(historic_weekday_consumptions) > 0 else None
  previous_weekday_latest_end = historic_weekday_consumptions[-1]["end"] if historic_weekday_consumptions is not None and len(historic_weekday_consumptions) > 0 else None

  historic_weekend_consumptions = previous_data.historic_weekend_consumption if previous_data is not None else None
  if historic_weekend_consumptions is None:
    historic_weekend_consumptions = await async_load_historic_consumptions(identifier, serial_number, False)

  previous_weekend_earliest_start = historic_weekend_consumptions[0]["start"] if historic_weekend_consumptions is not None and len(historic_weekend_consumptions) > 0 else None
  previous_weekend_latest_end = historic_weekend_consumptions[-1]["end"] if historic_weekend_consumptions is not None and len(historic_weekend_consumptions) > 0 else None

  # Add our new consumptions if they don't already exist and we have a full day of data
  for consumption in data.consumption:
    local_start: datetime = as_local(consumption["start"])
    is_weekend = local_start.weekday() == 5 or local_start.weekday() == 6
    if is_weekend and contains_consumption(historic_weekend_consumptions, consumption) == False:
      historic_weekend_consumptions.append(consumption)
    elif is_weekend == False and contains_consumption(historic_weekday_consumptions, consumption) == False:
      historic_weekday_consumptions.append(consumption)

  # Fetch rates that might be missing
  local_start = as_local(current).replace(hour=0, minute=0, second=0, microsecond=0)
  weekday_periods = get_octoplus_session_weekday_dates(local_start, 15, timedelta(hours=24), [])
  earliest_weekday_start = weekday_periods[-1].start
  missing_weekday_consumptions = extract_missing_consumption_periods(weekday_periods, historic_weekday_consumptions)

  weekend_periods = get_octoplus_session_weekend_dates(local_start, 8, timedelta(hours=24), [])
  earliest_weekend_start = weekend_periods[-1].start
  missing_weekend_consumptions = extract_missing_consumption_periods(weekend_periods, historic_weekend_consumptions)

  historic_weekday_consumptions = await async_get_missing_consumption(client, identifier, serial_number, historic_weekday_consumptions, missing_weekday_consumptions)
  historic_weekend_consumptions = await async_get_missing_consumption(client, identifier, serial_number, historic_weekend_consumptions, missing_weekend_consumptions)

  historic_weekday_consumptions = remove_old_consumptions(historic_weekday_consumptions, earliest_weekday_start)
  historic_weekend_consumptions = remove_old_consumptions(historic_weekend_consumptions, earliest_weekend_start)

  historic_weekday_consumptions.sort(key=lambda x: (x["start"].timestamp(), x["start"].fold))
  historic_weekend_consumptions.sort(key=lambda x: (x["start"].timestamp(), x["start"].fold))

  current_weekday_earliest_start = historic_weekday_consumptions[0]["start"] if historic_weekday_consumptions is not None and len(historic_weekday_consumptions) > 0 else None
  current_weekday_latest_end = historic_weekday_consumptions[-1]["end"] if historic_weekday_consumptions is not None and len(historic_weekday_consumptions) > 0 else None

  current_weekend_earliest_start = historic_weekend_consumptions[0]["start"] if historic_weekend_consumptions is not None and len(historic_weekend_consumptions) > 0 else None
  current_weekend_latest_end = historic_weekend_consumptions[-1]["end"] if historic_weekend_consumptions is not None and len(historic_weekend_consumptions) > 0 else None

  if current_weekday_earliest_start != previous_weekday_earliest_start or current_weekday_latest_end != previous_weekday_latest_end or len(missing_weekday_consumptions) > 0:
    _LOGGER.debug(f"Saving historic weekday consumption data: current_weekday_earliest_start: {current_weekday_earliest_start}; previous_weekday_earliest_start: {previous_weekday_earliest_start}; current_weekday_latest_end: {current_weekday_latest_end}; previous_weekday_latest_end: {previous_weekday_latest_end}; missing_weekday_consumptions: {len(missing_weekday_consumptions)}")
    await async_save_historic_consumptions(identifier, serial_number, True, historic_weekday_consumptions)

  if current_weekend_earliest_start != previous_weekend_earliest_start or current_weekend_latest_end != previous_weekend_latest_end or len(missing_weekend_consumptions) > 0:
    _LOGGER.debug(f"Saving historic weekend consumption data: current_weekend_earliest_start: {current_weekend_earliest_start}; previous_weekend_earliest_start: {previous_weekend_earliest_start}; current_weekend_latest_end: {current_weekend_latest_end}; previous_weekend_latest_end: {previous_weekend_latest_end}; missing_weekend_consumptions: {len(missing_weekend_consumptions)}")
    await async_save_historic_consumptions(identifier, serial_number, False, historic_weekend_consumptions)

  return PreviousConsumptionCoordinatorResult(
    data.last_evaluated,
    data.request_attempts,
    data.consumption,
    data.rates,
    data.standing_charge,
    historic_weekday_consumptions,
    historic_weekend_consumptions
  )

def get_latest_day(consumption_data: list | None):
  if consumption_data is None or len(consumption_data) < 1:
    return None
  
  current_reduced_consumption_data = []
  latest_reduced_consumption_data = None
  for consumption in consumption_data:
    local_start = as_local(consumption["start"])
    if (local_start.hour == 0 and local_start.minute == 0):
      if len(current_reduced_consumption_data) == 48:
        latest_reduced_consumption_data = current_reduced_consumption_data
      current_reduced_consumption_data = []

    current_reduced_consumption_data.append(consumption)

  if len(current_reduced_consumption_data) == 48:
    latest_reduced_consumption_data = current_reduced_consumption_data

  _LOGGER.debug(f"Latest day: {latest_reduced_consumption_data[-1]["end"] if latest_reduced_consumption_data is not None and len(latest_reduced_consumption_data) > 0 else None}")
  return latest_reduced_consumption_data

async def async_fetch_consumption_and_rates(
  previous_data: PreviousConsumptionCoordinatorResult | None,
  current: datetime,
  account_info,
  client: OctopusEnergyApiClient,
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

  _LOGGER.debug(f"{'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}: next_refresh: {previous_data.next_refresh if previous_data is not None else None}; ")
  if (previous_data == None or 
      current >= previous_data.next_refresh):
    rate_data = None
    standing_charge = None
    
    try:
      if (is_electricity == True):
        consumption_data = await client.async_get_electricity_consumption(identifier, serial_number, page_size=52)
        consumption_data = get_latest_day(consumption_data)

        if consumption_data is not None:
          period_from = consumption_data[0]["start"]
          period_to = consumption_data[-1]["end"]

          tariff = get_electricity_meter_tariff(period_from, account_info, identifier, serial_number) if tariff_override is None else tariff_override
          if tariff is None:
            _LOGGER.error(f"Could not determine tariff code for previous consumption for electricity {identifier}/{serial_number}")
            return previous_data

          # We'll calculate the wrong value if we don't have our intelligent dispatches
          if is_intelligent_product(tariff.product) and intelligent_device is not None and intelligent_dispatches is None:
            _LOGGER.debug("Dispatches not available for intelligent tariff. Using existing rate information")
            return previous_data
          
          if (previous_data is not None and 
              previous_data.rates is not None and 
              len(previous_data.rates) > 0 and 
              previous_data.rates[0]["start"] == period_from and previous_data.rates[-1]["end"] == period_to):
            _LOGGER.info('Previous rates are for our target consumption, so using previously retrieved rates and standing charges')
            rate_data = previous_data.rates
            standing_charge = { "value_inc_vat": previous_data.standing_charge }
          else:
            [rate_data, standing_charge] = await asyncio.gather(
              client.async_get_electricity_rates(tariff.product, tariff.code, is_smart_meter, period_from, period_to),
              client.async_get_electricity_standing_charge(tariff.product, tariff.code, period_from, period_to)
            )

          if intelligent_dispatches is not None:
            _LOGGER.debug(f"Adjusting rate data based on intelligent tariff; dispatches: {intelligent_dispatches}")
            rate_data = adjust_intelligent_rates(rate_data,
                                                  intelligent_dispatches.planned,
                                                  intelligent_dispatches.completed)
      else:
        consumption_data = await client.async_get_gas_consumption(identifier, serial_number, page_size=52)
        consumption_data = get_latest_day(consumption_data)

        if consumption_data is not None:
          period_from = consumption_data[0]["start"]
          period_to = consumption_data[-1]["end"]

          tariff = get_gas_meter_tariff(period_from, account_info, identifier, serial_number) if tariff_override is None else tariff_override
          if tariff is None:
            _LOGGER.error(f"Could not determine tariff code for previous consumption for gas {identifier}/{serial_number}")
            return previous_data
          
          if (previous_data is not None and 
              previous_data.rates is not None and 
              len(previous_data.rates) > 0 and 
              previous_data.rates[0]["start"] == period_from and previous_data.rates[-1]["end"] == period_to):
            _LOGGER.info('Previous rates are for our target consumption, so using previously retrieved rates and standing charges')
            rate_data = previous_data.rates
            standing_charge = { "value_inc_vat": previous_data.standing_charge }
          else:
            [rate_data, standing_charge] = await asyncio.gather(
              client.async_get_gas_rates(tariff.product, tariff.code, period_from, period_to),
              client.async_get_gas_standing_charge(tariff.product, tariff.code, period_from, period_to)
            )
      
      _LOGGER.debug(f"{'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}: consumption_data: {len(consumption_data) if consumption_data is not None else None}; rate_data: {len(rate_data) if rate_data is not None else None}; standing_charge: {standing_charge}")
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
          None,
          None
        )
    
      
      return PreviousConsumptionCoordinatorResult(
        current,
        1,
        previous_data.consumption if previous_data is not None else None,
        previous_data.rates if previous_data is not None else None,
        previous_data.standing_charge if previous_data is not None else None,
        previous_data.historic_weekday_consumption if previous_data is not None else None,
        previous_data.historic_weekend_consumption if previous_data is not None else None
      )
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      
      result = None
      if previous_data is not None:
        result =  PreviousConsumptionCoordinatorResult(
          previous_data.last_evaluated,
          previous_data.request_attempts + 1,
          previous_data.consumption,
          previous_data.rates,
          previous_data.standing_charge,
          previous_data.historic_weekday_consumption,
          previous_data.historic_weekend_consumption,
          last_error=e
        )

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number} - using cached data. See diagnostics sensor for more information.. Exception: {e}")
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
          last_error=e
        )
        _LOGGER.warning(f"Failed to retrieve previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}. See diagnostics sensor for more information.. Exception: {e}")

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
    tariff_override: Tariff = None):
  """Create reading coordinator"""
  previous_consumption_data_key = f'{identifier}_{serial_number}_previous_consumption_and_rates'

  async def async_load_historic_consumption(identifier: str, serial_number: str, is_weekday: bool):
    weekend_weekday_suffix = "weekday" if is_weekday else "weekend"
    store = storage.Store(hass, "1", f"octopus_energy.{identifier}_{serial_number}_{weekend_weekday_suffix}_consumption")

    try:
      data = await store.async_load()
      consumption = []
      if data is not None:
        _LOGGER.debug(f"Loaded historic consumption for {identifier}/{serial_number} ({weekend_weekday_suffix}) - {len(data)}")
        for item in data:
          consumption.append({
            "start": datetime.fromisoformat(item["start"]),
            "end": datetime.fromisoformat(item["end"]),
            "consumption": float(item["consumption"])
          })

      return consumption
    except:
      return []
    
  async def async_save_historic_consumption(identifier: str, serial_number: str, is_weekday: bool, consumption: list):
    weekend_weekday_suffix = "weekday" if is_weekday else "weekend"
    store = storage.Store(hass, "1", f"octopus_energy.{identifier}_{serial_number}_{weekend_weekday_suffix}_consumption")
    await store.async_save(consumption)
    _LOGGER.debug(f"Saved historic rates for {identifier}/{serial_number} ({weekend_weekday_suffix})")

  async def async_update_data():
    """Fetch data from API endpoint."""
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
        hass.data[DOMAIN][account_id][previous_consumption_data_key] = await async_enhance_with_historic_consumption(
          current,
          client,
          result,
          previous_data,
          identifier,
          serial_number,
          async_load_historic_consumption,
          async_save_historic_consumption
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