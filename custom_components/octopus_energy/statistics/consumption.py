import logging
import datetime

from . import (build_consumption_statistics, async_get_last_sum)

from homeassistant.core import HomeAssistant
from homeassistant.components.recorder.models import StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics
)

from ..const import DOMAIN
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

class ImportConsumptionStatisticsResult:
  total: float
  peak_totals: "dict[str, float]"

  def __init__(self, total: float, peak_totals: "dict[str, float]"):
    self.total = total
    self.peak_totals = peak_totals

async def async_import_external_statistics_from_consumption(
    current: datetime,
    hass: HomeAssistant,
    unique_id: str,
    name: str,
    consumptions,
    rates,
    unit_of_measurement: str, 
    consumption_key: str,
    initial_statistics: ImportConsumptionStatisticsResult = None
  ):
  if (consumptions is None or len(consumptions) < 1 or rates is None or len(rates) < 1):
    return

  statistic_id = f"{DOMAIN}:{unique_id}".lower()

  # Our sum needs to be based from the last total, so we need to grab the last record from the previous day
  latest_total_sum = initial_statistics.total if initial_statistics is not None else await async_get_last_sum(hass, consumptions[0]["start"], statistic_id)

  unique_rates = get_unique_rates(current, rates)
  total_unique_rates = len(unique_rates)

  _LOGGER.debug(f"statistic_id: {statistic_id}; latest_total_sum: {latest_total_sum}; total_unique_rates: {total_unique_rates};")

  statistics = build_consumption_statistics(current, consumptions, rates, consumption_key, latest_total_sum)

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
  if has_peak_rates(total_unique_rates):
    for index in range(0, total_unique_rates):
      peak_type = get_peak_type(total_unique_rates, index)
      
      _LOGGER.debug(f"Importing consumption statistics for '{peak_type}'...")

      target_rate = unique_rates[index]
      peak_statistic_id = f'{statistic_id}_{peak_type}'
      latest_peak_sum = initial_statistics.peak_totals[peak_type] if initial_statistics is not None and peak_type in initial_statistics.peak_totals else await async_get_last_sum(hass, consumptions[0]["start"], peak_statistic_id)

      peak_statistics = build_consumption_statistics(current, consumptions, rates, consumption_key, latest_peak_sum, target_rate)
      
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

  return ImportConsumptionStatisticsResult(statistics[-1]["sum"] if len(statistics) > 0 and statistics[-1] is not None else 0,
                                           peak_totals)