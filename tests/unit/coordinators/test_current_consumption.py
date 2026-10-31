from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from unittest import mock

import pytest

from custom_components.octopus_energy.api_client import ApiException
from custom_components.octopus_energy.const import DOMAIN
from custom_components.octopus_energy.coordinators.current_consumption import (
  CurrentConsumptionCoordinatorResult,
  async_create_current_consumption_coordinator,
  async_get_live_consumption,
  clear_home_mini_data_stale_issues,
)

LONDON = ZoneInfo("Europe/London")
DEVICE_ID = "device-1"

def reading(start: datetime, consumption: float = 0.1, demand: float = 200):
  return {
    "start": start,
    "end": start + timedelta(minutes=30),
    "consumption": consumption,
    "demand": demand,
    "total_consumption": 12.3,
    "total_export": 0,
  }

class Client:
  def __init__(self, responses):
    self.responses = list(responses)
    self.requests = []

  async def async_get_smart_meter_consumption(self, device_id, period_from, period_to):
    self.requests.append((device_id, period_from, period_to))
    response = self.responses.pop(0)
    if isinstance(response, Exception):
      raise response
    return response

@pytest.mark.asyncio
async def test_initial_empty_response_initialises_retry_and_diagnostics():
  current = datetime(2026, 8, 29, 10, 5, tzinfo=LONDON)

  result = await async_get_live_consumption(current, Client([[]]), DEVICE_ID, None, 1)

  assert result is not None
  assert result.data == []
  assert result.last_retrieved is None
  assert result.request_attempts == 1
  assert result.next_refresh == datetime(2026, 8, 29, 10, 6, tzinfo=LONDON)
  assert result.first_missing_at == current
  assert result.status == "empty"
  assert result.last_error is None

@pytest.mark.asyncio
async def test_repeated_empty_responses_keep_the_configured_refresh_rate():
  current = datetime(2026, 8, 29, 10, 5, tzinfo=LONDON)
  client = Client([[], [], []])

  first = await async_get_live_consumption(current, client, DEVICE_ID, None, 1)
  second = await async_get_live_consumption(first.next_refresh, client, DEVICE_ID, first, 1)
  third = await async_get_live_consumption(second.next_refresh, client, DEVICE_ID, second, 1)

  assert first.next_refresh == datetime(2026, 8, 29, 10, 6, tzinfo=LONDON)
  assert second.next_refresh == datetime(2026, 8, 29, 10, 7, tzinfo=LONDON)
  assert third.next_refresh == datetime(2026, 8, 29, 10, 8, tzinfo=LONDON)

@pytest.mark.asyncio
async def test_empty_response_preserves_same_day_data_without_claiming_it_is_fresh():
  current = datetime(2026, 8, 29, 10, 5, tzinfo=LONDON)
  previous_data = [reading(datetime(2026, 8, 29, 10, 0, tzinfo=LONDON), 0)]
  previous = CurrentConsumptionCoordinatorResult(
    current - timedelta(minutes=1), 1, 1, previous_data,
    last_retrieved=current - timedelta(minutes=1),
    latest_reading=previous_data[-1]["start"],
  )

  result = await async_get_live_consumption(current, Client([[]]), DEVICE_ID, previous, 1)

  assert result.data == previous_data
  assert result.last_retrieved == previous.last_retrieved
  assert result.latest_reading == previous.latest_reading
  assert result.request_attempts == 1
  assert result.status == "empty"

@pytest.mark.asyncio
async def test_empty_response_does_not_carry_yesterdays_data_into_today():
  current = datetime(2026, 8, 30, 0, 5, tzinfo=LONDON)
  previous_data = [reading(datetime(2026, 8, 29, 23, 30, tzinfo=LONDON))]
  previous = CurrentConsumptionCoordinatorResult(
    current - timedelta(minutes=10), 1, 1, previous_data,
    last_retrieved=current - timedelta(minutes=10),
    latest_reading=previous_data[-1]["start"],
  )

  result = await async_get_live_consumption(current, Client([[]]), DEVICE_ID, previous, 1)

  assert result.data == []
  assert result.last_retrieved == previous.last_retrieved
  assert result.status == "empty"

@pytest.mark.asyncio
async def test_midnight_empty_response_does_not_clear_existing_stale_repair():
  stale_calls = 0
  clear_calls = 0

  def raise_stale():
    nonlocal stale_calls
    stale_calls += 1

  def clear_stale():
    nonlocal clear_calls
    clear_calls += 1

  current = datetime(2026, 8, 30, 0, 1, tzinfo=LONDON)
  previous_data = [reading(datetime(2026, 8, 29, 23, 0, tzinfo=LONDON))]
  previous = CurrentConsumptionCoordinatorResult(
    current - timedelta(minutes=2), 1, 1, [],
    last_retrieved=current - timedelta(minutes=32),
    latest_reading=previous_data[-1]["start"],
    status="stale",
    last_good_data=previous_data,
  )

  still_stale = await async_get_live_consumption(current, Client([[]]), DEVICE_ID, previous, 1, raise_stale, clear_stale)

  assert still_stale.status == "stale"
  assert still_stale.data == []
  assert stale_calls == 1
  assert clear_calls == 0

  recovered_data = [reading(datetime(2026, 8, 30, 0, 0, tzinfo=LONDON))]
  recovered = await async_get_live_consumption(current + timedelta(minutes=1), Client([recovered_data]), DEVICE_ID, still_stale, 1, raise_stale, clear_stale)

  assert recovered.status == "fresh"
  assert recovered.data == recovered_data
  assert clear_calls == 1

@pytest.mark.asyncio
async def test_unchanged_response_does_not_advance_last_retrieved():
  current = datetime(2026, 8, 29, 10, 5, tzinfo=LONDON)
  data = [reading(datetime(2026, 8, 29, 10, 0, tzinfo=LONDON), 0)]
  previous = CurrentConsumptionCoordinatorResult(
    current - timedelta(minutes=1), 1, 1, data,
    last_retrieved=current - timedelta(minutes=1),
    latest_reading=data[-1]["start"],
  )

  result = await async_get_live_consumption(current, Client([data]), DEVICE_ID, previous, 1)

  assert result.last_retrieved == previous.last_retrieved
  assert result.status == "unchanged"
  assert result.request_attempts == 1

@pytest.mark.asyncio
async def test_changed_values_at_same_timestamp_are_fresh_data():
  current = datetime(2026, 8, 29, 10, 5, tzinfo=LONDON)
  old_data = [reading(datetime(2026, 8, 29, 10, 0, tzinfo=LONDON), 0, 0)]
  new_data = [reading(datetime(2026, 8, 29, 10, 0, tzinfo=LONDON), 0, -250)]
  previous = CurrentConsumptionCoordinatorResult(
    current - timedelta(minutes=1), 1, 1, old_data,
    last_retrieved=current - timedelta(minutes=1),
    latest_reading=old_data[-1]["start"],
  )

  result = await async_get_live_consumption(current, Client([new_data]), DEVICE_ID, previous, 1)

  assert result.data == new_data
  assert result.last_retrieved == current
  assert result.status == "fresh"

@pytest.mark.asyncio
async def test_partial_response_is_merged_with_same_day_data():
  current = datetime(2026, 8, 29, 10, 35, tzinfo=LONDON)
  first = reading(datetime(2026, 8, 29, 10, 0, tzinfo=LONDON), 0.1)
  previous_second = reading(datetime(2026, 8, 29, 10, 30, tzinfo=LONDON), 0.2, 100)
  updated_second = reading(datetime(2026, 8, 29, 10, 30, tzinfo=LONDON), 0.25, 150)
  previous = CurrentConsumptionCoordinatorResult(
    current - timedelta(minutes=1), 1, 1, [first, previous_second],
    last_retrieved=current - timedelta(minutes=1),
    latest_reading=previous_second["start"],
  )

  result = await async_get_live_consumption(current, Client([[updated_second]]), DEVICE_ID, previous, 1)

  assert result.data == [first, updated_second]
  assert result.last_good_data == [first, updated_second]
  assert result.last_retrieved == current

@pytest.mark.asyncio
async def test_partial_interval_update_preserves_existing_register_values():
  current = datetime(2026, 8, 29, 10, 5, tzinfo=LONDON)
  existing = reading(datetime(2026, 8, 29, 10, 0, tzinfo=LONDON), 0.1, 100)
  existing["total_consumption"] = 12.3
  existing["total_export"] = 5
  partial_update = reading(existing["start"], 0.2, 250)
  partial_update["total_consumption"] = None
  partial_update["total_export"] = None
  previous = CurrentConsumptionCoordinatorResult(
    current - timedelta(minutes=1), 1, 1, [existing],
    last_retrieved=current - timedelta(minutes=1),
    latest_reading=existing["start"],
  )

  result = await async_get_live_consumption(current, Client([[partial_update]]), DEVICE_ID, previous, 1)

  assert result.data[0]["consumption"] == 0.2
  assert result.data[0]["demand"] == 250
  assert result.data[0]["total_consumption"] == 12.3
  assert result.data[0]["total_export"] == 5

@pytest.mark.asyncio
async def test_out_of_period_reading_is_treated_as_empty():
  current = datetime(2026, 8, 29, 10, 5, tzinfo=LONDON)
  future = reading(datetime(2026, 8, 30, 0, 0, tzinfo=LONDON))

  result = await async_get_live_consumption(current, Client([[future]]), DEVICE_ID, None, 1)

  assert result.data == []
  assert result.latest_reading is None
  assert result.status == "empty"

@pytest.mark.asyncio
async def test_empty_data_becomes_stale_at_thirty_minutes_and_recovers_normally():
  stale_calls = 0

  def raise_stale():
    nonlocal stale_calls
    stale_calls += 1

  started = datetime(2026, 8, 29, 10, 0, tzinfo=LONDON)
  first = await async_get_live_consumption(started, Client([[]]), DEVICE_ID, None, 1, raise_stale)
  before_threshold = await async_get_live_consumption(started + timedelta(minutes=29), Client([[]]), DEVICE_ID, first, 1, raise_stale)
  at_threshold = await async_get_live_consumption(started + timedelta(minutes=30), Client([[]]), DEVICE_ID, before_threshold, 1, raise_stale)

  assert before_threshold.status == "empty"
  assert at_threshold.status == "stale"
  assert at_threshold.data == []
  assert stale_calls == 1

@pytest.mark.asyncio
async def test_stale_repair_is_raised_once_and_cleared_on_recovery():
  stale_calls = 0
  clear_calls = 0

  def raise_stale():
    nonlocal stale_calls
    stale_calls += 1

  def clear_stale():
    nonlocal clear_calls
    clear_calls += 1

  current = datetime(2026, 8, 29, 11, 0, tzinfo=LONDON)
  stale_data = [reading(datetime(2026, 8, 29, 10, 0, tzinfo=LONDON), 0)]
  previous = CurrentConsumptionCoordinatorResult(
    current - timedelta(minutes=1), 1, 1, stale_data,
    last_retrieved=current - timedelta(minutes=30),
    latest_reading=stale_data[-1]["start"],
  )

  stale = await async_get_live_consumption(current, Client([stale_data]), DEVICE_ID, previous, 1, raise_stale, clear_stale)

  assert stale.status == "stale"
  assert stale.data == []
  assert stale.last_good_data == stale_data
  assert stale.last_retrieved == previous.last_retrieved
  assert stale_calls == 1
  assert clear_calls == 0

  recovered_data = [reading(datetime(2026, 8, 29, 11, 0, tzinfo=LONDON), 0, -100)]
  recovered = await async_get_live_consumption(current + timedelta(minutes=1), Client([recovered_data]), DEVICE_ID, stale, 1, raise_stale, clear_stale)

  assert recovered.status == "fresh"
  assert recovered.last_retrieved == current + timedelta(minutes=1)
  assert stale_calls == 1
  assert clear_calls == 1

@pytest.mark.asyncio
async def test_api_error_preserves_cached_data_and_uses_retry_backoff():
  current = datetime(2026, 8, 29, 10, 5, tzinfo=LONDON)
  data = [reading(datetime(2026, 8, 29, 10, 0, tzinfo=LONDON))]
  previous = CurrentConsumptionCoordinatorResult(
    current - timedelta(minutes=1), 1, 1, data,
    last_retrieved=current - timedelta(minutes=1),
    latest_reading=data[-1]["start"],
  )

  result = await async_get_live_consumption(current, Client([ApiException("nope")]), DEVICE_ID, previous, 1)

  assert result.data == data
  assert result.last_retrieved == previous.last_retrieved
  assert result.request_attempts == 2
  assert result.next_refresh == datetime(2026, 8, 29, 10, 6, tzinfo=LONDON)
  assert result.status == "error"

@pytest.mark.asyncio
@pytest.mark.parametrize(
  ("current", "expected_duration"),
  [
    (datetime(2026, 3, 29, 12, tzinfo=LONDON), timedelta(hours=23)),
    (datetime(2026, 10, 25, 12, tzinfo=LONDON), timedelta(hours=25)),
  ],
)
async def test_query_uses_local_day_across_dst(current, expected_duration):
  client = Client([[]])

  await async_get_live_consumption(current, client, DEVICE_ID, None, 1)

  _, period_from, period_to = client.requests[0]
  assert period_from.hour == 0
  assert period_to.hour == 0
  assert period_to.astimezone(ZoneInfo("UTC")) - period_from.astimezone(ZoneInfo("UTC")) == expected_duration

@pytest.mark.asyncio
async def test_factory_reuses_coordinator_for_same_device():
  class Hass:
    data = {DOMAIN: {"A-1": {}}}

  hass = Hass()
  client = Client([[]])

  coordinator = mock.MagicMock()
  with mock.patch("custom_components.octopus_energy.coordinators.current_consumption.DataUpdateCoordinator", return_value=coordinator):
    first = await async_create_current_consumption_coordinator(hass, "A-1", client, DEVICE_ID, 5, "electricity", "123", "ABC")
    hass.data[DOMAIN]["A-1"]["CURRENT_CONSUMPTION_device-1"] = "preserved"
    second = await async_create_current_consumption_coordinator(hass, "A-1", client, DEVICE_ID, 1, "gas", "456", "DEF")

  assert first is second
  assert hass.data[DOMAIN]["A-1"]["CURRENT_CONSUMPTION_device-1"] == "preserved"
  assert first.home_mini_refresh_rate_in_minutes == 1
  assert first.home_mini_meter_details == {"electricity (123/ABC)", "gas (456/DEF)"}

def test_account_unload_clears_each_home_mini_repair():
  hass = object()
  account_data = {
    "CURRENT_CONSUMPTION_COORDINATOR_device-1": object(),
    "CURRENT_CONSUMPTION_COORDINATOR_device-2": object(),
    "OTHER": object(),
  }

  with mock.patch("custom_components.octopus_energy.coordinators.current_consumption.clear_home_mini_data_stale") as clear_issue:
    clear_home_mini_data_stale_issues(hass, account_data)

  assert clear_issue.call_args_list == [mock.call(hass, "device-1"), mock.call(hass, "device-2")]
