import re
from datetime import timedelta

from homeassistant.util.dt import (parse_datetime)

from ..const import (
  CONFIG_KIND,
  CONFIG_KIND_TARGET_RATE,
  CONFIG_ACCOUNT_ID,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_HOURS_MODE,
  CONFIG_TARGET_HOURS_MODE_EXACT,
  CONFIG_TARGET_HOURS_MODE_MINIMUM,
  CONFIG_TARGET_MAX_RATE,
  CONFIG_TARGET_MIN_RATE,
  CONFIG_TARGET_MPAN,
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_OFFSET,
  CONFIG_TARGET_OLD_END_TIME,
  CONFIG_TARGET_OLD_HOURS,
  CONFIG_TARGET_OLD_MPAN,
  CONFIG_TARGET_OLD_NAME,
  CONFIG_TARGET_OLD_START_TIME,
  CONFIG_TARGET_OLD_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_TYPE_CONTINUOUS,
  CONFIG_TARGET_WEIGHTING,
  DOMAIN,
  REGEX_ENTITY_NAME,
  REGEX_HOURS,
  REGEX_OFFSET_PARTS,
  REGEX_PRICE,
  REGEX_TIME,
  REGEX_WEIGHTING
)

from . import get_electricity_meter_tariffs
from ..utils.tariff_check import is_agile_tariff
from ..target_rates import create_weighting

async def async_migrate_target_config(version: int, data: {}, get_entries):
  new_data = {**data}

  if (version <= 1):
    new_data[CONFIG_KIND] = CONFIG_KIND_TARGET_RATE

  if (version <= 2):
    new_data[CONFIG_KIND] = CONFIG_KIND_TARGET_RATE

    if CONFIG_TARGET_OLD_NAME in new_data:
      new_data[CONFIG_TARGET_NAME] = new_data[CONFIG_TARGET_OLD_NAME]
      del new_data[CONFIG_TARGET_OLD_NAME]

    if CONFIG_TARGET_OLD_HOURS in new_data:
      new_data[CONFIG_TARGET_HOURS] = new_data[CONFIG_TARGET_OLD_HOURS]
      del new_data[CONFIG_TARGET_OLD_HOURS]

    if CONFIG_TARGET_OLD_TYPE in new_data:
      new_data[CONFIG_TARGET_TYPE] = new_data[CONFIG_TARGET_OLD_TYPE]
      del new_data[CONFIG_TARGET_OLD_TYPE]

    if CONFIG_TARGET_OLD_START_TIME in new_data:
      new_data[CONFIG_TARGET_START_TIME] = new_data[CONFIG_TARGET_OLD_START_TIME]
      del new_data[CONFIG_TARGET_OLD_START_TIME]

    if CONFIG_TARGET_OLD_END_TIME in new_data:
      new_data[CONFIG_TARGET_END_TIME] = new_data[CONFIG_TARGET_OLD_END_TIME]
      del new_data[CONFIG_TARGET_OLD_END_TIME]

    if CONFIG_TARGET_OLD_MPAN in new_data:
      new_data[CONFIG_TARGET_MPAN] = new_data[CONFIG_TARGET_OLD_MPAN]
      del new_data[CONFIG_TARGET_OLD_MPAN]

    entries: list = get_entries(DOMAIN)
    for entry in entries:
      if CONFIG_ACCOUNT_ID in entry.data:
        new_data[CONFIG_ACCOUNT_ID] = entry.data[CONFIG_ACCOUNT_ID]

  if (version <= 4):
    if CONFIG_TARGET_HOURS_MODE not in new_data:
      new_data[CONFIG_TARGET_HOURS_MODE] = CONFIG_TARGET_HOURS_MODE_EXACT

  return new_data

def merge_target_rate_config(data: dict, options: dict, updated_config: dict = None):
  config = dict(data)
  if options is not None:
    config.update(options)

  if updated_config is not None:
    config.update(updated_config)

    if CONFIG_TARGET_START_TIME not in updated_config and CONFIG_TARGET_START_TIME in config:
      config[CONFIG_TARGET_START_TIME] = None

    if CONFIG_TARGET_END_TIME not in updated_config and CONFIG_TARGET_END_TIME in config:
      config[CONFIG_TARGET_END_TIME] = None

    if CONFIG_TARGET_OFFSET not in updated_config and CONFIG_TARGET_OFFSET in config:
      config[CONFIG_TARGET_OFFSET] = None

    if CONFIG_TARGET_MIN_RATE not in updated_config and CONFIG_TARGET_MIN_RATE in config:
      config[CONFIG_TARGET_MIN_RATE] = None

    if CONFIG_TARGET_MAX_RATE not in updated_config and CONFIG_TARGET_MAX_RATE in config:
      config[CONFIG_TARGET_MAX_RATE] = None

    if CONFIG_TARGET_WEIGHTING not in updated_config and CONFIG_TARGET_WEIGHTING in config:
      config[CONFIG_TARGET_WEIGHTING] = None

  return config

def is_time_frame_long_enough(hours, start_time, end_time):
  start_time = parse_datetime(f"2023-08-01T{start_time}:00Z")
  end_time = parse_datetime(f"2023-08-01T{end_time}:00Z")
  if end_time <= start_time:
    end_time = end_time + timedelta(days=1)

  time_diff = end_time - start_time
  available_minutes = time_diff.total_seconds() / 60
  target_minutes = (hours / 0.5) * 30

  return available_minutes >= target_minutes

agile_start = parse_datetime(f"2023-08-01T16:00:00Z")
agile_end = parse_datetime(f"2023-08-01T23:00:00Z")

def is_in_agile_darkzone(start_time, end_time):
  start_time = parse_datetime(f"2023-08-01T{start_time}:00Z")
  end_time = parse_datetime(f"2023-08-01T{end_time}:00Z")
  if end_time <= start_time:
    end_time = end_time + timedelta(days=1)

  return start_time < agile_start and end_time > agile_end

def validate_target_rate_config(data, account_info, now):
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

  if CONFIG_TARGET_START_TIME in data and data[CONFIG_TARGET_START_TIME] is not None:
    matches = re.search(REGEX_TIME, data[CONFIG_TARGET_START_TIME])
    if matches is None:
      errors[CONFIG_TARGET_START_TIME] = "invalid_target_time"

  if CONFIG_TARGET_END_TIME in data and data[CONFIG_TARGET_END_TIME] is not None:
    matches = re.search(REGEX_TIME, data[CONFIG_TARGET_END_TIME])
    if matches is None:
      errors[CONFIG_TARGET_END_TIME] = "invalid_target_time"

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

  start_time = data[CONFIG_TARGET_START_TIME] if CONFIG_TARGET_START_TIME in data and data[CONFIG_TARGET_START_TIME] is not None else "00:00"
  end_time = data[CONFIG_TARGET_END_TIME] if CONFIG_TARGET_END_TIME in data and data[CONFIG_TARGET_END_TIME] is not None else "00:00"

  is_time_valid = CONFIG_TARGET_START_TIME not in errors and CONFIG_TARGET_END_TIME not in errors

  if CONFIG_TARGET_HOURS not in errors and is_time_valid:
    if is_time_frame_long_enough(data[CONFIG_TARGET_HOURS], start_time, end_time) == False:
      errors[CONFIG_TARGET_HOURS] = "invalid_hours_time_frame"

  meter_tariffs = get_electricity_meter_tariffs(account_info, now)
  if (data[CONFIG_TARGET_MPAN] not in meter_tariffs):
    errors[CONFIG_TARGET_MPAN] = "invalid_mpan"
  elif is_time_valid:
    tariff = meter_tariffs[data[CONFIG_TARGET_MPAN]]
    if is_agile_tariff(tariff.code):
      if is_in_agile_darkzone(start_time, end_time):
        errors[CONFIG_TARGET_END_TIME] = "invalid_end_time_agile"

  return errors