import re


from ..const import (
  CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_HOURS_MODE,
  CONFIG_TARGET_HOURS_MODE_EXACT,
  CONFIG_TARGET_HOURS_MODE_MINIMUM,
  CONFIG_TARGET_MAX_RATE,
  CONFIG_TARGET_MIN_RATE,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_OFFSET,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_TYPE_CONTINUOUS,
  CONFIG_TARGET_WEIGHTING,
  REGEX_ENTITY_NAME,
  REGEX_HOURS,
  REGEX_OFFSET_PARTS,
  REGEX_PRICE,
  REGEX_WEIGHTING
)

from . import get_electricity_meter_tariffs
from ..utils.tariff_check import is_agile_tariff
from ..target_rates import create_weighting

async def async_migrate_rolling_target_config(version: int, data: {}, get_entries):
  new_data = {**data}

  return new_data

def merge_rolling_target_rate_config(data: dict, options: dict, updated_config: dict = None):
  config = dict(data)
  if options is not None:
    config.update(options)

  if updated_config is not None:
    config.update(updated_config)

    if CONFIG_TARGET_OFFSET not in updated_config and CONFIG_TARGET_OFFSET in config:
      config[CONFIG_TARGET_OFFSET] = None

    if CONFIG_TARGET_MIN_RATE not in updated_config and CONFIG_TARGET_MIN_RATE in config:
      config[CONFIG_TARGET_MIN_RATE] = None

    if CONFIG_TARGET_MAX_RATE not in updated_config and CONFIG_TARGET_MAX_RATE in config:
      config[CONFIG_TARGET_MAX_RATE] = None

    if CONFIG_TARGET_WEIGHTING not in updated_config and CONFIG_TARGET_WEIGHTING in config:
      config[CONFIG_TARGET_WEIGHTING] = None

  return config

def validate_rolling_target_rate_config(data):
  errors = {}

  matches = re.search(REGEX_ENTITY_NAME, data[CONFIG_TARGET_NAME])
  if matches is None:
    errors[CONFIG_TARGET_NAME] = "invalid_target_name"

  # For some reason float type isn't working properly - reporting user input malformed
  if isinstance(data[CONFIG_TARGET_HOURS], float) == False:
    matches = re.search(REGEX_HOURS, data[CONFIG_TARGET_HOURS])
    if matches is None:
      errors[CONFIG_TARGET_HOURS] = "invalid_target_hours"
    else:
      data[CONFIG_TARGET_HOURS] = float(data[CONFIG_TARGET_HOURS])
  
  if CONFIG_TARGET_HOURS not in errors:
    if data[CONFIG_TARGET_HOURS] % 0.5 != 0:
      errors[CONFIG_TARGET_HOURS] = "invalid_target_hours"

  if isinstance(data[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD], float) == False:
    matches = re.search(REGEX_HOURS, data[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD])
    if matches is None:
      errors[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD] = "invalid_target_hours"
    else:
      data[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD] = float(data[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD])
  
  if CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD not in errors:
    if data[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD] % 0.5 != 0:
      errors[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD] = "invalid_target_hours"

  if CONFIG_TARGET_OFFSET in data and data[CONFIG_TARGET_OFFSET] is not None:
    matches = re.search(REGEX_OFFSET_PARTS, data[CONFIG_TARGET_OFFSET])
    if matches is None:
      errors[CONFIG_TARGET_OFFSET] = "invalid_offset"

  if CONFIG_TARGET_MIN_RATE in data and data[CONFIG_TARGET_MIN_RATE] is not None:
    if isinstance(data[CONFIG_TARGET_MIN_RATE], float) == False:
      matches = re.search(REGEX_PRICE, data[CONFIG_TARGET_MIN_RATE])
      if matches is None:
        errors[CONFIG_TARGET_MIN_RATE] = "invalid_price"
      else:
        data[CONFIG_TARGET_MIN_RATE] = float(data[CONFIG_TARGET_MIN_RATE])

  if CONFIG_TARGET_MAX_RATE in data and data[CONFIG_TARGET_MAX_RATE] is not None:
    if isinstance(data[CONFIG_TARGET_MAX_RATE], float) == False:
      matches = re.search(REGEX_PRICE, data[CONFIG_TARGET_MAX_RATE])
      if matches is None:
        errors[CONFIG_TARGET_MAX_RATE] = "invalid_price"
      else:
        data[CONFIG_TARGET_MAX_RATE] = float(data[CONFIG_TARGET_MAX_RATE])

  if CONFIG_TARGET_WEIGHTING in data and data[CONFIG_TARGET_WEIGHTING] is not None:
    matches = re.search(REGEX_WEIGHTING, data[CONFIG_TARGET_WEIGHTING])
    if matches is None:
      errors[CONFIG_TARGET_WEIGHTING] = "invalid_weighting"
    
    if CONFIG_TARGET_WEIGHTING not in errors:
      number_of_slots = int(data[CONFIG_TARGET_HOURS] * 2)
      weighting = create_weighting(data[CONFIG_TARGET_WEIGHTING], number_of_slots)

      if (len(weighting) != number_of_slots):
        errors[CONFIG_TARGET_WEIGHTING] = "invalid_weighting_slots"

    if data[CONFIG_TARGET_TYPE] != CONFIG_TARGET_TYPE_CONTINUOUS:
      errors[CONFIG_TARGET_WEIGHTING] = "weighting_not_supported_for_type"
    
    if CONFIG_TARGET_HOURS_MODE in data and data[CONFIG_TARGET_HOURS_MODE] != CONFIG_TARGET_HOURS_MODE_EXACT:
      errors[CONFIG_TARGET_WEIGHTING] = "weighting_not_supported_for_hour_mode"

  if CONFIG_TARGET_HOURS_MODE in data and data[CONFIG_TARGET_HOURS_MODE] == CONFIG_TARGET_HOURS_MODE_MINIMUM:
    if (CONFIG_TARGET_MIN_RATE not in data or data[CONFIG_TARGET_MIN_RATE] is None) and (CONFIG_TARGET_MAX_RATE not in data or data[CONFIG_TARGET_MAX_RATE] is None):
      errors[CONFIG_TARGET_HOURS_MODE] = "minimum_or_maximum_rate_not_specified"

  if CONFIG_TARGET_HOURS not in errors and CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD not in errors and data[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD] < data[CONFIG_TARGET_HOURS]:
    errors[CONFIG_ROLLING_TARGET_HOURS_LOOK_AHEAD] = "look_ahead_hours_not_long_enough"

  return errors