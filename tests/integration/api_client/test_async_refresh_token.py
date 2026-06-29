
import asyncio
from datetime import timedelta

import pytest

from homeassistant.util.dt import (utcnow)

from integration import get_test_context
from custom_components.octopus_energy.api_client import AuthenticationException, OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_token_is_expired_then_token_is_refreshed_raised():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id

    # Test that API key works as intended and that we can call multiple things at once
    account, octoplus = await asyncio.gather(client.async_get_account(account_id), client.async_get_octoplus_points())

    previous_token = client._graphql_token
    previous_refresh_token = client._graphql_refresh_token
    assert previous_token is not None
    assert previous_refresh_token is not None
    assert account is not None
    assert octoplus is not None

    # Make our api key invalid and test refreshing the token works
    client._graphql_expiration = utcnow() - timedelta(seconds=1)
    client._graphql_refresh_expiration = utcnow() - timedelta(seconds=1)

    new_account, new_octoplus = await asyncio.gather(client.async_get_account(account_id), client.async_get_octoplus_points())

    assert client._graphql_token is not None
    assert client._graphql_refresh_token is not None
    assert client._graphql_token != previous_token
    assert client._graphql_refresh_token != previous_refresh_token
    assert account == new_account
    assert octoplus == new_octoplus

@pytest.mark.asyncio
async def test_when_token_becomes_invalid_then_api_key_is_marked_as_invalid():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id

    account = await client.async_get_account(account_id)

    previous_token = client._graphql_token
    previous_refresh_token = client._graphql_refresh_token
    assert previous_token is not None
    assert previous_refresh_token is not None
    assert account is not None

    # Make our api key invalid and test refreshing the token works
    client._graphql_expiration = utcnow() - timedelta(seconds=1)
    client._graphql_refresh_expiration = utcnow() - timedelta(seconds=1)
    client._api_key = "invalid-api-key"

    exception_raised = False
    try:
        await client.async_get_account(account_id)
    except AuthenticationException as e:
        exception_raised = True

    assert client._is_api_key_invalid == True
    assert exception_raised == True

    exception_raised = False
    try:
        await client.async_get_account(account_id)
    except AuthenticationException as e:
        exception_raised = True
        assert e.args == ("API key has previously been marked as invalid - skipping refresh",)

    assert client._is_api_key_invalid == True
    assert exception_raised == True
