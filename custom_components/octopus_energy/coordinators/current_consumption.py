from datetime import (datetime, timedelta)
import logging
from custom_components.octopus_energy.coordinators import BaseCoordinatorResult

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_CURRENT_CONSUMPTION_KEY,
  DOMAIN,
)

from ..api_client import (ApiException, OctopusEnergyApiClient)

_LOGGER = logging.getLogger(__name__)

class CurrentConsumptionCoordinatorResult(BaseCoordinatorResult):
  data: list

  def __init__(self, last_retrieved: datetime, request_attempts: int, refresh_rate_in_minutes: int, data: list):
    super().__init__(last_retrieved, request_attempts, refresh_rate_in_minutes)
    self.data = data

async def async_get_live_consumption(
  current_date: datetime,
  client: OctopusEnergyApiClient,
  device_id: str,
  previous_consumption: CurrentConsumptionCoordinatorResult,
  refresh_rate_in_minutes: int
):
  if previous_consumption is None or current_date >= previous_consumption.next_refresh:
    period_from = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    period_to = current_date + timedelta(days=1)
    
    try:
      result = await client.async_get_smart_meter_consumption(device_id, period_from, period_to)
      if result is not None:
        return CurrentConsumptionCoordinatorResult(current_date, 1, refresh_rate_in_minutes, result)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        _LOGGER.error(e)
        raise

      result: CurrentConsumptionCoordinatorResult = None
      if previous_consumption is not None:
        result = CurrentConsumptionCoordinatorResult(
          previous_consumption.last_retrieved,
          previous_consumption.request_attempts + 1,
          refresh_rate_in_minutes,
          previous_consumption.data
        )
        _LOGGER.warning(f'Failed to retrieve smart meter consumption data - using cached version. Next attempt at {result.next_refresh}')
      else:
        result = CurrentConsumptionCoordinatorResult(
          # We want to force into our fallback mode
          current_date - timedelta(minutes=refresh_rate_in_minutes),
          2,
          refresh_rate_in_minutes,
          None
        )
        _LOGGER.warning(f'Failed to retrieve smart meter consumption data. Next attempt at {result.next_refresh}')
      
      return result
  
  return previous_consumption

async def async_create_current_consumption_coordinator(hass, client: OctopusEnergyApiClient, device_id: str, refresh_rate_in_minutes: int):
  """Create current consumption coordinator"""
  key = DATA_CURRENT_CONSUMPTION_KEY.format(device_id)

  # Reset data as we might have new information
  hass.data[DOMAIN][key] = None

  async def async_update_data():
    """Fetch data from API endpoint."""
    current: datetime = now()
    previous_consumption = hass.data[DOMAIN][key] if key in hass.data[DOMAIN] else None
    hass.data[DOMAIN][key] = await async_get_live_consumption(
      current,
      client,
      device_id,
      previous_consumption,
      refresh_rate_in_minutes
    )
    
    return hass.data[DOMAIN][key]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"current_consumption_{device_id}",
    update_method=async_update_data,
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )
  
  await coordinator.async_config_entry_first_refresh()

  return coordinator