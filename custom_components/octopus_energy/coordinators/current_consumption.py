from datetime import (datetime, timedelta)
import logging
from typing import Callable

from homeassistant.util.dt import (now)
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_CURRENT_CONSUMPTION_COORDINATOR_KEY,
  DATA_CURRENT_CONSUMPTION_KEY,
  DOMAIN,
  HOME_MINI_DATA_STALE_AFTER_MINUTES,
  REPAIR_HOME_MINI_DATA_STALE,
)

from ..api_client import (ApiException, OctopusEnergyApiClient)
from ..utils.repairs import safe_repair_key
from . import BaseCoordinatorResult

_LOGGER = logging.getLogger(__name__)
_LAST_RETRIEVED_UNSET = object()

class CurrentConsumptionCoordinatorResult(BaseCoordinatorResult):
  data: list

  def __init__(self, last_evaluated: datetime, request_attempts: int, refresh_rate_in_minutes: float, data: list, last_error: Exception | None = None, last_retrieved: datetime | None | object = _LAST_RETRIEVED_UNSET, latest_reading: datetime | None = None, first_missing_at: datetime | None = None, status: str = "fresh", last_good_data: list | None = None):
    actual_last_retrieved = last_evaluated if last_retrieved is _LAST_RETRIEVED_UNSET else last_retrieved
    super().__init__(last_evaluated, request_attempts, refresh_rate_in_minutes, actual_last_retrieved, last_error)
    # BaseCoordinatorResult uses last_evaluated as a default. For Home Mini data,
    # no timestamp is more truthful until a usable telemetry response arrives.
    self.last_retrieved = actual_last_retrieved
    self.data = data
    self.latest_reading = latest_reading
    self.first_missing_at = first_missing_at
    self.status = status
    self.last_good_data = last_good_data if last_good_data is not None else data

def _current_day_data(current_date: datetime, data: list | None) -> list:
  return [item for item in data or [] if item["start"].astimezone(current_date.tzinfo).date() == current_date.date()]

def _merge_consumption(previous_data: list, new_data: list) -> list:
  readings_by_start = {item["start"]: item for item in previous_data}
  for item in new_data:
    existing_item = readings_by_start.get(item["start"])
    if existing_item is None:
      readings_by_start[item["start"]] = item
      continue

    merged_item = dict(existing_item)
    for key, value in item.items():
      # Missing register/demand values in a partial response must not erase a
      # value retrieved earlier for the same interval. Consumption remains
      # numeric because the API intentionally maps a missing delta to zero.
      if value is not None:
        merged_item[key] = value
    readings_by_start[item["start"]] = merged_item
  return sorted(readings_by_start.values(), key=lambda item: item["start"])

def _is_stale(current_date: datetime, latest_reading: datetime | None, last_retrieved: datetime | None, first_missing_at: datetime | None) -> bool:
  freshness_reference = last_retrieved or latest_reading or first_missing_at
  return freshness_reference is not None and current_date >= freshness_reference + timedelta(minutes=HOME_MINI_DATA_STALE_AFTER_MINUTES)

def raise_home_mini_data_stale(hass, account_id: str, device_id: str, meter_details: str):
  ir.async_create_issue(
    hass,
    DOMAIN,
    safe_repair_key(REPAIR_HOME_MINI_DATA_STALE, device_id),
    is_fixable=False,
    is_persistent=False,
    severity=ir.IssueSeverity.ERROR,
    learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/home_mini_data_stale",
    translation_key="home_mini_data_stale",
    translation_placeholders={ "account_id": account_id, "meter_details": meter_details },
  )

def clear_home_mini_data_stale(hass, device_id: str):
  ir.async_delete_issue(hass, DOMAIN, safe_repair_key(REPAIR_HOME_MINI_DATA_STALE, device_id))

def clear_home_mini_data_stale_issues(hass, account_data: dict):
  coordinator_key_prefix = DATA_CURRENT_CONSUMPTION_COORDINATOR_KEY.format("")
  for runtime_key in account_data:
    if runtime_key.startswith(coordinator_key_prefix):
      clear_home_mini_data_stale(hass, runtime_key[len(coordinator_key_prefix):])

async def async_get_live_consumption(
  current_date: datetime,
  client: OctopusEnergyApiClient,
  device_id: str,
  previous_consumption: CurrentConsumptionCoordinatorResult | None,
  refresh_rate_in_minutes: float,
  raise_stale: Callable[[], None] = lambda: None,
  clear_stale: Callable[[], None] = lambda: None,
):
  if previous_consumption is None or current_date >= previous_consumption.next_refresh:
    period_from = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    period_to = period_from + timedelta(days=1)
    
    try:
      data = await client.async_get_smart_meter_consumption(device_id, period_from, period_to)
      if data is not None:
        _LOGGER.debug(f'Retrieved current consumption data for {device_id}; period_from: {period_from}; period_to: {period_to}; length: {len(data)}; last_from: {data[-1]["start"] if len(data) > 0 else None}')

        current_data = [item for item in data if period_from <= item["start"].astimezone(period_from.tzinfo) < period_to]
        previous_good_data = previous_consumption.last_good_data if previous_consumption is not None else []
        previous_data = _current_day_data(current_date, previous_good_data)
        merged_data = _merge_consumption(previous_data, current_data)
        changed = len(current_data) > 0 and merged_data != previous_data
        latest_reading = merged_data[-1]["start"] if len(merged_data) > 0 else None
        previous_last_retrieved = previous_consumption.last_retrieved if previous_consumption is not None else None
        newest_reading_is_recent = latest_reading is not None and current_date < latest_reading + timedelta(minutes=HOME_MINI_DATA_STALE_AFTER_MINUTES)
        last_retrieved = current_date if changed and newest_reading_is_recent else previous_last_retrieved
        first_missing_at = None if len(current_data) > 0 else (previous_consumption.first_missing_at or current_date if previous_consumption is not None else current_date)
        freshness_last_retrieved = last_retrieved if len(previous_data) > 0 or changed else None
        stale = _is_stale(current_date, latest_reading, freshness_last_retrieved, first_missing_at)
        if len(current_data) == 0 and previous_consumption is not None and previous_consumption.status == "stale":
          stale = True
        usable_data = [] if stale else merged_data
        last_good_data = merged_data if len(merged_data) > 0 else previous_good_data

        if stale:
          if previous_consumption is None or previous_consumption.status != "stale":
            _LOGGER.warning("Home Mini consumption data has stopped updating. See repairs for more information.")
          raise_stale()
        else:
          if previous_consumption is not None and previous_consumption.status == "stale":
            _LOGGER.info("Home Mini consumption data has started updating again.")
          clear_stale()

        return CurrentConsumptionCoordinatorResult(
          current_date,
          1,
          refresh_rate_in_minutes,
          usable_data,
          last_error=None,
          last_retrieved=last_retrieved,
          latest_reading=latest_reading,
          first_missing_at=first_missing_at,
          status="stale" if stale else ("empty" if len(current_data) == 0 else ("fresh" if changed else "unchanged")),
          last_good_data=last_good_data,
        )
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise

      result: CurrentConsumptionCoordinatorResult = None
      if previous_consumption is not None:
        current_day_last_good_data = _current_day_data(current_date, previous_consumption.last_good_data)
        result = CurrentConsumptionCoordinatorResult(
          previous_consumption.last_evaluated,
          previous_consumption.request_attempts + 1,
          refresh_rate_in_minutes,
          current_day_last_good_data,
          last_error=e,
          last_retrieved=previous_consumption.last_retrieved,
          latest_reading=previous_consumption.latest_reading if len(current_day_last_good_data) > 0 else None,
          first_missing_at=previous_consumption.first_missing_at or current_date,
          status="error",
          last_good_data=previous_consumption.last_good_data,
        )
        
        if (result.request_attempts == 2):
          _LOGGER.warning(f'Failed to retrieve smart meter consumption data - using cached version. See diagnostics sensor for more information.')
      else:
        result = CurrentConsumptionCoordinatorResult(
          current_date - timedelta(minutes=refresh_rate_in_minutes),
          2,
          refresh_rate_in_minutes,
          [],
          last_error=e,
          last_retrieved=None,
          latest_reading=None,
          first_missing_at=current_date,
          status="error",
          last_good_data=[],
        )
        _LOGGER.warning(f'Failed to retrieve smart meter consumption data. See diagnostics sensor for more information.')
      
      if _is_stale(current_date, result.latest_reading, result.last_retrieved if len(result.data) > 0 else None, result.first_missing_at):
        result.status = "stale"
        result.data = []
        if previous_consumption is None or previous_consumption.status != "stale":
          _LOGGER.warning("Home Mini consumption data has stopped updating. See repairs for more information.")
        raise_stale()

      return result
  
  return previous_consumption

async def async_create_current_consumption_coordinator(hass, account_id: str, client: OctopusEnergyApiClient, device_id: str, refresh_rate_in_minutes: float, meter_type: str, meter_point: str, serial_number: str):
  """Create current consumption coordinator"""
  key = DATA_CURRENT_CONSUMPTION_KEY.format(device_id)
  coordinator_key = DATA_CURRENT_CONSUMPTION_COORDINATOR_KEY.format(device_id)
  meter_details = f"{meter_type} ({meter_point}/{serial_number})"

  if coordinator_key in hass.data[DOMAIN][account_id]:
    existing_coordinator = hass.data[DOMAIN][account_id][coordinator_key]
    existing_coordinator.home_mini_refresh_rate_in_minutes = min(existing_coordinator.home_mini_refresh_rate_in_minutes, refresh_rate_in_minutes)
    existing_coordinator.home_mini_meter_details.add(meter_details)
    return existing_coordinator

  hass.data[DOMAIN][account_id][key] = None

  async def async_update_data():
    """Fetch data from API endpoint."""
    current: datetime = now()
    previous_consumption = hass.data[DOMAIN][account_id][key] if key in hass.data[DOMAIN][account_id] else None
    effective_refresh_rate = coordinator.home_mini_refresh_rate_in_minutes
    hass.data[DOMAIN][account_id][key] = await async_get_live_consumption(
      current,
      client,
      device_id,
      previous_consumption,
      effective_refresh_rate,
      lambda: raise_home_mini_data_stale(hass, account_id, device_id, ", ".join(sorted(coordinator.home_mini_meter_details))),
      lambda: clear_home_mini_data_stale(hass, device_id),
    )
    
    return hass.data[DOMAIN][account_id][key]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"current_consumption_{device_id}",
    update_method=async_update_data,
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )
  coordinator.home_mini_refresh_rate_in_minutes = refresh_rate_in_minutes
  coordinator.home_mini_meter_details = {meter_details}

  hass.data[DOMAIN][account_id][coordinator_key] = coordinator
  return coordinator
