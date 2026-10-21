import logging
from datetime import datetime, timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.dt import now

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.scratchcard import OctoplusScratchcardResponse
from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_CLIENT,
  DATA_OCTOPLUS_SCRATCHCARD,
  DOMAIN,
  REFRESH_RATE_IN_MINUTES_OCTOPLUS_SCRATCHCARD,
)
from . import BaseCoordinatorResult

_LOGGER = logging.getLogger(__name__)


class OctoplusScratchcardCoordinatorResult(BaseCoordinatorResult):
  def __init__(self, last_evaluated: datetime, request_attempts: int, data: OctoplusScratchcardResponse | None, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_OCTOPLUS_SCRATCHCARD, None, last_error)
    self.data = data


async def async_refresh_octoplus_scratchcard(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_id: str,
    existing_result: OctoplusScratchcardCoordinatorResult | None,
) -> OctoplusScratchcardCoordinatorResult:
  if existing_result is None or current >= existing_result.next_refresh:
    try:
      data = await client.async_get_octoplus_scratchcard(account_id)
      return OctoplusScratchcardCoordinatorResult(current, 1, data)
    except ApiException as e:
      if existing_result is not None:
        result = OctoplusScratchcardCoordinatorResult(existing_result.last_evaluated, existing_result.request_attempts + 1, existing_result.data, e)
        if result.request_attempts == 2:
          _LOGGER.warning("Failed to retrieve Octoplus scratchcard data - using cached data.")
      else:
        result = OctoplusScratchcardCoordinatorResult(
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_SCRATCHCARD), 2, None, e
        )
        _LOGGER.warning("Failed to retrieve Octoplus scratchcard data.")
      return result

  return existing_result


async def async_setup_octoplus_scratchcard_coordinator(hass, account_id: str):
  async def async_update_data():
    """Fetch data from API endpoint."""
    account_data = hass.data[DOMAIN][account_id]
    account_data[DATA_OCTOPLUS_SCRATCHCARD] = await async_refresh_octoplus_scratchcard(
      now(),
      account_data[DATA_CLIENT],
      account_id,
      account_data.get(DATA_OCTOPLUS_SCRATCHCARD),
    )
    return account_data[DATA_OCTOPLUS_SCRATCHCARD]

  return DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"octoplus_scratchcard_{account_id}",
    update_method=async_update_data,
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True,
  )
