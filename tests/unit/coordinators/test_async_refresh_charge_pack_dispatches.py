from datetime import datetime, timedelta
import pytest
import mock

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.charge_pack import ChargePackDispatch, ChargePackDispatches, ChargePackStatus, ChargePackTelemetry
from custom_components.octopus_energy.coordinators.charge_pack import ChargePackDispatchesCoordinatorResult, async_refresh_charge_pack_dispatches

current = datetime.strptime("2026-10-14T10:30:01+00:00", "%Y-%m-%dT%H:%M:%S%z")
last_retrieved = datetime.strptime("2026-10-14T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
account_id = "A-12345678"
device_id = "00000000-0011-4000-8020-000000000000"

def get_dispatch(start_offset_minutes: int, end_offset_minutes: int, energy: float = -4.5):
  return ChargePackDispatch(current + timedelta(minutes=start_offset_minutes), current + timedelta(minutes=end_offset_minutes), energy, "SMART")

def get_status(current_state: str = "SMART_CONTROL_CAPABLE"):
  return ChargePackStatus("LIVE", current_state, False)

def get_telemetry(state_of_charge: float = 50):
  return ChargePackTelemetry(state_of_charge, -3.0, "ONLINE", -3.2, "ONLINE", 1.5, 1.7, 0.4, 0, 12.0)

class SaveHistory:
  def __init__(self):
    self.calls = []

  async def __call__(self, history):
    self.calls.append(history)

async def refresh(read, existing_result, mock_data = False):
  """Refresh with a client whose async_get_charge_pack_dispatches returns read (or raises it, if it's an exception)"""
  api_calls = 0
  async def async_mock_get_charge_pack_dispatches(*args, **kwargs):
    nonlocal api_calls
    api_calls += 1
    if isinstance(read, Exception):
      raise read
    return read

  save_history = SaveHistory()
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_charge_pack_dispatches=async_mock_get_charge_pack_dispatches):
    client = OctopusEnergyApiClient("NOT_REAL")
    result: ChargePackDispatchesCoordinatorResult = await async_refresh_charge_pack_dispatches(
      current,
      client,
      account_id,
      device_id,
      existing_result,
      save_history,
      mock_data
    )

  return result, api_calls, save_history

@pytest.mark.asyncio
async def test_when_existing_result_is_none_then_dispatches_retrieved():
  planned = [get_dispatch(60, 120), get_dispatch(-30, 30, 6.0)]
  status = get_status()
  telemetry = get_telemetry()

  result, api_calls, save_history = await refresh(ChargePackDispatches(planned, status, telemetry), None)

  assert api_calls == 1
  assert result.last_evaluated == current
  assert result.last_retrieved == current
  assert result.request_attempts == 1
  assert result.last_error is None
  assert result.planned == planned
  assert result.status == status
  assert result.status_retrieved == current
  assert result.telemetry == telemetry
  assert result.telemetry_retrieved == current

  # The dispatch that's started joins the history
  assert result.history == [planned[1]]
  assert save_history.calls == [[planned[1]]]

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_then_existing_result_returned():
  planned = [get_dispatch(60, 120)]
  existing_result = ChargePackDispatchesCoordinatorResult(current, 1, planned, [], status=get_status(), status_retrieved=current)

  result, api_calls, save_history = await refresh(ChargePackDispatches([], None, None), existing_result)

  assert api_calls == 0
  assert result == existing_result
  assert result.planned == planned
  assert save_history.calls == []

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_and_a_dispatch_has_started_then_it_joins_the_history():
  started = get_dispatch(-1, 30)
  existing_result = ChargePackDispatchesCoordinatorResult(current - timedelta(minutes=1), 1, [started], [])

  result, api_calls, save_history = await refresh(ChargePackDispatches([], None, None), existing_result)

  assert api_calls == 0
  assert result.history == [started]
  assert save_history.calls == [[started]]

@pytest.mark.asyncio
async def test_when_history_is_unchanged_then_it_is_not_saved():
  planned = [get_dispatch(60, 120)]

  result, api_calls, save_history = await refresh(ChargePackDispatches(planned, None, None), None)

  assert api_calls == 1
  assert result.history == []
  assert save_history.calls == []

@pytest.mark.asyncio
async def test_when_status_and_telemetry_not_sent_then_previous_values_kept_with_their_retrieved_times():
  previous_status = get_status()
  previous_telemetry = get_telemetry(40)
  existing_result = ChargePackDispatchesCoordinatorResult(last_retrieved, 1, [], [],
                                                          status=previous_status, status_retrieved=last_retrieved,
                                                          telemetry=previous_telemetry, telemetry_retrieved=last_retrieved)
  planned = [get_dispatch(60, 120)]

  result, api_calls, save_history = await refresh(ChargePackDispatches(planned, None, None), existing_result)

  assert api_calls == 1
  assert result.last_retrieved == current
  assert result.planned == planned
  assert result.status == previous_status
  assert result.status_retrieved == last_retrieved
  assert result.telemetry == previous_telemetry
  assert result.telemetry_retrieved == last_retrieved

@pytest.mark.asyncio
async def test_when_only_telemetry_sent_then_only_telemetry_updated():
  previous_status = get_status()
  existing_result = ChargePackDispatchesCoordinatorResult(last_retrieved, 1, [], [],
                                                          status=previous_status, status_retrieved=last_retrieved,
                                                          telemetry=get_telemetry(40), telemetry_retrieved=last_retrieved)
  telemetry = get_telemetry(45)

  result, api_calls, save_history = await refresh(ChargePackDispatches([], None, telemetry), existing_result)

  assert result.status == previous_status
  assert result.status_retrieved == last_retrieved
  assert result.telemetry == telemetry
  assert result.telemetry_retrieved == current

@pytest.mark.asyncio
async def test_when_request_fails_then_existing_data_kept():
  planned = [get_dispatch(60, 120)]
  history = [get_dispatch(-120, -60)]
  status = get_status()
  telemetry = get_telemetry()
  existing_result = ChargePackDispatchesCoordinatorResult(last_retrieved, 1, planned, history,
                                                          status=status, status_retrieved=last_retrieved,
                                                          telemetry=telemetry, telemetry_retrieved=last_retrieved)
  error = RequestException("foo", [])

  result, api_calls, save_history = await refresh(error, existing_result)

  assert api_calls == 1
  assert result.last_evaluated == existing_result.last_evaluated
  assert result.last_retrieved == existing_result.last_retrieved
  assert result.request_attempts == existing_result.request_attempts + 1
  assert result.last_error == error
  assert result.planned == planned
  assert result.history == history
  assert result.status == status
  assert result.status_retrieved == last_retrieved
  assert result.telemetry == telemetry
  assert result.telemetry_retrieved == last_retrieved
  assert save_history.calls == []

@pytest.mark.asyncio
async def test_when_request_fails_and_no_existing_result_then_empty_result_returned():
  error = RequestException("foo", [])

  result, api_calls, save_history = await refresh(error, None)

  assert api_calls == 1
  assert result.last_evaluated == current - timedelta(minutes=3)
  assert result.request_attempts == 2
  assert result.last_error == error
  assert result.planned == []
  assert result.history == []
  assert result.status is None
  assert result.telemetry is None

@pytest.mark.asyncio
async def test_when_unexpected_error_then_it_is_raised():
  with pytest.raises(ValueError):
    await refresh(ValueError("unexpected"), None)

@pytest.mark.asyncio
async def test_when_mock_is_true_then_api_not_called():
  result, api_calls, save_history = await refresh(ChargePackDispatches([], None, None), None, True)

  assert api_calls == 0
  assert len(result.planned) > 0
  assert result.status is not None
  assert result.telemetry is not None
