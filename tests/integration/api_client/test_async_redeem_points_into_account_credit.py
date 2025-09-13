import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_redeem_octoplus_points_into_account_credit_is_called_with_invalid_points_then_errors_are_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id
    points = -1

    # Act
    result = await client.async_redeem_octoplus_points_into_account_credit(account_id, points)

    # Assert
    assert result is not None
    assert result.is_successful == False
    assert len(result.errors) == 1
    assert result.errors[0] == "Negative or zero points set"
