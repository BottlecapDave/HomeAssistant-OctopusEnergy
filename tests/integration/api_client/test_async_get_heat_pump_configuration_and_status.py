import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import AuthenticationException, OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_async_get_heat_pump_configuration_and_status_is_called_then_authentication_exception_is_thrown():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id
    heat_pump_id = "00:00:00:00:00:00:00:00"

    # Act
    try:
        await client.async_get_heat_pump_configuration_and_status(account_id, heat_pump_id)
        assert True == False
    except AuthenticationException as e:
        assert True == True