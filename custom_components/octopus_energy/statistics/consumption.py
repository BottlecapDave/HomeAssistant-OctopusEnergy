import logging
import datetime
from . import (build_consumption_statistics, async_get_last_sum)

from homeassistant.core import HomeAssistant
from homeassistant.components.recorder.models import StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics
)

from ..const import DOMAIN

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
  peak: float
  off_peak: float

  def __init__(self, total: float, peak: float, off_peak: float):
    self.total = total
    self.peak = peak
    self.off_peak = off_peak

async def async_import_external_statistics_from_consumption(
    current: datetime,
    hass: HomeAssistant,
    unique_id: str,
    name: str,
    consumptions,
    rates,
    unit_of_measurement: str, 
    consumption_key: str,
    include_peak_off_peak: bool = True,
    initial_statistics: ImportConsumptionStatisticsResult = None
  ):
  if (consumptions is None or len(consumptions) < 1 or rates is None or len(rates) < 1):
    return

  statistic_id = f"{DOMAIN}:{unique_id}".lower()

  # Our sum needs to be based from the last total, so we need to grab the last record from the previous day
  total_sum = initial_statistics.total if initial_statistics is not None else await async_get_last_sum(hass, consumptions[0]["start"], statistic_id)

  peak_statistic_id = f'{statistic_id}_peak'
  peak_sum = initial_statistics.peak if initial_statistics is not None else await async_get_last_sum(hass, consumptions[0]["start"], peak_statistic_id)

  off_peak_statistic_id = f'{statistic_id}_off_peak'
  off_peak_sum = initial_statistics.off_peak if initial_statistics is not None else await async_get_last_sum(hass, consumptions[0]["start"], off_peak_statistic_id)

  statistics = build_consumption_statistics(current, consumptions, rates, consumption_key, total_sum, peak_sum, off_peak_sum)

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
    statistics["total"]
  )

  if include_peak_off_peak:
    async_add_external_statistics(
      hass,
      StatisticMetaData(
        has_mean=False,
        has_sum=True,
        name=f'{name} Peak',
        source=DOMAIN,
        statistic_id=peak_statistic_id,
        unit_of_measurement=unit_of_measurement,
      ),
      statistics["peak"]
    )

    async_add_external_statistics(
      hass,
      StatisticMetaData(
        has_mean=False,
        has_sum=True,
        name=f'{name} Off Peak',
        source=DOMAIN,
        statistic_id=off_peak_statistic_id,
        unit_of_measurement=unit_of_measurement,
      ),
      statistics["off_peak"]
    )

  return ImportConsumptionStatisticsResult(statistics["total"][-1]["sum"] if statistics["total"][-1] is not None else 0,
                                           statistics["peak"][-1]["sum"] if statistics["peak"][-1] is not None else 0,
                                           statistics["off_peak"][-1]["sum"] if statistics["off_peak"][-1] is not None else 0)