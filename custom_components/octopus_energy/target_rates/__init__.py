from datetime import datetime, timedelta
import math
import re
import logging

from homeassistant.util.dt import (as_utc, parse_datetime)

from ..utils.conversions import value_inc_vat_to_pounds
from ..const import CONFIG_TARGET_HOURS_MODE_EXACT, CONFIG_TARGET_HOURS_MODE_MAXIMUM, CONFIG_TARGET_HOURS_MODE_MINIMUM, CONFIG_TARGET_KEYS, REGEX_OFFSET_PARTS, REGEX_WEIGHTING

_LOGGER = logging.getLogger(__name__)

def apply_offset(date_time: datetime, offset: str, inverse = False):
  matches = re.search(REGEX_OFFSET_PARTS, offset)
  if matches == None:
    raise Exception(f'Unable to extract offset: {offset}')

  symbol = matches[1]
  hours = float(matches[2])
  minutes = float(matches[3])
  seconds = float(matches[4])

  if ((symbol == "-" and inverse == False) or (symbol != "-" and inverse == True)):
    return date_time - timedelta(hours=hours, minutes=minutes, seconds=seconds)
  
  return date_time + timedelta(hours=hours, minutes=minutes, seconds=seconds)

def get_applicable_rates(current_date: datetime, target_start_time: str, target_end_time: str, rates, is_rolling_target = True):
  if (target_start_time is not None):
    target_start = parse_datetime(current_date.strftime(f"%Y-%m-%dT{target_start_time}:00%z"))
  else:
    target_start = parse_datetime(current_date.strftime(f"%Y-%m-%dT00:00:00%z"))

  if (target_end_time is not None):
    target_end = parse_datetime(current_date.strftime(f"%Y-%m-%dT{target_end_time}:00%z"))
  else:
    target_end = parse_datetime(current_date.strftime(f"%Y-%m-%dT00:00:00%z")) + timedelta(days=1)

  target_start = as_utc(target_start)
  target_end = as_utc(target_end)

  if (target_start >= target_end):
    _LOGGER.debug(f'{target_start} is after {target_end}, so setting target end to tomorrow')
    if target_start > current_date:
      target_start = target_start - timedelta(days=1)
    else:
      target_end = target_end + timedelta(days=1)

  # If our start date has passed, reset it to current_date to avoid picking a slot in the past
  if (is_rolling_target == True and target_start < current_date and current_date < target_end):
    _LOGGER.debug(f'Rolling target and {target_start} is in the past. Setting start to {current_date}')
    target_start = current_date

  # If our start and end are both in the past, then look to the next day
  if (target_start < current_date and target_end < current_date):
    target_start = target_start + timedelta(days=1)
    target_end = target_end + timedelta(days=1)

  _LOGGER.debug(f'Finding rates between {target_start} and {target_end}')

  # Retrieve the rates that are applicable for our target rate
  applicable_rates = []
  if rates is not None:
    for rate in rates:
      if rate["start"] >= target_start and (target_end is None or rate["end"] <= target_end):
        new_rate = dict(rate)
        new_rate["value_inc_vat"] = value_inc_vat_to_pounds(rate["value_inc_vat"])
        
        applicable_rates.append(new_rate)

  # Make sure that we have enough rates that meet our target period
  date_diff = target_end - target_start
  hours = (date_diff.days * 24) + (date_diff.seconds // 3600)
  periods = hours * 2
  if len(applicable_rates) < periods:
    _LOGGER.debug(f'Incorrect number of periods discovered. Require {periods}, but only have {len(applicable_rates)}')
    return None

  return applicable_rates

def __get_valid_to(rate):
  return rate["end"]

def calculate_continuous_times(
    applicable_rates: list,
    target_hours: float,
    search_for_highest_rate = False,
    find_last_rates = False,
    min_rate = None,
    max_rate = None,
    weighting: list = None,
    hours_mode = CONFIG_TARGET_HOURS_MODE_EXACT
  ):
  if (applicable_rates is None or target_hours <= 0):
    return []
  
  applicable_rates.sort(key=__get_valid_to, reverse=find_last_rates)
  applicable_rates_count = len(applicable_rates)
  total_required_rates = math.ceil(target_hours * 2)

  if weighting is not None and len(weighting) != total_required_rates:
    raise ValueError("Weighting does not match target hours")

  best_continuous_rates = None
  best_continuous_rates_total = None

  _LOGGER.debug(f'{applicable_rates_count} applicable rates found')

  # Loop through our rates and try and find the block of time that meets our desired
  # hours and has the lowest combined rates
  for index, rate in enumerate(applicable_rates):
    if (min_rate is not None and rate["value_inc_vat"] < min_rate):
      continue

    if (max_rate is not None and rate["value_inc_vat"] > max_rate):
      continue

    continuous_rates = [rate]
    continuous_rates_total = rate["value_inc_vat"] * (weighting[0] if weighting is not None and len(weighting) > 0 else 1)
    
    for offset in range(1, total_required_rates if hours_mode != CONFIG_TARGET_HOURS_MODE_MINIMUM else applicable_rates_count):
      if (index + offset) < applicable_rates_count:
        offset_rate = applicable_rates[(index + offset)]

        if (min_rate is not None and offset_rate["value_inc_vat"] < min_rate):
          break

        if (max_rate is not None and offset_rate["value_inc_vat"] > max_rate):
          break

        continuous_rates.append(offset_rate)
        continuous_rates_total += offset_rate["value_inc_vat"] * (weighting[offset] if weighting is not None else 1)
      else:
        break

    current_continuous_rates_length = len(continuous_rates)
    best_continuous_rates_length = len(best_continuous_rates) if best_continuous_rates is not None else 0
    
    if ((best_continuous_rates is None or 
         (search_for_highest_rate == False and continuous_rates_total < best_continuous_rates_total) or
         (search_for_highest_rate and continuous_rates_total > best_continuous_rates_total)
        )
        and
        (
          (hours_mode == CONFIG_TARGET_HOURS_MODE_EXACT and current_continuous_rates_length == total_required_rates) or
          (hours_mode == CONFIG_TARGET_HOURS_MODE_MINIMUM and current_continuous_rates_length >= total_required_rates and current_continuous_rates_length >= best_continuous_rates_length) or
          (hours_mode == CONFIG_TARGET_HOURS_MODE_MAXIMUM and current_continuous_rates_length <= total_required_rates and current_continuous_rates_length >= best_continuous_rates_length)
        )
      ):
      best_continuous_rates = continuous_rates
      best_continuous_rates_total = continuous_rates_total
    else:
      _LOGGER.debug(f'Total rates for current block {continuous_rates_total}. Total rates for best block {best_continuous_rates_total}')

  if best_continuous_rates is not None:
    # Make sure our rates are in ascending order before returning
    best_continuous_rates.sort(key=__get_valid_to)
    return best_continuous_rates
  
  return []

def calculate_intermittent_times(
    applicable_rates: list,
    target_hours: float,
    search_for_highest_rate = False,
    find_last_rates = False,
    min_rate = None,
    max_rate = None,
    hours_mode = CONFIG_TARGET_HOURS_MODE_EXACT
  ):
  if (applicable_rates is None):
    return []
  
  total_required_rates = math.ceil(target_hours * 2)

  if find_last_rates:
    if search_for_highest_rate:
      applicable_rates.sort(key= lambda rate: (-rate["value_inc_vat"], -rate["end"].timestamp()))
    else:
      applicable_rates.sort(key= lambda rate: (rate["value_inc_vat"], -rate["end"].timestamp()))
  else:
    if search_for_highest_rate:
      applicable_rates.sort(key= lambda rate: (-rate["value_inc_vat"], rate["end"]))
    else:
      applicable_rates.sort(key= lambda rate: (rate["value_inc_vat"], rate["end"]))

  applicable_rates = list(filter(lambda rate: (min_rate is None or rate["value_inc_vat"] >= min_rate) and (max_rate is None or rate["value_inc_vat"] <= max_rate), applicable_rates))
  
  _LOGGER.debug(f'{len(applicable_rates)} applicable rates found')

  if ((hours_mode == CONFIG_TARGET_HOURS_MODE_EXACT and len(applicable_rates) >= total_required_rates) or hours_mode == CONFIG_TARGET_HOURS_MODE_MAXIMUM):
    applicable_rates = applicable_rates[:total_required_rates]
    print(applicable_rates)

    # Make sure our rates are in ascending order before returning
    applicable_rates.sort(key=__get_valid_to)

    return applicable_rates
  elif len(applicable_rates) >= total_required_rates:
    # Make sure our rates are in ascending order before returning
    applicable_rates.sort(key=__get_valid_to)

    return applicable_rates
  
  return []

def get_target_rate_info(current_date: datetime, applicable_rates, offset: str = None):
  is_active = False
  next_time = None
  current_duration_in_hours = 0
  next_duration_in_hours = 0
  total_applicable_rates = len(applicable_rates)

  overall_total_cost = 0
  overall_min_cost = None
  overall_max_cost = None

  current_average_cost = None
  current_min_cost = None
  current_max_cost = None

  next_average_cost = None
  next_min_cost = None
  next_max_cost = None

  if (total_applicable_rates > 0):

    # Find the applicable rates that when combine become a continuous block. This is more for
    # intermittent rates.
    applicable_rates.sort(key=__get_valid_to)
    applicable_rate_blocks = list()
    block_valid_from = applicable_rates[0]["start"]

    total_cost = 0
    min_cost = None
    max_cost = None

    for index, rate in enumerate(applicable_rates):
      if (index > 0 and applicable_rates[index - 1]["end"] != rate["start"]):
        diff = applicable_rates[index - 1]["end"] - block_valid_from
        minutes = diff.total_seconds() / 60
        applicable_rate_blocks.append({
          "start": block_valid_from,
          "end": applicable_rates[index - 1]["end"],
          "duration_in_hours": minutes / 60,
          "average_cost": total_cost / (minutes / 30),
          "min_cost": min_cost,
          "max_cost": max_cost
        })

        block_valid_from = rate["start"]
        total_cost = 0
        min_cost = None
        max_cost = None

      total_cost += rate["value_inc_vat"]
      if min_cost is None or min_cost > rate["value_inc_vat"]:
        min_cost = rate["value_inc_vat"]

      if max_cost is None or max_cost < rate["value_inc_vat"]:
        max_cost = rate["value_inc_vat"]

      overall_total_cost += rate["value_inc_vat"]
      if overall_min_cost is None or overall_min_cost > rate["value_inc_vat"]:
        overall_min_cost = rate["value_inc_vat"]

      if overall_max_cost is None or overall_max_cost < rate["value_inc_vat"]:
        overall_max_cost = rate["value_inc_vat"]

    # Make sure our final block is added
    diff = applicable_rates[-1]["end"] - block_valid_from
    minutes = diff.total_seconds() / 60
    applicable_rate_blocks.append({
      "start": block_valid_from,
      "end": applicable_rates[-1]["end"],
      "duration_in_hours": minutes / 60,
      "average_cost": total_cost / (minutes / 30),
      "min_cost": min_cost,
      "max_cost": max_cost
    })

    # Find out if we're within an active block, or find the next block
    for index, rate in enumerate(applicable_rate_blocks):
      if (offset is not None):
        valid_from = apply_offset(rate["start"], offset)
        valid_to = apply_offset(rate["end"], offset)
      else:
        valid_from = rate["start"]
        valid_to = rate["end"]
      
      if current_date >= valid_from and current_date < valid_to:
        current_duration_in_hours = rate["duration_in_hours"]
        current_average_cost = rate["average_cost"]
        current_min_cost = rate["min_cost"]
        current_max_cost = rate["max_cost"]
        is_active = True
      elif current_date < valid_from:
        next_time = valid_from
        next_duration_in_hours = rate["duration_in_hours"]
        next_average_cost = rate["average_cost"]
        next_min_cost = rate["min_cost"]
        next_max_cost = rate["max_cost"]
        break

  return {
    "is_active": is_active,
    "overall_average_cost": round(overall_total_cost / total_applicable_rates, 5) if total_applicable_rates > 0  else 0,
    "overall_min_cost": overall_min_cost,
    "overall_max_cost": overall_max_cost,
    "current_duration_in_hours": current_duration_in_hours,
    "current_average_cost": current_average_cost,
    "current_min_cost": current_min_cost,
    "current_max_cost": current_max_cost,
    "next_time": next_time,
    "next_duration_in_hours": next_duration_in_hours,
    "next_average_cost": next_average_cost,
    "next_min_cost": next_min_cost,
    "next_max_cost": next_max_cost,
  }

def create_weighting(config: str, number_of_slots: int):
  if config is None or config == "" or config.isspace():
    return None

  matches = re.search(REGEX_WEIGHTING, config)
  if matches is None:
    raise ValueError("Invalid config")
  
  parts = config.split(',')
  parts_length = len(parts)
  weighting = []
  for index in range(parts_length):
    if (parts[index] == "*"):
      # +1 to account for the current part
      target_number_of_slots = number_of_slots - parts_length + 1
      for index in range(target_number_of_slots):
          weighting.append(1)

      continue

    weighting.append(int(parts[index]))

  return weighting

def compare_config(current_config: dict, existing_config: dict):
  if current_config is None or existing_config is None:
    return False

  for key in CONFIG_TARGET_KEYS:
    if ((key not in existing_config and key in current_config) or 
        (key in existing_config and key not in current_config) or
        (key in existing_config and key in current_config and current_config[key] != existing_config[key])):
      return False
    
  return True