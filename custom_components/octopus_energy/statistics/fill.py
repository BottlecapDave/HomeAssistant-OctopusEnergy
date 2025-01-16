import logging
from datetime import datetime

from . import (ImportStatisticsResult, build_filler_statistics)

from homeassistant.core import HomeAssistant
from homeassistant.components.recorder.models import StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_import_statistics
)

from ..utils.rate_information import get_peak_name, get_peak_type, get_unique_rates, has_peak_rates

_LOGGER = logging.getLogger(__name__)

def get_electricity_consumption_statistic_unique_id(serial_number: str, mpan: str, is_export: bool):
  return f"electricity_{serial_number}_{mpan}{'_export' if is_export == True else ''}_previous_accumulative_consumption"

def get_electricity_consumption_statistic_name(serial_number: str, mpan: str, is_export: bool):
  return f"Electricity {serial_number} {mpan}{' Export' if is_export == True else ''} Previous Accumulative Consumption"

def get_gas_consumption_statistic_unique_id(serial_number: str, mpan: str, is_kwh: bool = False):
  return f"gas_{serial_number}_{mpan}_previous_accumulative_consumption{'_kwh' if is_kwh else ''}"

def get_gas_consumption_statistic_name(serial_number: str, mpan: str, is_kwh: bool = False):
  return f"Gas {serial_number} {mpan} Previous Accumulative Consumption{' (kWh)' if is_kwh else ''}"

async def async_import_filler_statistics(
    hass: HomeAssistant,
    statistic_id: str,
    name: str,
    start: datetime,
    end: datetime,
    rates,
    unit_of_measurement: str,
    statistics: ImportStatisticsResult
  ):
  if (rates is None or len(rates) < 1):
    return

  unique_rates = get_unique_rates(start, rates)
  total_unique_rates = len(unique_rates)

  last_reset = start.replace(hour=0, minute=0, second=0, microsecond=0)

  statistics = build_filler_statistics(start, end, last_reset, statistics.total)

  if statistics is not None and len(statistics) > 0:
    async_import_statistics(
      hass,
      StatisticMetaData(
        has_mean=False,
        has_sum=True,
        name=name,
        source="recorder",
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
      
      _LOGGER.debug(f"Filling statistics for '{peak_type}'...")

      peak_statistic_id = f'{statistic_id}_{peak_type}'
      peak_statistics = build_filler_statistics(start, end, last_reset, statistics.peak_totals[peak_type])
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
      peak_states[peak_type] = peak_statistics[-1]["state"] if len(peak_statistics) > 0 and peak_statistics[-1] is not None else 0

  return ImportStatisticsResult(statistics[-1]["sum"] if statistics[-1] is not None else 0,
                                statistics[-1]["state"] if statistics[-1] is not None else 0,
                                peak_totals,
                                peak_states)