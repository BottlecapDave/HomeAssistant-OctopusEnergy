import logging
import datetime

from homeassistant.core import HomeAssistant
from homeassistant.components.recorder.models import StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    async_import_statistics
)

from ..const import DOMAIN
from ..utils.rate_information import get_peak_name, get_peak_type, get_unique_rates, has_peak_rates
from . import (ImportStatisticsResult, build_cost_statistics, async_get_last_sum)

_LOGGER = logging.getLogger(__name__)

def get_electricity_cost_statistic_unique_id(serial_number: str, mpan: str, is_export: bool):
  return f"electricity_{serial_number}_{mpan}{'_export' if is_export == True else ''}_previous_accumulative_cost"

def get_electricity_cost_statistic_name(serial_number: str, mpan: str, is_export: bool):
  return f"Electricity {serial_number} {mpan}{' Export' if is_export == True else ''} Previous Accumulative Cost"

def get_gas_cost_statistic_unique_id(serial_number: str, mpan: str):
  return f"gas_{serial_number}_{mpan}_previous_accumulative_cost"

def get_gas_cost_statistic_name(serial_number: str, mpan: str):
  return f"Gas {serial_number} {mpan} Previous Accumulative Cost"

async def async_import_external_statistics_from_cost(
    current: datetime,
    hass: HomeAssistant,
    unique_id: str,
    name: str,
    consumptions,
    rates,
    unit_of_measurement: str,
    consumption_key: str,
    initial_statistics: ImportStatisticsResult = None
  ):
  if (consumptions is None or len(consumptions) < 1 or rates is None or len(rates) < 1):
    return

  statistic_id = f"{DOMAIN}:{unique_id}".lower()

  # Our sum needs to be based from the last total, so we need to grab the last record from the previous day
  latest_total_sum = initial_statistics.total if initial_statistics is not None else await async_get_last_sum(hass, consumptions[0]["start"], statistic_id)

  unique_rates = get_unique_rates(consumptions[0]["start"], rates)
  total_unique_rates = len(unique_rates)
  
  _LOGGER.debug(f"statistic_id: {statistic_id}; latest_total_sum: {latest_total_sum}; total_unique_rates: {total_unique_rates};")

  statistics = build_cost_statistics(consumptions, rates, consumption_key, latest_total_sum)

  async_add_external_statistics(
    hass,
    StatisticMetaData(
      has_mean=False,
      has_sum=True,
      name=name,
      source=DOMAIN,
      statistic_id=statistic_id,
      unit_of_measurement=unit_of_measurement,
    ),
    statistics
  )

  peak_totals = {}
  peak_states = {}
  if has_peak_rates(total_unique_rates):
    for index in range(0, total_unique_rates):
      peak_type = get_peak_type(total_unique_rates, index)

      _LOGGER.debug(f"Importing cost statistics for '{peak_type}'...")

      target_rate = unique_rates[index]
      peak_statistic_id = f'{statistic_id}_{peak_type}'
      latest_peak_sum = initial_statistics.peak_totals[peak_type] if initial_statistics is not None and peak_type in initial_statistics.peak_totals else await async_get_last_sum(hass, consumptions[0]["start"], peak_statistic_id)

      peak_statistics = build_cost_statistics(consumptions, rates, consumption_key, latest_peak_sum, target_rate)
      
      async_add_external_statistics(
        hass,
        StatisticMetaData(
          has_mean=False,
          has_sum=True,
          name=f'{name} {get_peak_name(peak_type)}',
          source=DOMAIN,
          statistic_id=peak_statistic_id,
          unit_of_measurement=unit_of_measurement,
        ),
        peak_statistics
      )

      peak_totals[peak_type] = peak_statistics[-1]["sum"] if len(peak_statistics) > 0 and peak_statistics[-1] is not None else 0
      peak_states[peak_type] = peak_statistics[-1]["state"] if len(peak_statistics) > 0 and peak_statistics[-1] is not None else 0

  return ImportStatisticsResult(statistics[-1]["sum"] if statistics[-1] is not None else 0,
                                statistics[-1]["state"] if statistics[-1] is not None else 0,
                                peak_totals,
                                peak_states)

async def async_import_statistics_from_cost(
    current: datetime,
    hass: HomeAssistant,
    entity_id: str,
    name: str,
    consumptions,
    rates,
    unit_of_measurement: str,
    consumption_key: str,
    initial_statistics: ImportStatisticsResult = None
  ):
  if (consumptions is None or rates is None or len(rates) < 1 or (len(consumptions) < 1 and initial_statistics is None)):
    return

  # Our sum needs to be based from the last total, so we need to grab the last record from the previous day
  latest_total_sum = initial_statistics.total if initial_statistics is not None else await async_get_last_sum(hass, consumptions[0]["start"], entity_id)

  unique_rates = get_unique_rates(current, rates)
  total_unique_rates = len(unique_rates)
  
  _LOGGER.debug(f"statistic_id: {entity_id}; latest_total_sum: {latest_total_sum}; total_unique_rates: {total_unique_rates};")

  statistics = build_cost_statistics(consumptions, rates, consumption_key, latest_total_sum)

  if statistics is not None and len(statistics) > 0:
    async_import_statistics(
      hass,
      StatisticMetaData(
        has_mean=False,
        has_sum=True,
        name=name,
        source="recorder",
        statistic_id=entity_id,
        unit_of_measurement=unit_of_measurement,
      ),
      statistics
    )

  peak_totals = {}
  if has_peak_rates(total_unique_rates):
    for index in range(0, total_unique_rates):
      peak_type = get_peak_type(total_unique_rates, index)

      _LOGGER.debug(f"Importing cost statistics for '{peak_type}'...")

      target_rate = unique_rates[index]
      peak_statistic_id = f'{entity_id}_{peak_type}'
      latest_peak_sum = initial_statistics.peak_totals[peak_type] if initial_statistics is not None and peak_type in initial_statistics.peak_totals else await async_get_last_sum(hass, consumptions[0]["start"], peak_statistic_id)

      peak_statistics = build_cost_statistics(consumptions, rates, consumption_key, latest_peak_sum, target_rate)
      
      if peak_statistics is not None and len(peak_statistics) > 0:
        async_import_statistics(
          hass,
          StatisticMetaData(
            has_mean=False,
            has_sum=True,
            name=f'{name} {get_peak_name(peak_type)}',
            source="recorder",
            statistic_id=peak_statistic_id,
            unit_of_measurement=unit_of_measurement,
          ),
          peak_statistics
        )

      peak_totals[peak_type] = peak_statistics[-1]["sum"] if len(peak_statistics) > 0 and peak_statistics[-1] is not None else 0

  return ImportStatisticsResult(statistics[-1]["sum"] if statistics[-1] is not None else 0,
                                    peak_totals)