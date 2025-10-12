import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from homeassistant.helpers import issue_registry as ir

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_INTELLIGENT_DEVICES,
  DOMAIN,

  DATA_CLIENT,
  DATA_INTELLIGENT_DEVICE_COORDINATOR,
  REFRESH_RATE_IN_MINUTES_INTELLIGENT_DEVICE,
  REPAIR_INTELLIGENT_DEVICE_ADDED,
  REPAIR_INTELLIGENT_DEVICE_CHANGED,
  REPAIR_INTELLIGENT_DEVICE_NOT_FOUND,
  REPAIR_INTELLIGENT_DEVICE_REMOVED,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from . import BaseCoordinatorResult
from ..api_client.intelligent_device import IntelligentDevice
from ..intelligent import mock_intelligent_devices
from ..utils.repairs import safe_repair_key

_LOGGER = logging.getLogger(__name__)

class IntelligentDeviceCoordinatorResult(BaseCoordinatorResult):
  devices: list[IntelligentDevice]

  def __init__(self, last_evaluated: datetime, request_attempts: int, devices: list[IntelligentDevice], last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_INTELLIGENT_DEVICE, None, last_error)
    self.devices = devices

async def async_refresh_devices(
  hass,
  current: datetime,
  client: OctopusEnergyApiClient,
  account_id: str,
  current_intelligent_devices: list[IntelligentDevice],
  mock_intelligent_data: bool,
  previous_request: IntelligentDeviceCoordinatorResult
):
  if (current >= previous_request.next_refresh):

    # Delete legacy issues
    ir.async_delete_issue(hass, DOMAIN, REPAIR_INTELLIGENT_DEVICE_NOT_FOUND.format(account_id))

    try:
      if mock_intelligent_data:
        devices = mock_intelligent_devices()
      else:
        devices = await client.async_get_intelligent_devices(account_id)

      # Check if new devices have been added
      for device in devices:
        device_present = False
        for current_device in current_intelligent_devices:
          if device.id == current_device.id:
            device_present = True
            break

        if device_present == False:
          ir.async_create_issue(
            hass,
            DOMAIN,
            safe_repair_key(REPAIR_INTELLIGENT_DEVICE_ADDED, device.id),
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="intelligent_device_added",
            translation_placeholders={ "account_id": account_id },
          )
        else:
          ir.async_delete_issue(hass, DOMAIN, safe_repair_key(REPAIR_INTELLIGENT_DEVICE_ADDED, device.id))

      # Check if devices have been removed
      for current_device in current_intelligent_devices:
        # Delete legacy issues
        ir.async_delete_issue(hass, DOMAIN, REPAIR_INTELLIGENT_DEVICE_CHANGED.format(device.id))
        device_present = False
        for device in devices:
          if device.id == current_device.id:
            device_present = True
            break

        if device_present == False:
          ir.async_create_issue(
            hass,
            DOMAIN,
            safe_repair_key(REPAIR_INTELLIGENT_DEVICE_REMOVED, device.id),
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="intelligent_device_removed",
            translation_placeholders={ "account_id": account_id },
          )
        else:
          ir.async_delete_issue(hass, DOMAIN, safe_repair_key(REPAIR_INTELLIGENT_DEVICE_REMOVED, device.id))

      return IntelligentDeviceCoordinatorResult(current, 1, devices)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise
      
      result = IntelligentDeviceCoordinatorResult(
        previous_request.last_evaluated,
        previous_request.request_attempts + 1,
        previous_request.devices,
        last_error=e
      )
      
      if (result.request_attempts == 2):
        _LOGGER.warning(f'Failed to retrieve intelligent device information - using cached version. See diagnostics sensor for more information.')
      
      return result

  return previous_request

async def async_setup_intelligent_devices_coordinator(hass, account_id: str, intelligent_devices: list[IntelligentDevice], mock_intelligent_data: bool):
  async def async_update_intelligent_devices_data():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]

    hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICES] = await async_refresh_devices(
      hass,
      current,
      client,
      account_id,
      intelligent_devices,
      mock_intelligent_data,
      hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICES]
    )
    
    return hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICES]

  hass.data[DOMAIN][account_id][DATA_INTELLIGENT_DEVICE_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"update_intelligent_devices_{account_id}",
    update_method=async_update_intelligent_devices_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )