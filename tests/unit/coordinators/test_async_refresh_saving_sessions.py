from custom_components.octopus_energy.const import EVENT_ALL_SAVING_SESSIONS, EVENT_NEW_SAVING_SESSION
import pytest
import mock
from datetime import datetime, timedelta

from custom_components.octopus_energy.coordinators.saving_sessions import SavingSessionsCoordinatorResult, async_refresh_saving_sessions
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.api_client.saving_sessions import SavingSession, SavingSessionsResponse

def assert_raised_new_saving_session_event(
  raised_event: dict,
  account_id: str,
  expected_event: SavingSession
):
  assert "account_id" in raised_event
  assert raised_event["account_id"] == account_id

  assert "event_id" in raised_event
  assert raised_event["event_id"] == expected_event.id

  assert "event_start" in raised_event
  assert raised_event["event_start"] == expected_event.start

  assert "event_end" in raised_event
  assert raised_event["event_end"] == expected_event.end
  
  assert "event_octopoints" in raised_event
  assert raised_event["event_octopoints"] == expected_event.octopoints

def assert_raised_all_saving_session_event(
  raised_event: dict,
  account_id: str,
  nonjoined_events: list[SavingSession],
  joined_events: list[SavingSession]
):
  assert "account_id" in raised_event
  assert raised_event["account_id"] == account_id

  assert "nonjoined_events" in raised_event
  for idx, actual_event in enumerate(raised_event["nonjoined_events"]):
    expected_event = nonjoined_events[idx]

    assert "id" in actual_event
    assert actual_event["id"] == expected_event.id

    assert "start" in actual_event
    assert actual_event["start"] == expected_event.start

    assert "end" in actual_event
    assert actual_event["end"] == expected_event.end
    
    assert "octopoints" in actual_event
    assert actual_event["octopoints"] == expected_event.octopoints

  for idx, actual_event in enumerate(raised_event["joined_events"]):
    expected_event = joined_events[idx]

    assert "id" in actual_event
    assert actual_event["id"] == expected_event.id

    assert "start" in actual_event
    assert actual_event["start"] == expected_event.start

    assert "end" in actual_event
    assert actual_event["end"] == expected_event.end
    
    assert "octopoints" in actual_event
    assert actual_event["octopoints"] == expected_event.octopoints

@pytest.mark.asyncio
async def test_when_now_is_not_at_30_minute_mark_and_previous_data_is_available_then_previous_data_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  account_id = "ABC123"
  previous_data=SavingSessionsCoordinatorResult(datetime.now(), [], [])

  for minute in range(0, 59):
    if (minute == 0 or minute == 30):
      continue

    actual_fired_events = {}
    def fire_event(name, metadata):
      nonlocal actual_fired_events
      actual_fired_events[name] = metadata
      return None
    
    minuteStr = f'{minute}'.zfill(2)
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minuteStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

    # Act
    result = await async_refresh_saving_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result == previous_data

    assert len(actual_fired_events) == 0

@pytest.mark.asyncio
@pytest.mark.parametrize("minutes",[
  (0),
  (30),
])
async def test_when_upcoming_events_contains_events_in_past_then_events_filtered_out(minutes):
  # Arrange
  account_id = "ABC123"
  previous_data=None
    
  minutesStr = f'{minutes}'.zfill(2)
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", current_utc_timestamp - timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [])

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_saving_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None

    assert len(actual_fired_events) == 1
    assert_raised_all_saving_session_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [], [])

@pytest.mark.asyncio
@pytest.mark.parametrize("minutes",[
  (0),
  (30),
])
async def test_when_upcoming_events_contains_joined_events_then_events_filtered_out(minutes):
  # Arrange
  account_id = "ABC123"
  previous_data=None
    
  minutesStr = f'{minutes}'.zfill(2)
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [expected_saving_session])

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_saving_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None

    assert len(actual_fired_events) == 1
    assert_raised_all_saving_session_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [], [expected_saving_session])

@pytest.mark.asyncio
@pytest.mark.parametrize("minutes",[
  (0),
  (30),
])
async def test_when_upcoming_events_present_and_no_previous_data_then_new_event_fired(minutes):
  # Arrange
  account_id = "ABC123"
  previous_data=None
    
  minutesStr = f'{minutes}'.zfill(2)
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [])

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_saving_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None

    assert len(actual_fired_events) == 2
    assert_raised_new_saving_session_event(actual_fired_events[EVENT_NEW_SAVING_SESSION], account_id, expected_saving_session)
    assert_raised_all_saving_session_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [expected_saving_session], [])

@pytest.mark.asyncio
@pytest.mark.parametrize("minutes",[
  (0),
  (30),
])
async def test_when_upcoming_events_present_and_not_in_previous_data_then_new_event_fired(minutes):
  # Arrange
  account_id = "ABC123"
  previous_data = SavingSessionsCoordinatorResult(datetime.now(), [], [])
    
  minutesStr = f'{minutes}'.zfill(2)
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [])

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_saving_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None

    assert len(actual_fired_events) == 2
    assert_raised_new_saving_session_event(actual_fired_events[EVENT_NEW_SAVING_SESSION], account_id, expected_saving_session)
    assert_raised_all_saving_session_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [expected_saving_session], [])

@pytest.mark.asyncio
@pytest.mark.parametrize("minutes",[
  (0),
  (30),
])
async def test_when_upcoming_events_present_and_in_previous_data_then_new_event_not_fired(minutes):
  # Arrange
  account_id = "ABC123"
    
  minutesStr = f'{minutes}'.zfill(2)
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([], [expected_saving_session])
  
  previous_data = SavingSessionsCoordinatorResult(datetime.now(), [], [expected_saving_session])

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_saving_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None

    assert len(actual_fired_events) == 1
    assert_raised_all_saving_session_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [], [expected_saving_session])