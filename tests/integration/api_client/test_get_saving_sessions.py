import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_saving_sessions_is_called_then_events_are_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"])
    account_id = context["account_id"]

    # Act
    savings = await client.async_get_saving_sessions(account_id)

    # Assert
    assert savings is not None
    
    assert "events" in savings
    for event in savings["events"]:
        assert "start" in event
        assert "end" in event

    assert "points" in savings
    assert savings["points"] >= 0