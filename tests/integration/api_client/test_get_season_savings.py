from datetime import datetime, timedelta
import os
import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_season_savings_is_called_then_events_are_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"])
    account_id = context["account_id"]

    # Act
    events = await client.async_get_season_savings(account_id)

    # Assert
    assert events != None
    for event in events:
        assert "start" in event
        assert "end" in event