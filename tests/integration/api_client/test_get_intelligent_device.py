import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_intelligent_device_is_called_for_account_with_no_devices_then_none_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id

    # Act
    result = await client.async_get_intelligent_devices(account_id)

    # Assert
    assert result is not None
    assert len(result) == 0
  