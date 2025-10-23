import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
@pytest.mark.xfail(reason="Service seems to be down sometimes.")
async def test_when_check_headers_is_called_then_True_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)

    # Act
    result = await client.async_check_headers()

    # Assert
    assert result == True