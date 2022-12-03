from datetime import datetime, timedelta
import math
from homeassistant.util.dt import (as_utc, parse_datetime)
from .utils import (apply_offset)
import logging

_LOGGER = logging.getLogger(__name__)

def __get_applicable_rates(current_date, target_start_time, target_end_time, rates, target_start_offset, is_rolling_target):
  if target_end_time != None:
    # Get the target end for today. If this is in the past, then look at tomorrow
    target_end = parse_datetime(current_date.strftime(f"%Y-%m-%dT{target_end_time}:00%z"))
    if (is_rolling_target == True and target_end < current_date):
      target_end = target_end + timedelta(days=1)
  else:
    target_end = parse_datetime(current_date.strftime(f"%Y-%m-%dT00:00:00%z")) + timedelta(days=1)

  if target_start_time != None:
    # Get the target start on the same day as our target end. If this is after our target end (which can occur if we're looking for
    # a time over night), then go back a day
    target_start = parse_datetime(target_end.strftime(f"%Y-%m-%dT{target_start_time}:00%z"))
    if (target_start > target_end):
      target_start = target_start - timedelta(days=1)

  elif target_end_time != None:
    # If we have an end time set, then we should start from the same day as our end time
    target_start = parse_datetime(target_end.strftime(f"%Y-%m-%dT00:00:00%z"))
  elif is_rolling_target == False:
    target_start = parse_datetime(current_date.strftime(f"%Y-%m-%dT00:00:00%z"))
  else:
    target_start = current_date

  # If our start date has passed, reset it to current_date to avoid picking a slot in the past
  if (is_rolling_target == True and target_start < current_date):
    target_start = current_date

  # Apply our offset so we make sure our target turns on within the specified timeframe
  if (target_start_offset != None):
    target_start = apply_offset(target_start, target_start_offset, True)

  # Convert our target start/end timestamps to UTC as this is what our rates are in
  target_start = as_utc(target_start)
  if target_end is not None:
    target_end = as_utc(target_end)

  _LOGGER.debug(f'Finding rates between {target_start} and {target_end}')

  # Retrieve the rates that are applicable for our target rate
  applicable_rates = []
  if rates != None:
    for rate in rates:
      if rate["valid_from"] >= target_start and (target_end == None or rate["valid_to"] <= target_end):
        applicable_rates.append(rate)

  return applicable_rates

def __get_rate(rate):
  return rate["value_inc_vat"]

def __get_valid_to(rate):
  return rate["valid_to"]

def calculate_continuous_times(current_date, target_start_time, target_end_time, target_hours, rates, target_start_offset = None, is_rolling_target = True, search_for_highest_rate = False):
  applicable_rates = __get_applicable_rates(current_date, target_start_time, target_end_time, rates, target_start_offset, is_rolling_target)
  applicable_rates_count = len(applicable_rates)
  total_required_rates = math.ceil(target_hours * 2)

  best_continuous_rates = None
  best_continuous_rates_total = None

  _LOGGER.debug(f'{applicable_rates_count} applicable rates found')

  # Loop through our rates and try and find the block of time that meets our desired
  # hours and has the lowest combined rates
  for index, rate in enumerate(applicable_rates):
    continuous_rates = [rate]
    continuous_rates_total = rate["value_inc_vat"]
    
    for offset in range(1, total_required_rates):
      if (index + offset) < applicable_rates_count:
        offset_rate = applicable_rates[(index + offset)]
        continuous_rates.append(offset_rate)
        continuous_rates_total += offset_rate["value_inc_vat"]
      else:
        break
    
    if ((best_continuous_rates == None or (search_for_highest_rate == False and continuous_rates_total < best_continuous_rates_total) or (search_for_highest_rate and continuous_rates_total > best_continuous_rates_total)) and len(continuous_rates) == total_required_rates):
      best_continuous_rates = continuous_rates
      best_continuous_rates_total = continuous_rates_total
    else:
      _LOGGER.debug(f'Total rates for current block {continuous_rates_total}. Total rates for best block {best_continuous_rates_total}')

  if best_continuous_rates is not None:
    # Make sure our rates are in ascending order before returning
    best_continuous_rates.sort(key=__get_valid_to)
    return best_continuous_rates
  
  return []

def calculate_intermittent_times(current_date, target_start_time, target_end_time, target_hours, rates, target_start_offset = None, is_rolling_target = True, search_for_highest_rate = False):
  applicable_rates = __get_applicable_rates(current_date, target_start_time, target_end_time, rates, target_start_offset, is_rolling_target)
  total_required_rates = math.ceil(target_hours * 2)

  applicable_rates.sort(key=__get_rate, reverse=search_for_highest_rate)
  applicable_rates = applicable_rates[:total_required_rates]
  
  _LOGGER.debug(f'{len(applicable_rates)} applicable rates found')
  
  if (len(applicable_rates) < total_required_rates):
    return []

  # Make sure our rates are in ascending order before returning
  applicable_rates.sort(key=__get_valid_to)
  return applicable_rates

def is_target_rate_active(current_date: datetime, applicable_rates, offset: str = None):
  is_active = False
  next_time = None
  total_applicable_rates = len(applicable_rates)

  if (total_applicable_rates > 0):
    if (current_date < applicable_rates[0]["valid_from"]):
      next_time = applicable_rates[0]["valid_from"]

    for index, rate in enumerate(applicable_rates):
      if (offset != None):
        valid_from = apply_offset(rate["valid_from"], offset)
        valid_to = apply_offset(rate["valid_to"], offset)
      else:
        valid_from = rate["valid_from"]
        valid_to = rate["valid_to"]

      if current_date >= valid_from and current_date < valid_to:
        is_active = True

        next_index = index + 1
        if (next_index < total_applicable_rates):
          next_time = applicable_rates[next_index]["valid_from"]
        
        break

  return {
    "next_time": next_time,
    "is_active": is_active,
  }
