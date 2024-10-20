from datetime import datetime, timedelta
import pytest

from custom_components.octopus_energy.api_client.saving_sessions import SavingSession
from custom_components.octopus_energy.octoplus import get_octoplus_session_target

def generate_consumption_data(dates: list, consumption_values: list):
  consumption_data = []

  for index in range(len(dates)):
    consumption_data.append({
      "start": dates[index],
      "end": dates[index] + timedelta(minutes=30),
      "consumption": consumption_values[index % len(consumption_values)]
    })

    consumption_data.append({
      "start": dates[index] + timedelta(minutes=30),
      "end": dates[index] + timedelta(minutes=60),
      "consumption": consumption_values[index % len(consumption_values)]
    })

  return consumption_data

@pytest.mark.asyncio
async def test_when_current_is_before_saving_session_then_first_target_is_returned():
  # Arrange
  current = datetime.strptime("2023-12-25T16:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  saving_session = SavingSession(
    '1',
    'ABC',
    datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-25T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    0
  )

  target_consumption_dates = [
    datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-13T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-12T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-11T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
  ]

  consumption_data = generate_consumption_data(target_consumption_dates, [1.1, 1.2, 1.3])

  # Act
  result = get_octoplus_session_target(current, saving_session, consumption_data)

  # Assert
  assert result is not None
  assert result.current_target is not None
  assert result.current_target == result.baselines[0]
  
  assert len(result.baselines) == 2
  assert result.baselines[0].start == datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  assert result.baselines[0].end == datetime.strptime("2023-12-25T17:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  assert result.baselines[0].baseline == 1.19
  assert result.baselines[0].is_incomplete_calculation == False
  assert len(result.baselines[0].consumption_items) == len(target_consumption_dates)
  for index in range(len(target_consumption_dates)):
    assert result.baselines[0].consumption_items[index]["start"] == target_consumption_dates[index]
    assert result.baselines[0].consumption_items[index]["end"] == target_consumption_dates[index] + timedelta(minutes=30)

  assert result.baselines[1].start == datetime.strptime("2023-12-25T17:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  assert result.baselines[1].end == datetime.strptime("2023-12-25T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  assert result.baselines[1].baseline == 1.19
  assert result.baselines[1].is_incomplete_calculation == False
  assert len(result.baselines[1].consumption_items) == len(target_consumption_dates)
  for index in range(len(target_consumption_dates)):
    assert result.baselines[1].consumption_items[index]["start"] == target_consumption_dates[index] + timedelta(minutes=30)
    assert result.baselines[1].consumption_items[index]["end"] == target_consumption_dates[index] + timedelta(minutes=60)
  
@pytest.mark.asyncio
@pytest.mark.parametrize("current,expected_index",[
  (datetime.strptime("2023-12-25T17:29:59+01:00", "%Y-%m-%dT%H:%M:%S%z"), 0),
  (datetime.strptime("2023-12-25T17:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z"), 1),
])
async def test_when_current_is_during_saving_session_then_correct_target_is_returned(current: datetime, expected_index: int):
  # Arrange
  saving_session = SavingSession(
    '1',
    'ABC',
    datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-25T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    0
  )

  target_consumption_dates = [
    datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-13T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-12T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-11T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
  ]

  consumption_data = generate_consumption_data(target_consumption_dates, [1.1, 1.2, 1.3])

  # Act
  result = get_octoplus_session_target(current, saving_session, consumption_data)

  # Assert
  assert result is not None
  assert result.current_target is not None
  assert result.current_target == result.baselines[expected_index]
  
  assert len(result.baselines) == 2
  assert result.baselines[0].start == datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  assert result.baselines[0].end == datetime.strptime("2023-12-25T17:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  assert result.baselines[0].baseline == 1.19
  assert result.baselines[0].is_incomplete_calculation == False
  assert len(result.baselines[0].consumption_items) == len(target_consumption_dates)
  for index in range(len(target_consumption_dates)):
    assert result.baselines[0].consumption_items[index]["start"] == target_consumption_dates[index]
    assert result.baselines[0].consumption_items[index]["end"] == target_consumption_dates[index] + timedelta(minutes=30)

  assert result.baselines[1].start == datetime.strptime("2023-12-25T17:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  assert result.baselines[1].end == datetime.strptime("2023-12-25T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  assert result.baselines[1].baseline == 1.19
  assert result.baselines[1].is_incomplete_calculation == False
  assert len(result.baselines[1].consumption_items) == len(target_consumption_dates)
  for index in range(len(target_consumption_dates)):
    assert result.baselines[1].consumption_items[index]["start"] == target_consumption_dates[index] + timedelta(minutes=30)
    assert result.baselines[1].consumption_items[index]["end"] == target_consumption_dates[index] + timedelta(minutes=60)

@pytest.mark.asyncio
async def test_when_current_after_saving_session_then_none_is_returned():
  # Arrange
  current = datetime.strptime("2023-12-25T18:00:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  saving_session = SavingSession(
    '1',
    'ABC',
    datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-25T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    0
  )

  target_consumption_dates = [
    datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-13T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-12T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-11T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
  ]

  consumption_data = generate_consumption_data(target_consumption_dates, [1.1, 1.2, 1.3])

  # Act
  result = get_octoplus_session_target(current, saving_session, consumption_data)

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_saving_session_is_none_then_none_is_returned():
  # Arrange
  current = datetime.strptime("2023-12-25T16:00:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  saving_session = None

  target_consumption_dates = [
    datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-13T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-12T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-11T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
  ]

  consumption_data = generate_consumption_data(target_consumption_dates, [1.1, 1.2, 1.3])

  # Act
  result = get_octoplus_session_target(current, saving_session, consumption_data)

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_saving_session_is_weekday_and_consumption_data_is_incomplete_then_incomplete_flag_is_set():
  # Arrange
  current = datetime.strptime("2023-12-25T16:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  saving_session = SavingSession(
    '1',
    'ABC',
    datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-25T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    0
  )

  target_consumption_dates = [
    datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-13T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-12T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
  ]

  consumption_data = generate_consumption_data(target_consumption_dates, [1.1, 1.2, 1.3])

  # Act
  result = get_octoplus_session_target(current, saving_session, consumption_data)

  # Assert
  assert result is not None
  assert result.current_target is not None
  assert result.current_target == result.baselines[0]
  assert result.current_target.is_incomplete_calculation == True

@pytest.mark.asyncio
async def test_when_saving_session_is_weekend_and_consumption_data_is_incomplete_then_incomplete_flag_is_set():
  # Arrange
  current = datetime.strptime("2023-12-31T16:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  saving_session = SavingSession(
    '1',
    'ABC',
    datetime.strptime("2023-12-31T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-31T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    0
  )

  target_consumption_dates = [
    datetime.strptime("2023-12-30T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-24T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-23T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
  ]

  consumption_data = generate_consumption_data(target_consumption_dates, [1.1, 1.2, 1.3])

  # Act
  result = get_octoplus_session_target(current, saving_session, consumption_data)

  # Assert
  assert result is not None
  assert result.current_target is not None
  assert result.current_target == result.baselines[0]
  assert result.current_target.is_incomplete_calculation == True