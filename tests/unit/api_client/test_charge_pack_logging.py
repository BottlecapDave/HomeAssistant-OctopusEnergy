from datetime import timedelta
import logging
from unittest import mock
import pytest

from homeassistant.util.dt import now

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException

read_response_target = "custom_components.octopus_energy.api_client.OctopusEnergyApiClient.__async_read_response__"
create_client_session_target = "custom_components.octopus_energy.api_client.OctopusEnergyApiClient._create_client_session"

account_id = "A-1A2B3C4D"
device_id = "00000000-0011-4000-8020-0000DEADBEEF"
device_name = "My Secret Battery"

# Values that only appear in the response bodies, so they mustn't reach the logs
private_values = [device_id, device_name, "73.25", "4.125", "2026-10-14T11:00:00+00:00", "-6.875"]

class MockResponseContext:
  async def __aenter__(self):
    response = mock.Mock()
    response.status = 200
    return response

  async def __aexit__(self, *args):
    return False

class MockClientSession:
  def post(self, *args, **kwargs):
    return MockResponseContext()

def create_client():
  client = OctopusEnergyApiClient("test-api-key")
  client._graphql_token = "test-token"
  client._graphql_expiration = now() + timedelta(hours=1)
  return client

def devices_body():
  return { "data": { "devices": [{
    "id": device_id,
    "name": device_name,
    "provider": "SIGENERGY",
    "deviceType": "INVERTERS",
    "status": { "current": "LIVE" },
    "make": "Sigenergy",
    "model": "SigenStor",
  }] } }

def dispatches():
  return [{ "start": "2026-10-14T11:00:00+00:00", "end": "2026-10-14T11:30:00+00:00", "energyAddedKwh": "-6.875", "type": "SMART" }]

def dispatches_body():
  return { "data": {
    "devices": [{
      "id": device_id,
      "status": { "current": "LIVE", "currentState": "SMART_CONTROL_CAPABLE", "isSuspended": False },
      "telemetry": {
        "inverter": { "connectionStatus": "ONLINE", "powerInKw": "4.125" },
        "battery": { "connectionStatus": "ONLINE", "powerInKw": "4.125", "stateOfCharge": "73.25" },
      },
    }],
    "flexPlannedDispatches": dispatches(),
  } }

def plan_body():
  return { "data": { "flexPlannedDispatches": dispatches() } }

def assert_nothing_private_logged(caplog):
  for value in private_values:
    assert value not in caplog.text, f"{value} was logged"

@pytest.mark.asyncio
async def test_when_devices_are_discovered_then_only_the_status_is_logged(caplog):
  caplog.set_level(logging.DEBUG)
  client = create_client()

  with mock.patch(create_client_session_target, return_value=MockClientSession()):
    with mock.patch(read_response_target, return_value=devices_body()):
      result = await client.async_get_charge_pack_devices(account_id)

  assert len(result) == 1
  assert result[0].id == device_id
  assert "get-charge-pack-devices: HTTP 200" in caplog.text
  assert_nothing_private_logged(caplog)

@pytest.mark.asyncio
async def test_when_dispatches_are_read_then_only_the_status_is_logged(caplog):
  caplog.set_level(logging.DEBUG)
  client = create_client()

  with mock.patch(create_client_session_target, return_value=MockClientSession()):
    with mock.patch(read_response_target, return_value=dispatches_body()):
      result = await client.async_get_charge_pack_dispatches(account_id, device_id)

  assert len(result.planned) == 1
  assert result.telemetry is not None
  assert "charge-pack-dispatches: HTTP 200" in caplog.text
  assert_nothing_private_logged(caplog)

@pytest.mark.asyncio
async def test_when_falling_back_to_the_plan_then_the_device_is_not_logged(caplog):
  caplog.set_level(logging.DEBUG)
  client = create_client()

  with mock.patch(create_client_session_target, return_value=MockClientSession()):
    with mock.patch(read_response_target, side_effect=[RequestException("Failed to send request", []), plan_body()]):
      result = await client.async_get_charge_pack_dispatches(account_id, device_id)

  assert len(result.planned) == 1
  assert result.status is None
  assert "retrieving its plan only" in caplog.text
  assert "charge-pack-plan: HTTP 200" in caplog.text
  assert_nothing_private_logged(caplog)
