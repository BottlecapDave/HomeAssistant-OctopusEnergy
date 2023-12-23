import re

from ..const import (
  CONFIG_COST_NAME,
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

def validate_cost_tracker_config(data):
  errors = {}

  matches = re.search(REGEX_ENTITY_NAME, data[CONFIG_COST_NAME])
  if matches is None:
    errors[CONFIG_COST_NAME] = "invalid_target_name"

  return errors