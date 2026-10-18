from unittest.mock import AsyncMock

import pytest
from homeassistant.util.dt import now

from custom_components.octopus_energy.api_client import RequestException
from custom_components.octopus_energy.api_client.octoplus import OctoplusScratchcardResponse
from custom_components.octopus_energy.coordinators.octoplus_scratchcard import (
  OctoplusScratchcardCoordinatorResult,
  async_refresh_octoplus_scratchcard,
)


@pytest.mark.asyncio
async def test_refresh_returns_data_and_waits_until_next_refresh():
  current = now()
  data = OctoplusScratchcardResponse.model_validate({
    "activeSession": {},
    "scratchcard": None,
  })
  client = AsyncMock()
  client.async_get_octoplus_scratchcard.return_value = data

  result = await async_refresh_octoplus_scratchcard(current, client, "A-12345678", None)
  assert result.data is data
  assert result.request_attempts == 1
  assert result.next_refresh > current
  client.async_get_octoplus_scratchcard.assert_awaited_once_with("A-12345678")

  cached_result = await async_refresh_octoplus_scratchcard(current, client, "A-12345678", result)
  assert cached_result is result
  assert client.async_get_octoplus_scratchcard.await_count == 1

  new_data = OctoplusScratchcardResponse.model_validate({
    "activeSession": None,
    "scratchcard": None,
  })
  client.async_get_octoplus_scratchcard.return_value = new_data
  refreshed_result = await async_refresh_octoplus_scratchcard(result.next_refresh, client, "A-12345678", result)
  assert refreshed_result.data is new_data
  assert client.async_get_octoplus_scratchcard.await_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("has_cached_data", [True, False])
async def test_api_failure_preserves_cached_data_and_schedules_retry(has_cached_data):
  current = now()
  data = OctoplusScratchcardResponse.model_validate({
    "activeSession": {},
    "scratchcard": None,
  })
  existing = OctoplusScratchcardCoordinatorResult(current, 1, data) if has_cached_data else None
  error = RequestException("Unavailable", [])
  client = AsyncMock()
  client.async_get_octoplus_scratchcard.side_effect = error
  refresh_time = existing.next_refresh if existing is not None else current

  result = await async_refresh_octoplus_scratchcard(refresh_time, client, "A-12345678", existing)
  assert result.data is (data if has_cached_data else None)
  assert result.request_attempts == 2
  assert result.last_error is error
  assert result.next_refresh > refresh_time

  client.async_get_octoplus_scratchcard.side_effect = None
  client.async_get_octoplus_scratchcard.return_value = data
  recovered = await async_refresh_octoplus_scratchcard(result.next_refresh, client, "A-12345678", result)
  assert recovered.data is data
  assert recovered.request_attempts == 1
  assert recovered.last_error is None
