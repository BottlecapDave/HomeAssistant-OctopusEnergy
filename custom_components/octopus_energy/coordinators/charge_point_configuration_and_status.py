import asyncio
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
  is_mocked: bool,
  force: bool = False
):
  if (account_info is not None):
    account_id = account_info["id"]
    if (force or existing_charge_point_result is None or current >= existing_charge_point_result.next_refresh):
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

class ChargePointDataUpdateCoordinator(DataUpdateCoordinator):
  """DataUpdateCoordinator for a single charge point, with the ability to
  poll much more frequently for a short window - e.g. right after a user
  starts/stops boost charging, or around a scheduled charging period
  boundary - so dependent entities (like live power) pick up the resulting
  operational state change much faster than the normal refresh interval
  would, without permanently polling faster all the time.
  """

  def __init__(self, hass, account_id: str, device_uuid: str, property_id: str, mock_charge_point_data: bool):
    self.__account_id = account_id
    self.__device_uuid = device_uuid
    self.__property_id = property_id
    self.__mock_charge_point_data = mock_charge_point_data
    self.__normal_interval = timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS)
    self.__burst_task: asyncio.Task | None = None
    self.__force_next_refresh = False

    super().__init__(
      hass,
      _LOGGER,
      name=f"charge_point_{account_id}",
      update_method=self.__async_update_charge_point_data,
      update_interval=self.__normal_interval,
      always_update=True
    )

  async def __async_update_charge_point_data(self):
    """Fetch data from API endpoint."""
    account_id = self.__account_id
    key = DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY.format(self.__device_uuid)

    # Request our account data to be refreshed
    account_coordinator = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT_COORDINATOR]
    if account_coordinator is not None:
      await account_coordinator.async_request_refresh()

    current = utcnow()
    client: OctopusEnergyApiClient = self.hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_result = self.hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None

    force = self.__force_next_refresh
    self.__force_next_refresh = False

    self.hass.data[DOMAIN][account_id][key] = await async_refresh_charge_point_configuration_and_status(
      current,
      client,
      account_info,
      self.__property_id,
      self.__device_uuid,
      self.hass.data[DOMAIN][account_id][key] if key in self.hass.data[DOMAIN][account_id] else None,
      self.__mock_charge_point_data,
      force=force
    )

    return self.hass.data[DOMAIN][account_id][key]

  def async_start_burst_refresh(self, interval_seconds: int = 10, duration_seconds: int = 60):
    """(Re)start a short burst of frequent, forced polling. Cancels and
    restarts if one is already running, so overlapping triggers (e.g.
    boost turned on then off again within the window) just extend it
    rather than running two bursts in parallel."""
    if self.__burst_task is not None and not self.__burst_task.done():
      self.__burst_task.cancel()
    self.__burst_task = self.hass.async_create_task(self.__async_run_burst(interval_seconds, duration_seconds))

  async def __async_run_burst(self, interval_seconds: int, duration_seconds: int):
    self.update_interval = timedelta(seconds=interval_seconds)
    try:
      end = utcnow() + timedelta(seconds=duration_seconds)
      while utcnow() < end:
        # Wait a full interval before polling - the change we're bursting
        # around (e.g. a boost toggle) hasn't necessarily propagated on
        # Octopus's side yet, so an immediate poll can catch the charger
        # still in its pre-change state and read as an instant revert.
        await asyncio.sleep(interval_seconds)
        self.__force_next_refresh = True
        await self.async_request_refresh()
    finally:
      self.update_interval = self.__normal_interval

async def async_setup_charge_point_coordinator(hass, account_id: str, property_id: str, device_uuid: str, mock_charge_point_data: bool):
  key = DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_KEY.format(device_uuid)
  # Reset data as we might have new information
  hass.data[DOMAIN][account_id][key] = None

  hass.data[DOMAIN][account_id][DATA_CHARGE_POINT_CONFIGURATION_AND_STATUS_COORDINATOR.format(device_uuid)] = ChargePointDataUpdateCoordinator(
    hass, account_id, device_uuid, property_id, mock_charge_point_data
  )
