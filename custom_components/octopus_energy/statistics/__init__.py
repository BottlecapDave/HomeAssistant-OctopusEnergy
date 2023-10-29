import logging
from datetime import (datetime, timedelta)
from custom_components.octopus_energy.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData
from homeassistant.components.recorder.statistics import (
    statistics_during_period
)

from ..utils import get_active_tariff_code, get_off_peak_cost

_LOGGER = logging.getLogger(__name__)

def build_consumption_statistics(current: datetime, consumptions, rates, consumption_key: str, latest_total_sum: float, latest_peak_sum: float, latest_off_peak_sum: float):
  last_reset = consumptions[0]["from"].replace(minute=0, second=0, microsecond=0)
  sums = {
    "total": latest_total_sum,
    "peak": latest_peak_sum,
    "off_peak": latest_off_peak_sum
  }
  states = {
    "total": 0,
    "peak": 0,
    "off_peak": 0
  }
  
  total_statistics = []
  off_peak_statistics = []
  peak_statistics = []
  off_peak_cost = get_off_peak_cost(current, rates)

  _LOGGER.debug(f'total_sum: {latest_total_sum}; latest_peak_sum: {latest_peak_sum}; latest_off_peak_sum: {latest_off_peak_sum}; last_reset: {last_reset}; off_peak_cost: {off_peak_cost}')

  for index in range(len(consumptions)):
    consumption = consumptions[index]
    consumption_from = consumption["from"]
    consumption_to = consumption["to"]

    try:
      rate = next(r for r in rates if r["valid_from"] == consumption_from and r["valid_to"] == consumption_to)
    except StopIteration:
      raise Exception(f"Failed to find rate for consumption between {consumption_from} and {consumption_to}")
    
    if rate["value_inc_vat"] == off_peak_cost:
      sums["off_peak"] += consumption[consumption_key]
      states["off_peak"] += consumption[consumption_key]
    else:
      sums["peak"] += consumption[consumption_key]
      states["peak"] += consumption[consumption_key]
    
    start = consumption["from"].replace(minute=0, second=0, microsecond=0)
    sums["total"] += consumption[consumption_key]
    states["total"] += consumption[consumption_key]

    _LOGGER.debug(f'index: {index}; start: {start}; sums: {sums}; states: {states}; added: {(index) % 2 == 1}')

    if index % 2 == 1:
      total_statistics.append(
        StatisticData(
            start=start,
            last_reset=last_reset,
            sum=sums["total"],
            state=states["total"]
        )
      )

      off_peak_statistics.append(
        StatisticData(
            start=start,
            last_reset=last_reset,
            sum=sums["off_peak"],
            state=states["off_peak"]
        )
      )

      peak_statistics.append(
        StatisticData(
            start=start,
            last_reset=last_reset,
            sum=sums["peak"],
            state=states["peak"]
        )
      )

  return {
    "total": total_statistics,
    "peak": peak_statistics,
    "off_peak": off_peak_statistics
  }

def build_cost_statistics(current: datetime, consumptions, rates, consumption_key: str, latest_total_sum: float, latest_peak_sum: float, latest_off_peak_sum: float):
  last_reset = consumptions[0]["from"].replace(minute=0, second=0, microsecond=0)
  sums = {
    "total": latest_total_sum,
    "peak": latest_peak_sum,
    "off_peak": latest_off_peak_sum
  }
  states = {
    "total": 0,
    "peak": 0,
    "off_peak": 0
  }
  
  total_statistics = []
  off_peak_statistics = []
  peak_statistics = []
  off_peak_cost = get_off_peak_cost(current, rates)

  _LOGGER.debug(f'total_sum: {latest_total_sum}; latest_peak_sum: {latest_peak_sum}; latest_off_peak_sum: {latest_off_peak_sum}; last_reset: {last_reset}; off_peak_cost: {off_peak_cost}')

  for index in range(len(consumptions)):
    consumption = consumptions[index]
    consumption_from = consumption["from"]
    consumption_to = consumption["to"]
    start = consumption["from"].replace(minute=0, second=0, microsecond=0)

    try:
      rate = next(r for r in rates if r["valid_from"] == consumption_from and r["valid_to"] == consumption_to)
    except StopIteration:
      raise Exception(f"Failed to find rate for consumption between {consumption_from} and {consumption_to}")
    
    if rate["value_inc_vat"] == off_peak_cost:
      sums["off_peak"] += round((consumption[consumption_key] * rate["value_inc_vat"]) / 100, 2)
      states["off_peak"] += round((consumption[consumption_key] * rate["value_inc_vat"]) / 100, 2)
    else:
      sums["peak"] += round((consumption[consumption_key] * rate["value_inc_vat"]) / 100, 2)
      states["peak"] += round((consumption[consumption_key] * rate["value_inc_vat"]) / 100, 2)
    
    sums["total"] += round((consumption[consumption_key] * rate["value_inc_vat"]) / 100, 2)
    states["total"] += round((consumption[consumption_key] * rate["value_inc_vat"]) / 100, 2)

    _LOGGER.debug(f'index: {index}; start: {start}; sums: {sums}; states: {states}; added: {(index) % 2 == 1}')

    if index % 2 == 1:
      total_statistics.append(
        StatisticData(
            start=start,
            last_reset=last_reset,
            sum=sums["total"],
            state=states["total"]
        )
      )

      off_peak_statistics.append(
        StatisticData(
            start=start,
            last_reset=last_reset,
            sum=sums["off_peak"],
            state=states["off_peak"]
        )
      )

      peak_statistics.append(
        StatisticData(
            start=start,
            last_reset=last_reset,
            sum=sums["peak"],
            state=states["peak"]
        )
      )

  return {
    "total": total_statistics,
    "peak": peak_statistics,
    "off_peak": off_peak_statistics
  }

async def async_get_last_sum(hass: HomeAssistant, latest_date: datetime, statistic_id: str) -> float:
  last_total_stat = await get_instance(hass).async_add_executor_job(
    statistics_during_period,
    hass,
    latest_date - timedelta(days=7),
    latest_date,
    {statistic_id},
    "hour",
    None, 
    {"sum"}
  )
  total_sum = last_total_stat[statistic_id][-1]["sum"] if statistic_id in last_total_stat and len(last_total_stat[statistic_id]) > 0 else 0

  return total_sum

def get_statistic_ids_to_remove(now, account_info):
  external_statistic_ids_to_remove = []

  if (account_info is None):
    return external_statistic_ids_to_remove

  if len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      electricity_tariff_code = get_active_tariff_code(now, point["agreements"])
      if electricity_tariff_code is None:
        for meter in point["meters"]:
          external_statistic_ids_to_remove.append(f"{DOMAIN}:electricity_{meter['serial_number']}_{point['mpan']}{'_export' if meter['is_export'] == True else ''}_previous_accumulative_consumption")
          external_statistic_ids_to_remove.append(f"{DOMAIN}:electricity_{meter['serial_number']}_{point['mpan']}{'_export' if meter['is_export'] == True else ''}_previous_accumulative_cost")
          external_statistic_ids_to_remove.append(f"{DOMAIN}:electricity_{meter['serial_number']}_{point['mpan']}_previous_accumulative_cost")
          _LOGGER.info(f'Skipping electricity meter due to no active agreement; mpan: {point["mpan"]}; serial number: {meter["serial_number"]}')
  else:
    _LOGGER.info('No electricity meters available')

  if len(account_info["gas_meter_points"]) > 0:
    for point in account_info["gas_meter_points"]:
      # We only care about points that have active agreements
      gas_tariff_code = get_active_tariff_code(now, point["agreements"])
      if gas_tariff_code is None:
        for meter in point["meters"]:
          external_statistic_ids_to_remove.append(f"{DOMAIN}:gas_{meter['serial_number']}_{point['mprn']}_previous_accumulative_consumption")
          external_statistic_ids_to_remove.append(f"{DOMAIN}:gas_{meter['serial_number']}_{point['mprn']}_previous_accumulative_cost")
          _LOGGER.info(f'Skipping gas meter due to no active agreement; mprn: {point["mprn"]}; serial number: {meter["serial_number"]}')
  else:
    _LOGGER.info('No gas meters available')

  return external_statistic_ids_to_remove