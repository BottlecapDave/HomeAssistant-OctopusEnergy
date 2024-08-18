import pytest

from .. import get_test_context
from custom_components.octopus_energy.api_client import AuthenticationException
from custom_components.octopus_energy.api_client_home_pro import OctopusEnergyHomeProApiClient

@pytest.mark.asyncio
async def test_when_ping_is_called_and_api_key_is_invalid_then_exception_is_raised():
  # Arrange
  context = get_test_context()
  
  client = OctopusEnergyHomeProApiClient(context.base_url, "invalid-api-key")

  # Act
  exception_raised = False
  try:
    await client.async_ping()
  except AuthenticationException:
    exception_raised = True

  # Assert
  assert exception_raised == True

@pytest.mark.asyncio
async def test_when_ping_is_called_then_data_is_returned():
  # Arrange
  context = get_test_context()
  
  client = OctopusEnergyHomeProApiClient(context.base_url, context.api_key)

  # Act
  result = await client.async_ping()

  # Assert
  assert result == True