from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.api_client.wheel_of_fortune import (
  build_wheel_of_fortune_query,
  map_wheel_of_fortune_spins_response,
)


@pytest.mark.parametrize(
  "include_electricity,include_gas,contains_electricity,contains_gas",
  [
    (True, True, True, True),
    (True, False, True, False),
    (False, True, False, True),
  ],
)
def test_build_wheel_of_fortune_query_only_includes_monitored_supplies(
  include_electricity,
  include_gas,
  contains_electricity,
  contains_gas,
):
  query = build_wheel_of_fortune_query("A-123", include_electricity, include_gas)

  assert ("fuelType:ELECTRICITY" in query) == contains_electricity
  assert ("fuelType:GAS" in query) == contains_gas
  assert 'accountNumber: "A-123"' in query


def test_build_wheel_of_fortune_query_rejects_no_supplies():
  with pytest.raises(ValueError, match="At least one supply"):
    build_wheel_of_fortune_query("A-123", False, False)


@pytest.mark.parametrize(
  "response_body,include_electricity,include_gas,expected_electricity,expected_gas",
  [
    ({"data": {"electricity": {"spinsAllowed": 1}, "gas": {"spinsAllowed": 2}}}, True, True, 1, 2),
    ({"data": {"electricity": {"spinsAllowed": 1}}}, True, False, 1, None),
    ({"data": {"gas": {"spinsAllowed": 2}}}, False, True, None, 2),
  ],
)
def test_map_wheel_of_fortune_spins_response_allows_excluded_supply_to_be_absent(
  response_body,
  include_electricity,
  include_gas,
  expected_electricity,
  expected_gas,
):
  result = map_wheel_of_fortune_spins_response(response_body, include_electricity, include_gas)

  assert result is not None
  assert result.electricity == expected_electricity
  assert result.gas == expected_gas


def test_map_wheel_of_fortune_spins_response_rejects_missing_monitored_supply():
  assert map_wheel_of_fortune_spins_response(
    {"data": {"electricity": {"spinsAllowed": 1}}},
    True,
    True,
  ) is None


@pytest.mark.asyncio
async def test_async_get_wheel_of_fortune_spins_sends_and_accepts_single_supply_query():
  response = MagicMock()
  response_context = MagicMock()
  response_context.__aenter__ = AsyncMock(return_value=response)
  response_context.__aexit__ = AsyncMock(return_value=None)
  session = MagicMock()
  session.post.return_value = response_context

  client = OctopusEnergyApiClient("test-api-key")
  client.async_refresh_token = AsyncMock()
  client._create_client_session = AsyncMock(return_value=session)
  client.__async_read_response__ = AsyncMock(return_value={
    "data": {"electricity": {"spinsAllowed": 3}}
  })

  result = await client.async_get_wheel_of_fortune_spins(
    "A-123",
    include_electricity=True,
    include_gas=False,
  )

  payload = session.post.call_args.kwargs["json"]
  assert "fuelType:ELECTRICITY" in payload["query"]
  assert "fuelType:GAS" not in payload["query"]
  assert result.electricity == 3
  assert result.gas is None
