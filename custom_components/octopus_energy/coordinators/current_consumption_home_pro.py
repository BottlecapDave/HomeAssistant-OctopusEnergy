from datetime import (datetime, timedelta)
import logging

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  DATA_HOME_PRO_CURRENT_CONSUMPTION_KEY,
  DOMAIN,
  HOME_PRO_COORDINATOR_REFRESH_IN_SECONDS,
  REFRESH_RATE_IN_MINUTES_HOME_PRO_CONSUMPTION,
)

from ..api_client import (ApiException)
from ..api_client_home_pro import OctopusEnergyHomeProApiClient

from .current_consumption import CurrentConsumptionCoordinatorResult

_LOGGER = logging.getLogger(__name__)

async def async_get_home_pro_consumption(
  current_date: datetime,
  client: OctopusEnergyHomeProApiClient,
  is_electricity: bool,
  previous_consumption: CurrentConsumptionCoordinatorResult
):
  if previous_consumption is None or current_date >= previous_consumption.next_refresh:
    
    try:
      data = await client.async_get_consumption(is_electricity)
      if data is not None:
        _LOGGER.debug(f'Retrieved current consumption data from home pro for {"electricity" if is_electricity else "gas"}')
        return CurrentConsumptionCoordinatorResult(current_date, 1, REFRESH_RATE_IN_MINUTES_HOME_PRO_CONSUMPTION, data)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise

      result: CurrentConsumptionCoordinatorResult = None
      if previous_consumption is not None:
        result = CurrentConsumptionCoordinatorResult(
          previous_consumption.last_retrieved,
          previous_consumption.request_attempts + 1,
          REFRESH_RATE_IN_MINUTES_HOME_PRO_CONSUMPTION,
          previous_consumption.data
        )
        _LOGGER.warning(f'Failed to retrieve current consumption data from home pro data - using cached version. Next attempt at {result.next_refresh}')
      else:
        result = CurrentConsumptionCoordinatorResult(
          # We want to force into our fallback mode
          current_date - timedelta(minutes=REFRESH_RATE_IN_MINUTES_HOME_PRO_CONSUMPTION),
          2,
          REFRESH_RATE_IN_MINUTES_HOME_PRO_CONSUMPTION,
          None
        )
        _LOGGER.warning(f'Failed to retrieve current consumption data from home pro data. Next attempt at {result.next_refresh}')
      
      return result
  
  return previous_consumption

async def async_create_home_pro_current_consumption_coordinator(hass, account_id: str, client: OctopusEnergyHomeProApiClient, is_electricity: bool):
  """Create current consumption coordinator"""
  key = DATA_HOME_PRO_CURRENT_CONSUMPTION_KEY.format(is_electricity)

  # Reset data as we might have new information
  hass.data[DOMAIN][account_id][key] = None

  async def async_update_data():
    """Fetch data from API endpoint."""
    current: datetime = now()
    previous_consumption = hass.data[DOMAIN][account_id][key] if key in hass.data[DOMAIN][account_id] else None
    hass.data[DOMAIN][account_id][key] = await async_get_home_pro_consumption(
      current,
      client,
      is_electricity,
      previous_consumption
    )
    
    return hass.data[DOMAIN][account_id][key]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"home_pro_current_consumption_{is_electricity}",
    update_method=async_update_data,
    update_interval=timedelta(seconds=HOME_PRO_COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  return coordinator