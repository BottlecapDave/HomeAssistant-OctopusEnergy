import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR,
  DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY,
  DOMAIN,

  DATA_CLIENT,
  DATA_ACCOUNT,
  DATA_ACCOUNT_COORDINATOR,
  REFRESH_RATE_IN_MINUTES_CHARGE_POINT,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.charge_point import OnboardedChargePoint
from . import BaseCoordinatorResult

from ..charge_point import mock_charge_point_status_and_configuration

_LOGGER = logging.getLogger(__name__)

class ChargePointCoordinatorResult(BaseCoordinatorResult):
  device_uuid: str
  data: OnboardedChargePoint

  def __init__(self, last_evaluated: datetime, request_attempts: int, device_uuid: str, data: OnboardedChargePoint, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_CHARGE_POINT, None, last_error)
    self.device_uuid = device_uuid
    self.data = data

async def async_refresh_charge_point_configuration_and_status(
  current: datetime,
  client: OctopusEnergyApiClient,
  account_info,
  property_id: str,
  device_uuid: str,
  existing_charge_point_result: ChargePointCoordinatorResult | None,
  is_mocked: bool
):
  if (account_info is not None):
    account_id = account_info["id"]
    if (existing_charge_point_result is None or current >= existing_charge_point_result.next_refresh):
      status_and_configuration = None
      raised_exception = None

      if is_mocked:
        status_and_configuration = mock_charge_point_status_and_configuration()
      elif device_uuid is not None:
        try:
          status_and_configuration = await client.async_get_charge_point_configuration_and_status(account_id, property_id, device_uuid)
          _LOGGER.debug(f'Charge point config and status retrieved for account {account_id} and device {device_uuid}')
        except Exception as e:
          if isinstance(e, ApiException) == False:
            raise

          raised_exception = e
          _LOGGER.debug(f'Failed to retrieve charge point configuration and status for account {account_id} and device {device_uuid}')

      if status_and_configuration is not None:
        return ChargePointCoordinatorResult(current, 1, device_uuid, status_and_configuration)

      result = None
      if (existing_charge_point_result is not None):
        result = ChargePointCoordinatorResult(
          existing_charge_point_result.last_evaluated,
          existing_charge_point_result.request_attempts + 1,
          device_uuid,
          existing_charge_point_result.data,
          last_error=raised_exception
        )

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve new charge point configuration and status - using cached settings. See diagnostics sensor for more information.")
      else:
        # We want to force into our fallback mode
        result = ChargePointCoordinatorResult(current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_CHARGE_POINT), 2, device_uuid, None, last_error=raised_exception)
        _LOGGER.warning(f"Failed to retrieve new charge point configuration and status. See diagnostics sensor for more information.")

      return result

  return existing_charge_point_result

async def async_setup_charge_point_coordinator(hass, account_id: str, property_id: str, device_uuid: str, mock_charge_point_data: bool):
  key = DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY.format(device_uuid)
  # Reset data as we might have new information
  hass.data[DOMAIN][account_id][key] = None

  async def async_update_charge_point_data():
    """Fetch data from API endpoint."""
    # Request our account data to be refreshed
    account_coordinator = hass.data[DOMAIN][account_id][DATA_ACCOUNT_COORDINATOR]
    if account_coordinator is not None:
      await account_coordinator.async_request_refresh()

    current = utcnow()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None

    hass.data[DOMAIN][account_id][key] = await async_refresh_charge_point_configuration_and_status(
      current,
      client,
      account_info,
      property_id,
      device_uuid,
      hass.data[DOMAIN][account_id][key] if key in hass.data[DOMAIN][account_id] else None,
      mock_charge_point_data
    )

    return hass.data[DOMAIN][account_id][key]

  hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR.format(device_uuid)] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"charge_point_{account_id}",
    update_method=async_update_charge_point_data,
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )
