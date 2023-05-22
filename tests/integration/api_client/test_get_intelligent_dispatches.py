import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_intelligent_dispatches_is_called_for_account_on_different_tariff_then_results_are_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"])
    account_id = context["account_id"]

    # Act
    dispatches = await client.async_get_intelligent_dispatches(account_id)

    # Assert
    assert dispatches is not None
    assert "complete" in dispatches
    assert "planned" in dispatches
  