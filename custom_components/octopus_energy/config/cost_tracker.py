import re

from . import get_electricity_meter_tariffs

from ..const import (
  CONFIG_COST_TRACKER_MONTH_DAY_RESET,
  CONFIG_COST_TRACKER_MPAN,
  CONFIG_COST_TRACKER_NAME,
  CONFIG_COST_TRACKER_WEEKDAY_RESET,
  REGEX_ENTITY_NAME
)

async def async_migrate_cost_tracker_config(version: int, data: {}, get_entries):
  new_data = {**data}

  return new_data

def merge_cost_tracker_config(data: dict, options: dict, updated_config: dict = None):
  config = dict(data)
  if options is not None:
    config.update(options)

  if updated_config is not None:
    config.update(updated_config)

  return config

def validate_cost_tracker_config(data, account_info, now):
  errors = {}

  matches = re.search(REGEX_ENTITY_NAME, data[CONFIG_COST_TRACKER_NAME])
  if matches is None:
    errors[CONFIG_COST_TRACKER_NAME] = "invalid_target_name"

  meter_tariffs = get_electricity_meter_tariffs(account_info, now)
  if (data[CONFIG_COST_TRACKER_MPAN] not in meter_tariffs):
    errors[CONFIG_COST_TRACKER_MPAN] = "invalid_mpan"

  # For some reason int type isn't working properly - reporting user input malformed
  if CONFIG_COST_TRACKER_WEEKDAY_RESET in data:
    if isinstance(data[CONFIG_COST_TRACKER_WEEKDAY_RESET], int) == False:
      matches = re.search("^[0-9]+$", data[CONFIG_COST_TRACKER_WEEKDAY_RESET])
      if matches is None:
        errors[CONFIG_COST_TRACKER_WEEKDAY_RESET] = "invalid_week_day"
      else:
        data[CONFIG_COST_TRACKER_WEEKDAY_RESET] = int(data[CONFIG_COST_TRACKER_WEEKDAY_RESET])

    if (data[CONFIG_COST_TRACKER_WEEKDAY_RESET] < 0 or data[CONFIG_COST_TRACKER_WEEKDAY_RESET] > 6):
      errors[CONFIG_COST_TRACKER_WEEKDAY_RESET] = "invalid_week_day"

  if (CONFIG_COST_TRACKER_MONTH_DAY_RESET in data and (data[CONFIG_COST_TRACKER_MONTH_DAY_RESET] < 1 or data[CONFIG_COST_TRACKER_MONTH_DAY_RESET] > 28)):
    errors[CONFIG_COST_TRACKER_MONTH_DAY_RESET] = "invalid_month_day"

  return errors