import pytest

from .. import get_test_context
from custom_components.octopus_energy.api_client import AuthenticationException
from custom_components.octopus_energy.api_client_home_pro import OctopusEnergyHomeProApiClient

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

  assert "demand" in data[0]
  if is_electricity:
    assert data[0]["demand"] >= 0
  else:
    assert data[0]["demand"] is None

  assert "total_consumption" in data[0]
  assert data[0]["total_consumption"] is None or data[0]["total_consumption"] >= 0

  assert "start" in data[0]
  assert "end" in data[0]

  assert "is_kwh" in data[0]
  assert data[0]["is_kwh"] == True