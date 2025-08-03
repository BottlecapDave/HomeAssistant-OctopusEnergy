import logging
from datetime import datetime, timedelta
from typing import Any, Callable

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
  EVENT_FAN_CLUB_DISCOUNTS,
  REFRESH_RATE_IN_MINUTES_FAN_CLUB_DISCOUNTS,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from . import BaseCoordinatorResult
from ..fan_club import DiscountSource, combine_discounts, mock_fan_club_forecast

_LOGGER = logging.getLogger(__name__)

class FanClubDiscountCoordinatorResult(BaseCoordinatorResult):
  last_evaluated: datetime
  discounts: list[DiscountSource]

  def __init__(self, last_evaluated: datetime, request_attempts: int, discounts: list[DiscountSource], last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_FAN_CLUB_DISCOUNTS, None, last_error)
    self.discounts = discounts

async def async_refresh_fan_club_discounts(
    current: datetime,
    account_id: str,
    client: OctopusEnergyApiClient,
    existing_result: FanClubDiscountCoordinatorResult,
    fire_event: Callable[[str, "dict[str, Any]"], None],
    mock_fan_club: bool = False
) -> FanClubDiscountCoordinatorResult:
  if existing_result is None or current >= existing_result.next_refresh:
    try:
      if mock_fan_club:
        result = mock_fan_club_forecast()
      else:
        result = await client.async_get_fan_club_discounts(account_id)

      discounts: list[DiscountSource] = []
      if result is not None and result.fanClubStatus is not None:
        for item in result.fanClubStatus:
          discounts.append(DiscountSource(source=item.discountSource, discounts=combine_discounts(item)))

          # Fire events
          event_data = { "discounts": list(map(lambda x: x.dict(), discounts[-1].discounts)), "account_id": account_id, "source": discounts[-1].source }
          fire_event(EVENT_FAN_CLUB_DISCOUNTS, event_data)

      return FanClubDiscountCoordinatorResult(current, 1, discounts)
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

async def async_setup_fan_club_discounts_coordinator(hass, account_id: str, mock_fan_club: bool):
  async def async_update_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]

    hass.data[DOMAIN][account_id][DATA_FAN_CLUB_DISCOUNTS] = await async_refresh_fan_club_discounts(
      current,
      account_id,
      client,
      hass.data[DOMAIN][account_id][DATA_FAN_CLUB_DISCOUNTS] if DATA_FAN_CLUB_DISCOUNTS in hass.data[DOMAIN][account_id] else None,
      hass.bus.async_fire,
      mock_fan_club
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