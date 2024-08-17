import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_wheel_of_fortune_spins_called_then_spins_are_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id

    # Act
    result = await client.async_get_wheel_of_fortune_spins(account_id)

    # Assert
    assert result is not None

    assert result.electricity >= 0
    assert result.gas >= 0