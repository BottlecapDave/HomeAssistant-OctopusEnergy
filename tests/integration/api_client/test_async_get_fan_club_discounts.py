import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_async_get_fan_club_discounts_is_called_with_account_with_no_fan_club_then_empty_array_is_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)

    # Act
    result = await client.async_get_fan_club_discounts(context.account_id)

    # Assert
    assert result is not None
    assert result.fanClubStatus is not None
    assert len(result.fanClubStatus) == 0