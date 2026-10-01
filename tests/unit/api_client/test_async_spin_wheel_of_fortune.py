from datetime import timedelta
from unittest import mock
import pytest

from homeassistant.util.dt import now

from custom_components.octopus_energy.api_client import (
  OctopusEnergyApiClient,
  RequestException
)

read_response_target = "custom_components.octopus_energy.api_client.OctopusEnergyApiClient.__async_read_response__"
create_client_session_target = "custom_components.octopus_energy.api_client.OctopusEnergyApiClient._create_client_session"

class MockResponseContext:
  async def __aenter__(self):
    return mock.Mock()

  async def __aexit__(self, *args):
    return False

class MockClientSession:
  def __init__(self):
    self.requested_payload = None

  def post(self, *args, **kwargs):
    self.requested_payload = kwargs["json"]
    return MockResponseContext()

def create_client():
  client = OctopusEnergyApiClient("test-api-key")
  client._graphql_token = "test-token"
  client._graphql_expiration = now() + timedelta(hours=1)
  return client

@pytest.mark.asyncio
@pytest.mark.parametrize("is_electricity,expected_fuel_type", [
  (True, "ELECTRICITY"),
  (False, "GAS"),
])
async def test_when_prize_is_returned_then_prize_value_is_returned(is_electricity: bool, expected_fuel_type: str):
  # Arrange
  client = create_client()
  session = MockClientSession()
  response_body = { "data": { "spinWheelOfFortune": { "prize": { "value": 8 } } } }

  # Act
  with mock.patch(create_client_session_target, return_value=session):
    with mock.patch(read_response_target, return_value=response_body):
      result = await client.async_spin_wheel_of_fortune("ABC123", is_electricity)

  # Assert
  assert result == 8
  assert 'accountNumber: "ABC123"' in session.requested_payload["query"]
  assert f'fuelType: {expected_fuel_type}' in session.requested_payload["query"]

@pytest.mark.asyncio
@pytest.mark.parametrize("response_body", [
  None,
  {},
  { "data": None },
  { "data": {} },
  { "data": { "spinWheelOfFortune": None } },
  { "data": { "spinWheelOfFortune": {} } },
  { "data": { "spinWheelOfFortune": { "prize": None } } },
  { "data": { "spinWheelOfFortune": { "prize": {} } } },
  { "data": { "spinWheelOfFortune": { "prize": { "value": None } } } },
])
async def test_when_prize_is_not_returned_then_exception_is_raised(response_body):
  # Arrange
  client = create_client()

  # Act
  with mock.patch(create_client_session_target, return_value=MockClientSession()):
    with mock.patch(read_response_target, return_value=response_body):
      with pytest.raises(RequestException):
        await client.async_spin_wheel_of_fortune("ABC123", True)
