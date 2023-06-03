from datetime import (datetime, timedelta)
import logging

from homeassistant.util.dt import (parse_datetime, utcnow, now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  DOMAIN,
)

from ..api_client import (OctopusEnergyApiClient)

_LOGGER = logging.getLogger(__name__)

async def async_get_live_consumption(client: OctopusEnergyApiClient, device_id, current_date: datetime, last_retrieval_date: datetime):
    period_to = current_date.strftime("%Y-%m-%dT%H:%M:00Z")
    if (last_retrieval_date is None):
      period_from = (parse_datetime(period_to) - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:00Z")
    elif (current_date - last_retrieval_date).days >= 5:
      period_from = (parse_datetime(period_to) - timedelta(days=5)).strftime("%Y-%m-%dT00:00:00Z")
    else:
      period_from = (last_retrieval_date + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:00Z")
    
    try:
      result = await client.async_get_smart_meter_consumption(device_id, period_from, period_to)
      if result is not None:

        total_consumption = 0
        latest_date = None
        demand = None
        for item in result:
          total_consumption += item["consumption"]
          if (latest_date is None or latest_date < item["startAt"]):
            latest_date = item["startAt"]
            demand = item["demand"]

        return {
          "consumption": total_consumption,
          "startAt": latest_date,
          "demand": demand
        }
      
    except:
      _LOGGER.debug('Failed to retrieve smart meter consumption data')
    
    return None

async def async_create_current_consumption_coordinator(hass, client: OctopusEnergyApiClient, device_id: str, is_electricity: bool):
  """Create current consumption coordinator"""

  async def async_update_data():
    """Fetch data from API endpoint."""
    previous_current_consumption_date_key = f'{device_id}_previous_current_consumption_date'
    last_date = None
    if previous_current_consumption_date_key in hass.data[DOMAIN]:
      last_date = hass.data[DOMAIN][previous_current_consumption_date_key]
    elif is_electricity == False:
      last_date = (now() - timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    data = await async_get_live_consumption(client, device_id, utcnow(), last_date)
    if data is not None:
      hass.data[DOMAIN][previous_current_consumption_date_key] = data["startAt"]

    return data

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"current_consumption_{device_id}",
    update_method=async_update_data,
    update_interval=timedelta(minutes=1),
  )
  
  await coordinator.async_config_entry_first_refresh()

  return coordinator