from datetime import (datetime, timedelta)
import logging

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  DOMAIN,
)

from ..api_client import (OctopusEnergyApiClient)

_LOGGER = logging.getLogger(__name__)

async def async_get_live_consumption(client: OctopusEnergyApiClient, device_id, current_date: datetime):
    period_from = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    period_to = current_date + timedelta(days=1)
    
    try:
      result = await client.async_get_smart_meter_consumption(device_id, period_from, period_to)
      if result is not None:
        _LOGGER.debug(f'Current Home Mini consumption retrieved')
        return result
      
    except:
      _LOGGER.debug('Failed to retrieve smart meter consumption data')
    
    return None

async def async_create_current_consumption_coordinator(hass, client: OctopusEnergyApiClient, device_id: str, is_electricity: bool, refresh_rate_in_minutes: int):
  """Create current consumption coordinator"""

  async def async_update_data():
    """Fetch data from API endpoint."""
    return await async_get_live_consumption(client, device_id, now())

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"current_consumption_{device_id}",
    update_method=async_update_data,
    update_interval=timedelta(minutes=refresh_rate_in_minutes),
  )
  
  await coordinator.async_config_entry_first_refresh()

  return coordinator