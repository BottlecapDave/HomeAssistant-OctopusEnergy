import logging
from . import (build_consumption_statistics, async_get_last_sum)

from homeassistant.core import HomeAssistant
from homeassistant.components.recorder.models import StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics
)

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_import_external_statistics_from_consumption(
    hass: HomeAssistant,
    unique_id: str,
    name: str,
    consumptions,
    rates,
    unit_of_measurement: str, 
    consumption_key: str,
    include_peak_off_peak: bool = True
  ):
  if (consumptions is None or len(consumptions) < 1 or rates is None or len(rates) < 1):
    return

  statistic_id = f"{DOMAIN}:{unique_id}".lower()

  # Our sum needs to be based from the last total, so we need to grab the last record from the previous day
  total_sum = await async_get_last_sum(hass, consumptions[0]["from"], statistic_id)

  peak_statistic_id = f'{statistic_id}_peak'
  peak_sum = await async_get_last_sum(hass, consumptions[0]["from"], peak_statistic_id)

  off_peak_statistic_id = f'{statistic_id}_off_peak'
  off_peak_sum = await async_get_last_sum(hass, consumptions[0]["from"], off_peak_statistic_id)

  statistics = build_consumption_statistics(consumptions, rates, consumption_key, total_sum, peak_sum, off_peak_sum)

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