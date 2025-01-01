import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_intelligent_dispatches_is_called_for_account_on_different_tariff_then_exception_is_raised():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id

    # Act
    exception_raised = False
    try:
        await client.async_get_intelligent_dispatches(account_id, "123")
    except:
        exception_raised = True

    # Assert
    assert exception_raised == True
  