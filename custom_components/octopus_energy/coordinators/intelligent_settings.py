import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)
from homeassistant.helpers import storage

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,

  DATA_CLIENT,
  DATA_ACCOUNT,
  DATA_ACCOUNT_COORDINATOR,
  DATA_INTELLIGENT_SETTINGS,
  DATA_INTELLIGENT_SETTINGS_COORDINATOR,
  REFRESH_RATE_IN_MINUTES_INTELLIGENT,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.intelligent_settings import IntelligentSettings
from . import BaseCoordinatorResult

from ..intelligent import has_intelligent_tariff, mock_intelligent_settings

_LOGGER = logging.getLogger(__name__)

class IntelligentCoordinatorResult(BaseCoordinatorResult):
  settings: IntelligentSettings

  def __init__(self, last_evaluated: datetime, request_attempts: int, settings: IntelligentSettings, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_INTELLIGENT, None, last_error)
    self.settings = settings

async def async_refresh_intelligent_settings(
  current: datetime,
  client: OctopusEnergyApiClient,
  account_info,
  device_id: str,
  existing_intelligent_settings_result: IntelligentCoordinatorResult | None,
  is_settings_mocked: bool
):
  if (account_info is not None):
    account_id = account_info["id"]
    if (existing_intelligent_settings_result is None or current >= existing_intelligent_settings_result.next_refresh):
      settings = None
      raised_exception = None
      if device_id is not None and has_intelligent_tariff(current, account_info):
        try:
          settings = await client.async_get_intelligent_settings(account_id, device_id)
          _LOGGER.debug(f'Intelligent settings retrieved for account {account_id} device {device_id}')
        except Exception as e:
          if isinstance(e, ApiException) == False:
            raise

          raised_exception = e
          _LOGGER.debug(f'Failed to retrieve intelligent settings for account {account_id}')

      if is_settings_mocked:
        settings = mock_intelligent_settings()

      if settings is not None:
        return IntelligentCoordinatorResult(current, 1, settings)
      
      result = None
      if (existing_intelligent_settings_result is not None):
        result = IntelligentCoordinatorResult(
          existing_intelligent_settings_result.last_evaluated,
          existing_intelligent_settings_result.request_attempts + 1,
          existing_intelligent_settings_result.settings,
          last_error=raised_exception
        )

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve new intelligent settings - using cached settings. See diagnostics sensor for more information.")
      else:
        # We want to force into our fallback mode
        result = IntelligentCoordinatorResult(current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT), 2, None, last_error=raised_exception)
        _LOGGER.warning(f"Failed to retrieve new intelligent settings. See diagnostics sensor for more information.")
      
      return result
  
  return existing_intelligent_settings_result
  
async def async_setup_intelligent_settings_coordinator(hass, account_id: str, device_id: str, mock_intelligent_data: bool):
  # Reset data rates as we might have new information
  hass.data[DOMAIN][account_id][DATA_INTELLIGENT_SETTINGS] = None
  
  async def async_update_intelligent_settings_data():
    """Fetch data from API endpoint."""
    # Request our account data to be refreshed
    account_coordinator = hass.data[DOMAIN][account_id][DATA_ACCOUNT_COORDINATOR]
    if account_coordinator is not None:
      await account_coordinator.async_request_refresh()

    current = utcnow()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
      
    hass.data[DOMAIN][account_id][DATA_INTELLIGENT_SETTINGS] = await async_refresh_intelligent_settings(
      current,
      client,
      account_info,
      device_id,
      hass.data[DOMAIN][account_id][DATA_INTELLIGENT_SETTINGS] if DATA_INTELLIGENT_SETTINGS in hass.data[DOMAIN][account_id] else None,
      mock_intelligent_data
    )

    return hass.data[DOMAIN][account_id][DATA_INTELLIGENT_SETTINGS]

  hass.data[DOMAIN][account_id][DATA_INTELLIGENT_SETTINGS_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"intelligent_settings_{account_id}",
    update_method=async_update_intelligent_settings_data,
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )