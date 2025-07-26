import pytest

from .. import get_test_context
from custom_components.octopus_energy.api_client_home_pro import OctopusEnergyHomeProApiClient

@pytest.mark.asyncio
async def test_when_ping_is_called_then_true_is_returned():
  # Arrange
  context = get_test_context()
  
  client = OctopusEnergyHomeProApiClient(context.base_url, context.api_key)

  # Act
  result = await client.async_ping()

  # Assert
  assert result == True

@pytest.mark.asyncio
async def test_when_ping_is_called_when_invalid_address_provided_then_false_is_returned():
  # Arrange
  context = get_test_context()
  
  client = OctopusEnergyHomeProApiClient("http://10.0.0.1", context.api_key)

  # Act
  result = await client.async_ping()

  # Assert
  assert result == False