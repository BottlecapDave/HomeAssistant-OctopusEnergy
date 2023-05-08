import logging
from datetime import (datetime, timedelta)

from homeassistant.core import HomeAssistant
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    statistics_during_period
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_import_external_statistics_from_consumption(hass: HomeAssistant, now: datetime, unique_id: str, name: str, consumptions, unit_of_measurement: str, consumption_key: str):
  statistic_id = f"{DOMAIN}:{unique_id}".lower()

  # Our sum needs to be based from the last total, so we need to grab the last record from the previous day
  last_stat = await get_instance(hass).async_add_executor_job(
    statistics_during_period,
    hass,
    consumptions[0]["from"] - timedelta(days=7),
    consumptions[0]["from"],
    {statistic_id},
    "hour",
    None, 
    {"sum"}
  )

  statistics = []
  
  last_reset = consumptions[0]["from"].replace(minute=0, second=0, microsecond=0)
  sum = last_stat[statistic_id][-1]["sum"] if statistic_id in last_stat and len(last_stat[statistic_id]) > 0 else 0 
  state = 0

  _LOGGER.debug(f'last_stat: {last_stat}; sum: {sum}; last_reset: {last_reset}')

  for index in range(len(consumptions)):
    charge = consumptions[index]
    
    start = charge["from"].replace(minute=0, second=0, microsecond=0)
    sum += charge[consumption_key]
    state += charge[consumption_key]

    _LOGGER.debug(f'index: {index}; start: {start}; sum: {sum}; state: {state}; added: {(index) % 2 == 1}')

    if index % 2 == 1:
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
    source=DOMAIN,
    statistic_id=statistic_id,
    unit_of_measurement=unit_of_measurement,
  )

  async_add_external_statistics(hass, metadata, statistics)