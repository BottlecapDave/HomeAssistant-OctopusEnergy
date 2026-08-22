from custom_components.octopus_energy.api_client.free_electricity_sessions import FreeElectricitySessionsResponse
import pytest
import mock
from datetime import datetime, timedelta

from custom_components.octopus_energy.coordinators.power_up_down_sessions import PowerUpDownSessionsCoordinatorResult, async_refresh_power_up_down_sessions
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.saving_sessions import SavingSession, SavingSessionsResponse
from custom_components.octopus_energy.const import EVENT_ALL_FREE_ELECTRICITY_SESSIONS, EVENT_ALL_POWER_UP_SESSIONS, EVENT_ALL_SAVING_SESSIONS, EVENT_NEW_SAVING_SESSION, EVENT_ALL_POWER_DOWN_SESSIONS, EVENT_NEW_POWER_DOWN_SESSION, REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN

region = "1"

def assert_raised_new_power_down_event(
  raised_event: dict,
  account_id: str,
  expected_event: SavingSession
):
  assert "account_id" in raised_event
  assert raised_event["account_id"] == account_id

  assert "event_id" in raised_event
  assert raised_event["event_id"] == expected_event.id

  assert "event_code" in raised_event
  assert raised_event["event_code"] == expected_event.code

  assert "event_start" in raised_event
  assert raised_event["event_start"] == expected_event.start

  assert "event_end" in raised_event
  assert raised_event["event_end"] == expected_event.end

  assert "event_duration_in_minutes" in raised_event
  assert raised_event["event_duration_in_minutes"] == expected_event.duration_in_minutes
  
  assert "event_octopoints_per_kwh" in raised_event
  assert raised_event["event_octopoints_per_kwh"] == expected_event.octopoints

def assert_raised_all_power_down_event(
  raised_event: dict,
  account_id: str,
  all_available_events: list[SavingSession],
  expected_available_events: list[SavingSession],
  expected_joined_events: list[SavingSession]
):
  assert "account_id" in raised_event
  assert raised_event["account_id"] == account_id

  assert "available_events" in raised_event
  assert len(expected_available_events) == len(raised_event["available_events"])
  for idx, actual_event in enumerate(raised_event["available_events"]):
    expected_event = expected_available_events[idx]

    assert "id" in actual_event
    assert actual_event["id"] == expected_event.id

    assert "code" in actual_event
    assert actual_event["code"] == expected_event.code

    assert "start" in actual_event
    assert actual_event["start"] == expected_event.start

    assert "end" in actual_event
    assert actual_event["end"] == expected_event.end

    assert "duration_in_minutes" in actual_event
    assert actual_event["duration_in_minutes"] == expected_event.duration_in_minutes
    
    assert "octopoints_per_kwh" in actual_event
    assert actual_event["octopoints_per_kwh"] == expected_event.octopoints

  assert len(expected_joined_events) == len(raised_event["joined_events"])
  for idx, actual_event in enumerate(raised_event["joined_events"]):
    expected_event = expected_joined_events[idx]

    assert "id" in actual_event
    assert actual_event["id"] == expected_event.id

    assert "start" in actual_event
    assert actual_event["start"] == expected_event.start

    assert "end" in actual_event
    assert actual_event["end"] == expected_event.end

    assert "duration_in_minutes" in actual_event
    assert actual_event["duration_in_minutes"] == expected_event.duration_in_minutes
    
    assert "rewarded_octopoints" in actual_event
    assert actual_event["rewarded_octopoints"] == expected_event.octopoints

    expected_available_event = None
    for event in all_available_events:
      if event.id == expected_event.id:
        expected_available_event = event
        break

    assert expected_available_event is not None
    assert "octopoints_per_kwh" in actual_event
    assert actual_event["octopoints_per_kwh"] == expected_available_event.octopoints

def assert_raised_all_power_up_event(
  raised_event: dict,
  account_id: str,
  all_available_events: list[SavingSession],
  joined_events: list[SavingSession]
):
  assert "account_id" in raised_event
  assert raised_event["account_id"] == account_id

  for idx, actual_event in enumerate(raised_event["events"]):
    expected_event = joined_events[idx]

    assert "start" in actual_event
    assert actual_event["start"] == expected_event.start

    assert "end" in actual_event
    assert actual_event["end"] == expected_event.end

    assert "duration_in_minutes" in actual_event
    assert actual_event["duration_in_minutes"] == expected_event.duration_in_minutes

    expected_available_event = None
    for event in all_available_events:
      if event.id == expected_event.id:
        expected_available_event = event
        break

    assert expected_available_event is not None

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_and_previous_data_is_available_then_previous_data_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  account_id = "ABC123"

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  previous_data=PowerUpDownSessionsCoordinatorResult(current_utc_timestamp, 1, [], [], [], [])

  # Act
  result = await async_refresh_power_up_down_sessions(
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
async def test_when_upcoming_power_down_events_contains_events_in_past_then_events_filtered_out():
  # Arrange
  account_id = "ABC123"
  previous_data=None

  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", "ABC", current_utc_timestamp - timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [], [], [], region)

  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
    return FreeElectricitySessionsResponse([])

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions, async_get_free_electricity_sessions=async_mocked_get_free_electricity_sessions):
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_power_up_down_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None

    assert len(actual_fired_events) == 4
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [], [], [])
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_POWER_DOWN_SESSIONS], account_id, [], [], [])

    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_POWER_UP_SESSIONS], account_id, [], [])
    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_FREE_ELECTRICITY_SESSIONS], account_id, [], [])

@pytest.mark.asyncio
async def test_when_upcoming_power_down_events_contains_joined_events_then_events_filtered_out():
  # Arrange
  account_id = "ABC123"
  previous_data=None
    
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", "ABC", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [expected_saving_session], [], [], region)

  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
      return FreeElectricitySessionsResponse([])
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions, async_get_free_electricity_sessions=async_mocked_get_free_electricity_sessions):
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_power_up_down_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None

    assert len(actual_fired_events) == 4
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [expected_saving_session], [], [expected_saving_session])
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_POWER_DOWN_SESSIONS], account_id, [expected_saving_session], [], [expected_saving_session])

    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_POWER_UP_SESSIONS], account_id, [], [])
    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_FREE_ELECTRICITY_SESSIONS], account_id, [], [])

@pytest.mark.asyncio
async def test_when_upcoming_power_down_events_present_and_no_previous_data_then_new_event_fired():
  # Arrange
  account_id = "ABC123"
  previous_data=None
    
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", "ABC", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [], [], [], region)

  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
      return FreeElectricitySessionsResponse([])
  
  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
      return FreeElectricitySessionsResponse([])
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions, async_get_free_electricity_sessions=async_mocked_get_free_electricity_sessions):
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_power_up_down_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None

    assert len(actual_fired_events) == 6
    assert_raised_new_power_down_event(actual_fired_events[EVENT_NEW_SAVING_SESSION], account_id, expected_saving_session)
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [expected_saving_session], [expected_saving_session], [])
    assert_raised_new_power_down_event(actual_fired_events[EVENT_NEW_POWER_DOWN_SESSION], account_id, expected_saving_session)
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_POWER_DOWN_SESSIONS], account_id, [expected_saving_session], [expected_saving_session], [])

    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_POWER_UP_SESSIONS], account_id, [], [])
    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_FREE_ELECTRICITY_SESSIONS], account_id, [], [])

@pytest.mark.asyncio
@pytest.mark.parametrize("targetRegions", [
  (None),
  ([]),
  (["1", "2"]),
])
async def test_when_upcoming_power_down_events_present_and_not_in_previous_data_then_new_event_fired(targetRegions: list[str] | None):
  # Arrange
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  account_id = "ABC123"
  previous_data = PowerUpDownSessionsCoordinatorResult(current_utc_timestamp - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN), 1, [], [], [], [])

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", "ABC", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1, targetRegions)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [], [], [], region)

  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
      return FreeElectricitySessionsResponse([])
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions, async_get_free_electricity_sessions=async_mocked_get_free_electricity_sessions):
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_power_up_down_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None
    assert len(result.available_power_down_events) == 1
    assert result.available_power_down_events[0] == expected_saving_session

    assert len(actual_fired_events) == 6
    assert_raised_new_power_down_event(actual_fired_events[EVENT_NEW_SAVING_SESSION], account_id, expected_saving_session)
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [expected_saving_session], [expected_saving_session], [])
    assert_raised_new_power_down_event(actual_fired_events[EVENT_NEW_POWER_DOWN_SESSION], account_id, expected_saving_session)
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_POWER_DOWN_SESSIONS], account_id, [expected_saving_session], [expected_saving_session], [])

    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_POWER_UP_SESSIONS], account_id, [], [])
    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_FREE_ELECTRICITY_SESSIONS], account_id, [], [])

@pytest.mark.asyncio
async def test_when_upcoming_power_down_events_present_but_for_different_region_then_not_in_upcoming_events():
  # Arrange
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  account_id = "ABC123"
  previous_data = PowerUpDownSessionsCoordinatorResult(current_utc_timestamp - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN), 1, [], [], [], [])

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", "ABC", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1, ["_C", "_B"])
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [], [], [], region)

  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
      return FreeElectricitySessionsResponse([])
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions, async_get_free_electricity_sessions=async_mocked_get_free_electricity_sessions):
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_power_up_down_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None
    assert len(result.available_power_down_events) == 0

    assert len(actual_fired_events) == 4
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [expected_saving_session], [], [])
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_POWER_DOWN_SESSIONS], account_id, [expected_saving_session], [], [])

    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_POWER_UP_SESSIONS], account_id, [], [])
    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_FREE_ELECTRICITY_SESSIONS], account_id, [], [])


@pytest.mark.asyncio
async def test_when_upcoming_power_down_events_present_and_in_previous_data_then_new_event_not_fired():
  # Arrange
  account_id = "ABC123"
    
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", "ABC", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [], [], [], region)
  
  previous_data = PowerUpDownSessionsCoordinatorResult(current_utc_timestamp - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN), 1, [expected_saving_session], [], [], [])

  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
      return FreeElectricitySessionsResponse([])
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions, async_get_free_electricity_sessions=async_mocked_get_free_electricity_sessions):
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_power_up_down_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None

    assert len(actual_fired_events) == 4
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [expected_saving_session], [expected_saving_session], [])
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_POWER_DOWN_SESSIONS], account_id, [expected_saving_session], [expected_saving_session], [])

    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_POWER_UP_SESSIONS], account_id, [], [])
    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_FREE_ELECTRICITY_SESSIONS], account_id, [], [])

@pytest.mark.asyncio
async def test_when_upcoming_power_down_events_present_and_in_previous_data_but_with_different_event_code_then_new_event_fired():
  # Arrange
  account_id = "ABC123"
    
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", "ABC", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [], [], [], region)
  
  previous_data = PowerUpDownSessionsCoordinatorResult(current_utc_timestamp - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN), 1, [SavingSession("1", "DEF", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)], [], [], [])

  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
      return FreeElectricitySessionsResponse([])
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions, async_get_free_electricity_sessions=async_mocked_get_free_electricity_sessions):
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_power_up_down_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None

    assert len(actual_fired_events) == 6
    assert_raised_new_power_down_event(actual_fired_events[EVENT_NEW_SAVING_SESSION], account_id, expected_saving_session)
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [expected_saving_session], [expected_saving_session], [])
    assert_raised_new_power_down_event(actual_fired_events[EVENT_NEW_POWER_DOWN_SESSION], account_id, expected_saving_session)
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_POWER_DOWN_SESSIONS], account_id, [expected_saving_session], [expected_saving_session], [])

    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_POWER_UP_SESSIONS], account_id, [], [])
    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_FREE_ELECTRICITY_SESSIONS], account_id, [], [])

@pytest.mark.asyncio
async def test_when_previous_data_is_out_of_date_then_new_date_is_retrieved():
  # Arrange
  account_id = "ABC123"
    
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  saving_sessions_retrieved = False
  expected_saving_session = SavingSession("1", "ABC", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    nonlocal saving_sessions_retrieved
    saving_sessions_retrieved = True
    return SavingSessionsResponse([], [expected_saving_session], [], [], region)
  
  previous_data = PowerUpDownSessionsCoordinatorResult(current_utc_timestamp - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN), 1, [], [expected_saving_session], [], [])

  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
      return FreeElectricitySessionsResponse([])
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions, async_get_free_electricity_sessions=async_mocked_get_free_electricity_sessions):
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_power_up_down_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.next_refresh == current_utc_timestamp.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN)
    assert saving_sessions_retrieved == True

@pytest.mark.asyncio
async def test_when_exception_raised_then_previous_data_is_returned_and_exception_captured():
  # Arrange
  account_id = "ABC123"
    
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  saving_sessions_retrieved = False
  raised_exception = RequestException("foo", [])
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    nonlocal saving_sessions_retrieved
    saving_sessions_retrieved = True
    raise raised_exception
  
  previous_data = PowerUpDownSessionsCoordinatorResult(current_utc_timestamp - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN), 1, [], [SavingSession("1", "ABC", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1)], [], [])

  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
      return FreeElectricitySessionsResponse([])
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions, async_get_free_electricity_sessions=async_mocked_get_free_electricity_sessions):
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_power_up_down_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.available_power_down_events == previous_data.available_power_down_events
    assert result.joined_power_down_events == previous_data.joined_power_down_events
    assert result.last_evaluated == previous_data.last_evaluated
    assert result.request_attempts == previous_data.request_attempts + 1
    assert result.next_refresh == previous_data.next_refresh + timedelta(minutes=1)
    assert result.last_error == raised_exception
    assert saving_sessions_retrieved == True

@pytest.mark.asyncio
async def test_when_upcoming_power_down_events_present_and_region_is_none_then_not_in_upcoming_events():
  # Arrange
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  account_id = "ABC123"
  previous_data = PowerUpDownSessionsCoordinatorResult(current_utc_timestamp - timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_POWER_DOWN), 1, [], [], [], [])

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  expected_saving_session = SavingSession("1", "ABC", current_utc_timestamp + timedelta(minutes=1), current_utc_timestamp + timedelta(minutes=31), 1, ["_C", "_B"])
  async def async_mocked_get_saving_sessions(*args, **kwargs):
    return SavingSessionsResponse([expected_saving_session], [], [], [], None)

  async def async_mocked_get_free_electricity_sessions(*args, **kwargs):
      return FreeElectricitySessionsResponse([])
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_saving_sessions=async_mocked_get_saving_sessions, async_get_free_electricity_sessions=async_mocked_get_free_electricity_sessions):
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_power_up_down_sessions(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      fire_event
    )

    # Assert
    assert result is not None
    assert len(result.available_power_down_events) == 0

    assert len(actual_fired_events) == 4
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_SAVING_SESSIONS], account_id, [expected_saving_session], [], [])
    assert_raised_all_power_down_event(actual_fired_events[EVENT_ALL_POWER_DOWN_SESSIONS], account_id, [expected_saving_session], [], [])

    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_POWER_UP_SESSIONS], account_id, [], [])
    assert_raised_all_power_up_event(actual_fired_events[EVENT_ALL_FREE_ELECTRICITY_SESSIONS], account_id, [], [])