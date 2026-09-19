from datetime import timedelta
from unittest import mock
import pytest

from homeassistant.util.dt import now

from custom_components.octopus_energy.api_client import (
  AuthenticationException,
  OctopusEnergyApiClient,
  ServerException
)

fetch_token_target = "custom_components.octopus_energy.api_client.OctopusEnergyApiClient._OctopusEnergyApiClient__async_fetch_token"

def set_token_as_retrieved(client: OctopusEnergyApiClient):
  client._graphql_token = "test-token"
  client._graphql_expiration = now() + timedelta(hours=1)

@pytest.mark.asyncio
async def test_when_token_retrieval_fails_with_server_exception_then_cooldown_is_set():
  # Arrange
  client = OctopusEnergyApiClient("test-api-key")

  # Act
  with mock.patch(fetch_token_target, side_effect=ServerException("cloudfront")):
    with pytest.raises(ServerException):
      await client.async_refresh_token()

  # Assert
  assert client._token_retrieval_failures == 1
  assert client._token_retrieval_cooldown_until is not None
  assert client._token_retrieval_cooldown_until > now()

@pytest.mark.asyncio
async def test_when_cooldown_is_active_then_token_retrieval_is_not_attempted():
  # Arrange
  client = OctopusEnergyApiClient("test-api-key")

  with mock.patch(fetch_token_target, side_effect=ServerException("cloudfront")):
    with pytest.raises(ServerException):
      await client.async_refresh_token()

  # Act
  with mock.patch(fetch_token_target, side_effect=ServerException("cloudfront")) as mocked_fetch_token:
    with pytest.raises(ServerException):
      await client.async_refresh_token()

    # Assert
    assert mocked_fetch_token.call_count == 0

  # The failed attempt that was never made must not extend the cooldown
  assert client._token_retrieval_failures == 1

@pytest.mark.asyncio
async def test_when_cooldown_has_elapsed_then_token_retrieval_is_attempted():
  # Arrange
  client = OctopusEnergyApiClient("test-api-key")

  with mock.patch(fetch_token_target, side_effect=ServerException("cloudfront")):
    with pytest.raises(ServerException):
      await client.async_refresh_token()

  client._token_retrieval_cooldown_until = now() - timedelta(minutes=1)

  # Act
  with mock.patch(fetch_token_target, side_effect=ServerException("cloudfront")) as mocked_fetch_token:
    with pytest.raises(ServerException):
      await client.async_refresh_token()

    # Assert
    assert mocked_fetch_token.call_count == 1

  assert client._token_retrieval_failures == 2

@pytest.mark.asyncio
async def test_when_token_retrieval_succeeds_then_cooldown_is_cleared():
  # Arrange
  client = OctopusEnergyApiClient("test-api-key")

  with mock.patch(fetch_token_target, side_effect=ServerException("cloudfront")):
    with pytest.raises(ServerException):
      await client.async_refresh_token()

  client._token_retrieval_cooldown_until = now() - timedelta(minutes=1)

  # Act
  with mock.patch(fetch_token_target, side_effect=lambda: set_token_as_retrieved(client)):
    await client.async_refresh_token()

  # Assert
  assert client._token_retrieval_failures == 0
  assert client._token_retrieval_cooldown_until is None

@pytest.mark.asyncio
async def test_when_api_key_is_invalid_then_cooldown_is_not_involved():
  # Arrange
  client = OctopusEnergyApiClient("test-api-key")

  # Act
  with mock.patch(fetch_token_target, side_effect=AuthenticationException("invalid", [])):
    with pytest.raises(AuthenticationException):
      await client.async_refresh_token()

  # Assert
  assert client._is_api_key_invalid == True
  assert client._token_retrieval_failures == 0
  assert client._token_retrieval_cooldown_until is None
