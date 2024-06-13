import pytest

from .. import get_test_context
from custom_components.octopus_energy.api_client import AuthenticationException
from custom_components.octopus_energy.api_client_home_pro import OctopusEnergyHomeProApiClient

@pytest.mark.asyncio
@pytest.mark.parametrize("is_electricity",[
    (True),
    (False)
])
async def test_when_get_consumption_is_called_and_api_key_is_invalid_then_exception_is_raised(is_electricity: bool):
  # Arrange
  context = get_test_context()
  
  client = OctopusEnergyHomeProApiClient(context.base_url, "invalid-api-key")

  # Act
  exception_raised = False
  try:
    await client.async_get_consumption(is_electricity)
  except AuthenticationException:
    exception_raised = True

  # Assert
  assert exception_raised == True

@pytest.mark.asyncio
@pytest.mark.parametrize("is_electricity",[
    (True),
    (False)
])
async def test_when_get_consumption_is_called_then_data_is_returned(is_electricity: bool):
  # Arrange
  context = get_test_context()
  
  client = OctopusEnergyHomeProApiClient(context.base_url, context.api_key)

  # Act
  data = await client.async_get_consumption(is_electricity)

  # Assert
  assert data is not None

  assert len(data) == 1

  assert "consumption" in data[0]
  assert data[0]["consumption"] >= 0

  assert "demand" in data[0]
  assert data[0]["demand"] >= 0

  assert "total_consumption" in data[0]
  assert data[0]["total_consumption"] >= 0