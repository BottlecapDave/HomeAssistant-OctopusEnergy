import logging

from homeassistant.core import HomeAssistant
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_import_statistics,
    get_last_statistics
)

_LOGGER = logging.getLogger(__name__)

async def async_import_statistics_from_consumption(hass: HomeAssistant, unique_id: str, name: str, consumptions, unit_of_measurement: str, consumption_key: str):
  statistic_id = f"sensor.{unique_id}".lower()
  last_stat = await get_instance(hass).async_add_executor_job(
    get_last_statistics, hass, 1, statistic_id, False, {"sum"}
  )

  statistics = []
  
  start = consumptions[0]["from"].replace(minute=0, second=0, microsecond=0)
  last_reset = consumptions[-1]["from"].replace(minute=0, second=0, microsecond=0)
  sum = last_stat[statistic_id][0]["sum"] if statistic_id in last_stat and len(last_stat[statistic_id]) > 0 else 0 

  for index in range(len(consumptions)):
    charge = consumptions[index]
    
    start = charge["from"].replace(minute=0, second=0, microsecond=0)
    state = charge[consumption_key]
    sum += state

    _LOGGER.debug(f'index: {index}; start: {start}; sum: {sum}; state: {state}; added: {(index + 1) % 2}')

    if (index + 1) % 2 == 0:
      statistics.append(
        StatisticData(
            start=start,
            last_reset=last_reset,
            sum=sum,
            state=state
        )
      )

  metadata = StatisticMetaData(
    has_mean=False,
    has_sum=True,
    name=name,
    source='recorder',
    statistic_id=statistic_id,
    unit_of_measurement=unit_of_measurement,
  )

  async_import_statistics(hass, metadata, statistics)