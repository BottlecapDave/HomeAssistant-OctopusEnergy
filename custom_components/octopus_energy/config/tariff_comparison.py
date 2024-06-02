import re
from datetime import datetime, timedelta

from . import get_meter_tariffs

from ..const import (
  CONFIG_TARIFF_COMPARISON_MPAN_MPRN,
  CONFIG_TARIFF_COMPARISON_NAME,
  CONFIG_TARIFF_COMPARISON_PRODUCT_CODE,
  CONFIG_TARIFF_COMPARISON_TARIFF_CODE,
  REGEX_ENTITY_NAME
)

from ..api_client import OctopusEnergyApiClient

async def async_migrate_tariff_comparison_config(version: int, data: {}, get_entries):
  new_data = {**data}

  return new_data

def merge_tariff_comparison_config(data: dict, options: dict, updated_config: dict = None):
  config = dict(data)
  if options is not None:
    config.update(options)

  if updated_config is not None:
    config.update(updated_config)

  return config

async def async_validate_tariff_comparison_config(data, account_info, now: datetime, client: OctopusEnergyApiClient):
  errors = {}

  matches = re.search(REGEX_ENTITY_NAME, data[CONFIG_TARIFF_COMPARISON_NAME])
  if matches is None:
    errors[CONFIG_TARIFF_COMPARISON_NAME] = "invalid_target_name"

  meter_tariffs = get_meter_tariffs(account_info, now)
  if (data[CONFIG_TARIFF_COMPARISON_MPAN_MPRN] not in meter_tariffs):
    errors[CONFIG_TARIFF_COMPARISON_MPAN_MPRN] = "invalid_mpan"

  period_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
  period_to = period_from + timedelta(days=1)
  rates = await client.async_get_electricity_rates(data[CONFIG_TARIFF_COMPARISON_PRODUCT_CODE], data[CONFIG_TARIFF_COMPARISON_TARIFF_CODE], True, period_from, period_to)

  if rates is None or len(rates) == 0:
    errors[CONFIG_TARIFF_COMPARISON_PRODUCT_CODE] = "invalid_product_or_tariff"

  return errors