import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_FAN_CLUB_DISCOUNTS_COORDINATOR,
  DOMAIN,
  DATA_CLIENT,
  DATA_FAN_CLUB_DISCOUNTS,
  REFRESH_RATE_IN_MINUTES_FAN_CLUB_DISCOUNTS,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from . import BaseCoordinatorResult
from ..api_client.fan_club import FanClubStatusItem

_LOGGER = logging.getLogger(__name__)

class FanClubDiscountCoordinatorResult(BaseCoordinatorResult):
  last_evaluated: datetime
  discounts: list[FanClubStatusItem]

  def __init__(self, last_evaluated: datetime, request_attempts: int, discounts: list[FanClubStatusItem], last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_FAN_CLUB_DISCOUNTS, None, last_error)
    self.discounts = discounts

async def async_refresh_fan_club_discounts(
    current: datetime,
    account_id: str,
    client: OctopusEnergyApiClient,
    existing_result: FanClubDiscountCoordinatorResult
) -> FanClubDiscountCoordinatorResult:
  if existing_result is None or current >= existing_result.next_refresh:
    try:
      result = await client.async_get_fan_club_discounts(account_id)

      return FanClubDiscountCoordinatorResult(current, 1, result.fanClubStatus if result is not None else [])
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      
      result = None
      if (existing_result is not None):
        result = FanClubDiscountCoordinatorResult(existing_result.last_evaluated, existing_result.request_attempts + 1, existing_result.discounts, last_error=e)
        
        if (result.request_attempts == 2):
          _LOGGER.warning(f'Failed to retrieve fan club discounts - using cached data. See diagnostics sensor for more information.')
      else:
        result = FanClubDiscountCoordinatorResult(
          # We want to force into our fallback mode
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_FAN_CLUB_DISCOUNTS),
          2,
          None,
          last_error=e
        )
        _LOGGER.warning(f'Failed to retrieve fan club discounts. See diagnostics sensor for more information.')

      return result
  
  return existing_result

async def async_setup_fan_club_discounts_coordinator(hass, account_id: str):
  async def async_update_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]

    hass.data[DOMAIN][account_id][DATA_FAN_CLUB_DISCOUNTS] = await async_refresh_fan_club_discounts(
      current,
      account_id,
      client,
      hass.data[DOMAIN][account_id][DATA_FAN_CLUB_DISCOUNTS] if DATA_FAN_CLUB_DISCOUNTS in hass.data[DOMAIN][account_id] else None
    )

    return hass.data[DOMAIN][account_id][DATA_FAN_CLUB_DISCOUNTS]

  hass.data[DOMAIN][account_id][DATA_FAN_CLUB_DISCOUNTS_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"{account_id}_fan_club_discounts",
    update_method=async_update_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  return hass.data[DOMAIN][account_id][DATA_FAN_CLUB_DISCOUNTS_COORDINATOR]