import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.octopus_energy.api_client import (
  OctopusEnergyApiClient,
  RequestException,
  TimeoutException,
  integration_context_header,
  octoplus_scratchcard_query,
)
from custom_components.octopus_energy.api_client.scratchcard import (
  OctoplusScratchcard,
  OctoplusScratchcardOffer,
  OctoplusScratchcardPrize,
  OctoplusScratchcardResponse,
  OctoplusScratchcardSession,
)
from custom_components.octopus_energy.octoplus import is_scratchcard_available


def test_scratchcard_response_uses_base_model_serialization():
  payload = {
    "activeSession": {
      "startsAt": "2026-09-27T23:00:00Z",
      "endsAt": "2026-09-28T23:00:00Z",
      "externalReference": "session-reference",
    },
    "scratchcard": {
      "externalReference": "scratchcard-reference",
      "status": "PRIZE_CLAIMED",
      "offer": {"slug": "coffee", "featureDisplayText": "A free coffee"},
      "prize": {"__typename": "OctoplusOfferType"},
    },
  }
  data = OctoplusScratchcardResponse.model_validate(payload)
  assert isinstance(data.activeSession, OctoplusScratchcardSession)
  assert isinstance(data.scratchcard, OctoplusScratchcard)
  assert isinstance(data.scratchcard.offer, OctoplusScratchcardOffer)
  assert isinstance(data.scratchcard.prize, OctoplusScratchcardPrize)
  assert data.model_dump(mode="json", by_alias=True) == {
    **payload,
    "has_active_session": True,
    "has_scratchcard": True,
  }


@pytest.mark.asyncio
@pytest.mark.parametrize("active_session,scratchcard,expected", [
  (None, None, False),
  ({"externalReference": "session-reference"}, None, True),
  ({"externalReference": "session-reference"}, {"status": "DID_NOT_WIN"}, False),
])
async def test_authenticated_scratchcard_query(active_session, scratchcard, expected):
  client = OctopusEnergyApiClient("test-api-key")
  client._graphql_token = "test-token"
  response = Mock(status=200)
  response.request_info.headers = {integration_context_header: "octoplus-scratchcard"}
  response.text = AsyncMock(return_value=json.dumps({
    "data": {"octoplusActiveScratchcardData": {
      "activeSession": active_session,
      "scratchcard": scratchcard,
    }},
  }))
  session = Mock()
  session.post.return_value.__aenter__ = AsyncMock(return_value=response)
  session.post.return_value.__aexit__ = AsyncMock(return_value=False)
  with patch.object(client, "async_refresh_token", AsyncMock()) as refresh_token:
    with patch.object(client, "_create_client_session", AsyncMock(return_value=session)):
      result = await client.async_get_octoplus_scratchcard("A-12345678")

  refresh_token.assert_awaited_once()
  session.post.assert_called_once_with(
    "https://api.backend.octopus.energy/v1/graphql/",
    json={
      "query": octoplus_scratchcard_query,
      "variables": {"accountNumber": "A-12345678"},
    },
    headers={"Authorization": "test-token", integration_context_header: "octoplus-scratchcard"},
  )
  assert is_scratchcard_available(result) is expected


@pytest.mark.asyncio
@pytest.mark.parametrize("body", [
  None,
  {},
  {"data": None},
  {"data": {}},
  {"data": {"octoplusActiveScratchcardData": None}},
  {"data": {"octoplusActiveScratchcardData": {"activeSession": {}}}},
  {"data": {"octoplusActiveScratchcardData": {"scratchcard": None}}},
])
async def test_incomplete_response_is_not_treated_as_available(body):
  client = OctopusEnergyApiClient("test-api-key")
  session = Mock()
  session.post.return_value.__aenter__ = AsyncMock()
  session.post.return_value.__aexit__ = AsyncMock(return_value=False)
  with patch.object(client, "async_refresh_token", AsyncMock()):
    with patch.object(client, "_create_client_session", AsyncMock(return_value=session)):
      with patch.object(client, "__async_read_response__", AsyncMock(return_value=body)):
        with pytest.raises(RequestException):
          await client.async_get_octoplus_scratchcard("A-12345678")


@pytest.mark.asyncio
async def test_graphql_errors_are_raised():
  client = OctopusEnergyApiClient("test-api-key")
  response = Mock(status=200)
  response.request_info.headers = {}
  response.text = AsyncMock(return_value=json.dumps({"errors": [{"message": "Scratchcard unavailable"}]}))
  session = Mock()
  session.post.return_value.__aenter__ = AsyncMock(return_value=response)
  session.post.return_value.__aexit__ = AsyncMock(return_value=False)
  with patch.object(client, "async_refresh_token", AsyncMock()):
    with patch.object(client, "_create_client_session", AsyncMock(return_value=session)):
      with pytest.raises(RequestException):
        await client.async_get_octoplus_scratchcard("A-12345678")


@pytest.mark.asyncio
async def test_timeout_is_translated_to_api_exception():
  client = OctopusEnergyApiClient("test-api-key")
  with patch.object(client, "async_refresh_token", AsyncMock()):
    with patch.object(client, "_create_client_session", AsyncMock(side_effect=TimeoutError)):
      with pytest.raises(TimeoutException):
        await client.async_get_octoplus_scratchcard("A-12345678")
