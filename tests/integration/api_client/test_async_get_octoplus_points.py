import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_octoplus_points_is_called_then_points_are_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)

    # Act
    points = await client.async_get_octoplus_points()

    # Assert
    assert points >= 0