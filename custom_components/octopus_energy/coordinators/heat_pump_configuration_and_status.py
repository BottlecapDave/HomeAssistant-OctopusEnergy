import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR,
  DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY,
  DOMAIN,

  DATA_CLIENT,
  DATA_ACCOUNT,
  DATA_ACCOUNT_COORDINATOR,
  REFRESH_RATE_IN_MINUTES_HEAT_PUMP,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.heat_pump import HeatPumpResponse
from . import BaseCoordinatorResult

from ..heat_pump import mock_heat_pump_status_and_configuration

_LOGGER = logging.getLogger(__name__)

class HeatPumpCoordinatorResult(BaseCoordinatorResult):
  euid: str
  data: HeatPumpResponse

  def __init__(self, last_evaluated: datetime, request_attempts: int, euid: str, data: HeatPumpResponse, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_HEAT_PUMP, None, last_error)
    self.euid = euid
    self.data = data

async def async_refresh_heat_pump_configuration_and_status(
  current: datetime,
  client: OctopusEnergyApiClient,
  account_info,
  euid: str,
  existing_heat_pump_result: HeatPumpCoordinatorResult | None,
  is_mocked: bool
):
  if (account_info is not None):
    account_id = account_info["id"]
    if (existing_heat_pump_result is None or current >= existing_heat_pump_result.next_refresh):
      status_and_configuration = None
      raised_exception = None

      if is_mocked:
        status_and_configuration = mock_heat_pump_status_and_configuration()
      elif euid is not None:
        try:
          status_and_configuration = await client.async_get_heat_pump_configuration_and_status(account_id, euid)
          _LOGGER.debug(f'Heat Pump config and status retrieved for account {account_id} and device {euid}')
        except Exception as e:
          if isinstance(e, ApiException) == False:
            raise

          raised_exception = e
          _LOGGER.debug(f'Failed to retrieve heat pump configuration and status for account {account_id} and device {euid}')

      if status_and_configuration is not None:
        return HeatPumpCoordinatorResult(current, 1, euid, status_and_configuration)
      
      result = None
      if (existing_heat_pump_result is not None):
        result = HeatPumpCoordinatorResult(
          existing_heat_pump_result.last_evaluated,
          existing_heat_pump_result.request_attempts + 1,
          euid,
          existing_heat_pump_result.data,
          last_error=raised_exception
        )

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve new heat pump configuration and status - using cached settings. See diagnostics sensor for more information.")
      else:
        # We want to force into our fallback mode
        result = HeatPumpCoordinatorResult(current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_HEAT_PUMP), 2, euid, None, last_error=raised_exception)
        _LOGGER.warning(f"Failed to retrieve new heat pump configuration and status. See diagnostics sensor for more information.")
      
      return result
  
  return existing_heat_pump_result
  
async def async_setup_heat_pump_coordinator(hass, account_id: str, euid: str, mock_heat_pump_data: bool):
  key = DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_KEY.format(euid)
  # Reset data as we might have new information
  hass.data[DOMAIN][account_id][key] = None
  
  async def async_update_heat_pump_data():
    """Fetch data from API endpoint."""
    # Request our account data to be refreshed
    account_coordinator = hass.data[DOMAIN][account_id][DATA_ACCOUNT_COORDINATOR]
    if account_coordinator is not None:
      await account_coordinator.async_request_refresh()

    current = utcnow()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
      
    hass.data[DOMAIN][account_id][key] = await async_refresh_heat_pump_configuration_and_status(
      current,
      client,
      account_info,
      euid,
      hass.data[DOMAIN][account_id][key] if key in hass.data[DOMAIN][account_id] else None,
      mock_heat_pump_data
    )

    return hass.data[DOMAIN][account_id][key]

  hass.data[DOMAIN][account_id][DATA_HEAT_PUMP_CONFIGURATION_AND_STATUS_COORDINATOR.format(euid)] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"heat_pump_{account_id}",
    update_method=async_update_heat_pump_data,
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )