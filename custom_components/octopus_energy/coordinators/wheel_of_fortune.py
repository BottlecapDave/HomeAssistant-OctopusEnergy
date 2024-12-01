import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,
  DATA_CLIENT,
  DATA_WHEEL_OF_FORTUNE_SPINS,
  REFRESH_RATE_IN_MINUTES_OCTOPLUS_WHEEL_OF_FORTUNE,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.wheel_of_fortune import WheelOfFortuneSpinsResponse
from . import BaseCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class WheelOfFortuneSpinsCoordinatorResult(BaseCoordinatorResult):
  last_evaluated: datetime
  spins: WheelOfFortuneSpinsResponse

  def __init__(self, last_evaluated: datetime, request_attempts: int, spins: WheelOfFortuneSpinsResponse, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_OCTOPLUS_WHEEL_OF_FORTUNE, None, last_error)
    self.spins = spins

async def async_refresh_wheel_of_fortune_spins(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_id: str,
    existing_result: WheelOfFortuneSpinsCoordinatorResult
) -> WheelOfFortuneSpinsCoordinatorResult:
  if existing_result is None or current >= existing_result.next_refresh:
    try:
      result = await client.async_get_wheel_of_fortune_spins(account_id)

      return WheelOfFortuneSpinsCoordinatorResult(current, 1, result)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      
      result = None
      if (existing_result is not None):
        result = WheelOfFortuneSpinsCoordinatorResult(existing_result.last_evaluated, existing_result.request_attempts + 1, existing_result.spins, last_error=e)
        if (result.request_attempts == 2):
          _LOGGER.warning(f'Failed to retrieve wheel of fortune spins - using cached data. See diagnostics sensor for more information.')
      else:
        result = WheelOfFortuneSpinsCoordinatorResult(
          # We want to force into our fallback mode
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_WHEEL_OF_FORTUNE),
          2,
          None,
          last_error=e
        )
        _LOGGER.warning(f'Failed to retrieve wheel of fortune spins. See diagnostics sensor for more information.')

      return result
  
  return existing_result

async def async_setup_wheel_of_fortune_spins_coordinator(hass, account_id: str):
  async def async_update_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]

    hass.data[DOMAIN][account_id][DATA_WHEEL_OF_FORTUNE_SPINS] = await async_refresh_wheel_of_fortune_spins(
      current,
      client,
      account_id,
      hass.data[DOMAIN][account_id][DATA_WHEEL_OF_FORTUNE_SPINS] if DATA_WHEEL_OF_FORTUNE_SPINS in hass.data[DOMAIN][account_id] else None
    )

    return hass.data[DOMAIN][account_id][DATA_WHEEL_OF_FORTUNE_SPINS]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"wheel_of_fortune_spins_{account_id}",
    update_method=async_update_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  return coordinator