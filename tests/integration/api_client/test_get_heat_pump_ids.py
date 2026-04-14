import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_heat_pump_ids_for_account_with_no_heat_pumps_is_called_then_empty_array_is_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id

    # Act
    account = await client.async_get_account(account_id)

    assert "property_ids" in account
    assert account["property_ids"] is not None
    assert len(account["property_ids"]) >= 0

    heat_pump_ids = await client.async_get_heat_pump_ids(account_id, account["property_ids"])
    # Assert
    assert heat_pump_ids is not None
    assert len(heat_pump_ids) == 0