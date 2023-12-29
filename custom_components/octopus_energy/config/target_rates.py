import re
from datetime import timedelta

from homeassistant.util.dt import (parse_datetime)

from ..const import (
  CONFIG_KIND,
  CONFIG_KIND_TARGET_RATE,
  CONFIG_ACCOUNT_ID,
  CONFIG_TARGET_END_TIME,
  CONFIG_TARGET_HOURS,
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
  DOMAIN,
  REGEX_ENTITY_NAME,
  REGEX_HOURS,
  REGEX_OFFSET_PARTS,
  REGEX_TIME
)

from ..utils import get_active_tariff_code
from ..utils.tariff_check import is_agile_tariff

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

  return new_data

def merge_target_rate_config(data: dict, options: dict, updated_config: dict = None):
  config = dict(data)
  if options is not None:
    config.update(options)

  if updated_config is not None:
    config.update(updated_config)

  return config

def get_meter_tariffs(account_info, now):
  meters = {}
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff_code = get_active_tariff_code(now, point["agreements"])
      if active_tariff_code is not None:
        meters[point["mpan"]] = active_tariff_code

  return meters

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

  if CONFIG_TARGET_START_TIME in data:
    matches = re.search(REGEX_TIME, data[CONFIG_TARGET_START_TIME])
    if matches is None:
      errors[CONFIG_TARGET_START_TIME] = "invalid_target_time"

  if CONFIG_TARGET_END_TIME in data:
    matches = re.search(REGEX_TIME, data[CONFIG_TARGET_END_TIME])
    if matches is None:
      errors[CONFIG_TARGET_END_TIME] = "invalid_target_time"

  if CONFIG_TARGET_OFFSET in data:
    matches = re.search(REGEX_OFFSET_PARTS, data[CONFIG_TARGET_OFFSET])
    if matches is None:
      errors[CONFIG_TARGET_OFFSET] = "invalid_offset"

  start_time = data[CONFIG_TARGET_START_TIME] if CONFIG_TARGET_START_TIME in data else "00:00"
  end_time = data[CONFIG_TARGET_END_TIME] if CONFIG_TARGET_END_TIME in data else "00:00"

  if CONFIG_TARGET_HOURS not in errors and CONFIG_TARGET_START_TIME not in errors and CONFIG_TARGET_END_TIME not in errors:
    if is_time_frame_long_enough(data[CONFIG_TARGET_HOURS], start_time, end_time) == False:
      errors[CONFIG_TARGET_HOURS] = "invalid_hours_time_frame"

  meter_tariffs = get_meter_tariffs(account_info, now)
  if (data[CONFIG_TARGET_MPAN] not in meter_tariffs):
    errors[CONFIG_TARGET_MPAN] = "invalid_mpan"
  else:
    tariff = meter_tariffs[data[CONFIG_TARGET_MPAN]]
    if is_agile_tariff(tariff):
      if is_in_agile_darkzone(start_time, end_time):
        errors[CONFIG_TARGET_END_TIME] = "invalid_end_time_agile"

  return errors