import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_saving_sessions_is_called_then_events_are_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id

    # Act
    result = await client.async_get_saving_sessions(account_id)

    # Assert
    assert result is not None

    assert result.available_events is not None
    for event in result.available_events:
        assert event.id is not None
        assert event.code is not None
        assert event.start is not None
        assert event.end is not None
        assert event.octopoints >= 0
    
    assert result.joined_events is not None
    for event in result.joined_events:
        assert event.id is not None
        assert event.code is None
        assert event.start is not None
        assert event.end is not None
        assert event.octopoints is None or event.octopoints >= 0