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
  DATA_CHARGE_PACK_COORDINATOR,
  DATA_CHARGE_PACK_DISPATCHES,
  REFRESH_RATE_IN_MINUTES_CHARGE_PACK,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.charge_pack import ChargePackDispatch, ChargePackStatus, ChargePackTelemetry
from ..charge_pack import update_history
from ..storage.charge_pack import async_save_cached_charge_pack_history
from . import BaseCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class ChargePackDispatchesCoordinatorResult(BaseCoordinatorResult):
  planned: list[ChargePackDispatch]
  history: list[ChargePackDispatch]
  status: ChargePackStatus | None
  telemetry: ChargePackTelemetry | None

  def __init__(self, last_evaluated: datetime, request_attempts: int, planned: list[ChargePackDispatch],
               history: list[ChargePackDispatch], last_retrieved: datetime | None = None, last_error: Exception | None = None,
               status: ChargePackStatus | None = None, telemetry: ChargePackTelemetry | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_CHARGE_PACK, last_retrieved, last_error)
    self.planned = planned
    self.history = history
    self.status = status
    self.telemetry = telemetry

async def async_refresh_charge_pack_dispatches(
  current: datetime,
  client: OctopusEnergyApiClient,
  account_id: str,
  device_id: str,
  existing_result: ChargePackDispatchesCoordinatorResult,
  async_save_history = None
) -> ChargePackDispatchesCoordinatorResult:
  """The plan, read every REFRESH_RATE_IN_MINUTES_CHARGE_PACK minutes, and the
  history of the dispatches that started (saved when it changes)."""
  history = existing_result.history if existing_result is not None else []
  if existing_result is None or current >= existing_result.next_refresh:
    try:
      read = await client.async_get_charge_pack_dispatches(account_id, device_id)
      new_history = update_history(history, read.planned, current)
      if new_history != history and async_save_history is not None:
        await async_save_history(new_history)
      # (the status is kept if Octopus didn't send it this time)
      status = read.status if read.status is not None else (existing_result.status if existing_result is not None else None)
      telemetry = read.telemetry if read.telemetry is not None else (existing_result.telemetry if existing_result is not None else None)
      return ChargePackDispatchesCoordinatorResult(current, 1, read.planned, new_history, status=status, telemetry=telemetry)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise

      if existing_result is not None:
        result = ChargePackDispatchesCoordinatorResult(existing_result.last_evaluated, existing_result.request_attempts + 1,
                                                       existing_result.planned, history, existing_result.last_retrieved, last_error=e,
                                                       status=existing_result.status, telemetry=existing_result.telemetry)
        if result.request_attempts == 2:
          _LOGGER.warning(f'Failed to retrieve the charge pack dispatches for {device_id} - using cached data. See diagnostics sensor for more information.')
        return result

      _LOGGER.warning(f'Failed to retrieve the charge pack dispatches for {device_id}. See diagnostics sensor for more information.')
      return ChargePackDispatchesCoordinatorResult(
        # We want to force into our fallback mode
        current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_CHARGE_PACK),
        2,
        [],
        history,
        last_error=e
      )

  # Between reads: a planned dispatch that's started since joins the history
  new_history = update_history(history, existing_result.planned, current)
  if new_history != history:
    if async_save_history is not None:
      await async_save_history(new_history)
    existing_result.history = new_history
  return existing_result

async def async_setup_charge_pack_coordinator(hass, account_id: str, device_id: str):
  key = DATA_CHARGE_PACK_DISPATCHES.format(device_id)

  async def async_save_history(history):
    await async_save_cached_charge_pack_history(hass, device_id, history)

  async def async_update_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    hass.data[DOMAIN][account_id][key] = await async_refresh_charge_pack_dispatches(
      current,
      client,
      account_id,
      device_id,
      hass.data[DOMAIN][account_id][key] if key in hass.data[DOMAIN][account_id] else None,
      async_save_history
    )
    return hass.data[DOMAIN][account_id][key]

  hass.data[DOMAIN][account_id][DATA_CHARGE_PACK_COORDINATOR.format(device_id)] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"charge_pack_dispatches_{device_id}",
    update_method=async_update_data,
    # Updated every minute (so a dispatch that starts joins the history), but the
    # plan is only read every REFRESH_RATE_IN_MINUTES_CHARGE_PACK minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )
