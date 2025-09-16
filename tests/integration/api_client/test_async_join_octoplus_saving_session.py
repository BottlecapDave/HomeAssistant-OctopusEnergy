import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_join_octoplus_saving_session_is_called_with_invalid_event_then_errors_are_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id
    event_code = "not-an-event-code"

    # Act
    result = await client.async_join_octoplus_saving_session(account_id, event_code)

    # Assert
    assert result is not None
    assert result.is_successful == False
    assert len(result.errors) == 1
    assert result.errors[0] == "Saving Sessions event not found"