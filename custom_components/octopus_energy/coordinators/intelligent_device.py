import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from homeassistant.helpers import issue_registry as ir

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_INTELLIGENT_DEVICE,
  DOMAIN,

  DATA_CLIENT,
  DATA_INTELLIGENT_DEVICE_COORDINATOR,
  REFRESH_RATE_IN_MINUTES_INTELLIGENT_DEVICE,
  REPAIR_INTELLIGENT_DEVICE_CHANGED,
  REPAIR_INTELLIGENT_DEVICE_NOT_FOUND,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from . import BaseCoordinatorResult
from ..api_client.intelligent_device import IntelligentDevice
from ..intelligent import mock_intelligent_device

_LOGGER = logging.getLogger(__name__)

class IntelligentDeviceCoordinatorResult(BaseCoordinatorResult):
  device: IntelligentDevice

  def __init__(self, last_evaluated: datetime, request_attempts: int, device: IntelligentDevice, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_INTELLIGENT_DEVICE, None, last_error)
    self.device = device

async def async_refresh_device(
  hass,
  current: datetime,
  client: OctopusEnergyApiClient,
  account_id: str,
  current_intelligent_device: IntelligentDevice,
  mock_intelligent_data: bool,
  previous_request: IntelligentDeviceCoordinatorResult
):
  if (current >= previous_request.next_refresh):
    device = None
    try:
      if mock_intelligent_data:
        device = mock_intelligent_device()
      else:
        device = await client.async_get_intelligent_device(account_id)

      if device is None:
        ir.async_create_issue(
          hass,
          DOMAIN,
          REPAIR_INTELLIGENT_DEVICE_NOT_FOUND.format(account_id),
          is_fixable=False,
          severity=ir.IssueSeverity.ERROR,
          translation_key="intelligent_device_not_found",
          translation_placeholders={ "account_id": account_id },
        )
      else:
        _LOGGER.debug('IntelligentDevice information retrieved')

        ir.async_delete_issue(hass, DOMAIN, REPAIR_INTELLIGENT_DEVICE_NOT_FOUND.format(account_id))

        if device.id != current_intelligent_device.id:
          ir.async_create_issue(
            hass,
            DOMAIN,
            REPAIR_INTELLIGENT_DEVICE_CHANGED.format(account_id),
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="intelligent_device_changed",
            translation_placeholders={ "account_id": account_id },
          )
        else:
          ir.async_delete_issue(hass, DOMAIN, REPAIR_INTELLIGENT_DEVICE_CHANGED.format(account_id))

        return IntelligentDeviceCoordinatorResult(current, 1, device)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      
      result = IntelligentDeviceCoordinatorResult(
        previous_request.last_evaluated,
        previous_request.request_attempts + 1,
        previous_request.device,
        last_error=e
      )
      
      if (result.request_attempts == 2):
        _LOGGER.warning(f'Failed to retrieve intelligent device information - using cached version. See diagnostics sensor for more information.')
      
      return result

  return previous_request

async def async_setup_intelligent_device_coordinator(hass, account_id: str, intelligent_device: IntelligentDevice, mock_intelligent_data: bool):
  async def async_update_intelligent_device_data():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]

    hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE] = await async_refresh_device(
      hass,
      current,
      client,
      account_id,
      intelligent_device,
      mock_intelligent_data,
      hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE]
    )
    
    return hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE]

  hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"update_account-{account_id}",
    update_method=async_update_intelligent_device_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )