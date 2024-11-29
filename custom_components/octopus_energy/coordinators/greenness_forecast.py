import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_GREENNESS_FORECAST_COORDINATOR,
  DOMAIN,
  DATA_CLIENT,
  DATA_GREENNESS_FORECAST,
  REFRESH_RATE_IN_MINUTES_GREENNESS_FORECAST,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from . import BaseCoordinatorResult
from ..api_client.greenness_forecast import GreennessForecast

_LOGGER = logging.getLogger(__name__)

class GreennessForecastCoordinatorResult(BaseCoordinatorResult):
  last_evaluated: datetime
  forecast: list[GreennessForecast]

  def __init__(self, last_evaluated: datetime, request_attempts: int, forecast: list[GreennessForecast], last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_GREENNESS_FORECAST, None, last_error)
    self.forecast = forecast

async def async_refresh_greenness_forecast(
    current: datetime,
    client: OctopusEnergyApiClient,
    existing_result: GreennessForecastCoordinatorResult
) -> GreennessForecastCoordinatorResult:
  if existing_result is None or current >= existing_result.next_refresh:
    try:
      result = await client.async_get_greenness_forecast()

      return GreennessForecastCoordinatorResult(current, 1, result)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      
      result = None
      if (existing_result is not None):
        result = GreennessForecastCoordinatorResult(existing_result.last_evaluated, existing_result.request_attempts + 1, existing_result.forecast, last_error=e)
        
        if (result.request_attempts == 2):
          _LOGGER.warning(f'Failed to retrieve greenness forecast - using cached data. See diagnostics sensor for more information.')
      else:
        result = GreennessForecastCoordinatorResult(
          # We want to force into our fallback mode
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_GREENNESS_FORECAST),
          2,
          None,
          last_error=e
        )
        _LOGGER.warning(f'Failed to retrieve greenness forecast. See diagnostics sensor for more information.')

      return result
  
  return existing_result

async def async_setup_greenness_forecast_coordinator(hass, account_id: str):
  async def async_update_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]

    hass.data[DOMAIN][account_id][DATA_GREENNESS_FORECAST] = await async_refresh_greenness_forecast(
      current,
      client,
      hass.data[DOMAIN][account_id][DATA_GREENNESS_FORECAST] if DATA_GREENNESS_FORECAST in hass.data[DOMAIN][account_id] else None
    )

    return hass.data[DOMAIN][account_id][DATA_GREENNESS_FORECAST]

  hass.data[DOMAIN][account_id][DATA_GREENNESS_FORECAST_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"{account_id}_greenness_forecast",
    update_method=async_update_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  return hass.data[DOMAIN][account_id][DATA_GREENNESS_FORECAST_COORDINATOR]