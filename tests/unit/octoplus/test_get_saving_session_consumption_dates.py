from datetime import datetime, timedelta
import pytest


from custom_components.octopus_energy.api_client.saving_sessions import SavingSession
from custom_components.octopus_energy.octoplus import get_octoplus_session_consumption_dates

@pytest.mark.asyncio
@pytest.mark.parametrize("saving_session_start,expected_result",[
  (
    # Sunday
    datetime.strptime("2023-12-31T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-30T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-24T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-23T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-17T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Saturday
    datetime.strptime("2023-12-30T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-24T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-23T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-17T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-16T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Friday
    datetime.strptime("2023-12-29T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-28T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-27T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-26T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Thursday
    datetime.strptime("2023-12-28T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-27T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-26T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Wednesday
    datetime.strptime("2023-12-27T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-26T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-13T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Tuesday
    datetime.strptime("2023-12-26T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
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
  ),
  (
    # Monday
    datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
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
  )
])
async def test_when_no_previous_saving_sessions_then_correct_dates_returned(saving_session_start: datetime, expected_result: list[datetime]):
  # Arrange
  saving_session_diff = timedelta(minutes=90)
  previous_saving_sessions = []
  saving_session = SavingSession('1', 'ABC', saving_session_start, saving_session_start + saving_session_diff, 0)

  # Act
  result = get_octoplus_session_consumption_dates(saving_session, previous_saving_sessions)

  # Assert
  assert len(result) == len(expected_result)
  for index in range(len(expected_result)):
    expected_start = expected_result[index]
    expected_end = expected_start + saving_session_diff

    assert result[index].start == expected_start
    assert result[index].end == expected_end

@pytest.mark.asyncio
@pytest.mark.parametrize("saving_session_start,previous_saving_session_start,expected_result",[
  (
    # Sunday
    datetime.strptime("2023-12-31T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-24T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-30T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-23T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-17T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-16T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Saturday
    datetime.strptime("2023-12-30T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-23T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-24T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-17T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-16T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-10T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Friday
    datetime.strptime("2023-12-29T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-26T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-28T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-27T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Thursday
    datetime.strptime("2023-12-28T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-25T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-27T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-26T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-13T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Wednesday
    datetime.strptime("2023-12-27T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-22T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-26T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-13T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-12T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Tuesday
    datetime.strptime("2023-12-26T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-21T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-20T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-13T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-12T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-11T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  ),
  (
    # Monday
    datetime.strptime("2023-12-25T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-12-20T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [
      datetime.strptime("2023-12-22T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-21T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-19T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-18T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-15T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-14T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-13T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-12T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-11T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2023-12-08T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    ]
  )
])
async def test_when_previous_saving_sessions_present_then_returned_dates_do_not_include_saving_session(saving_session_start: datetime, previous_saving_session_start: datetime, expected_result: list[datetime]):
  # Arrange
  saving_session_diff = timedelta(minutes=90)
  previous_saving_sessions = [SavingSession('2', 'DEF',previous_saving_session_start, previous_saving_session_start + timedelta(hours=1), 0)]
  saving_session = SavingSession('1', 'ABC', saving_session_start, saving_session_start + saving_session_diff, 0)

  # Act
  result = get_octoplus_session_consumption_dates(saving_session, previous_saving_sessions)

  # Assert
  assert len(result) == len(expected_result)
  for index in range(len(expected_result)):
    expected_start = expected_result[index]
    expected_end = expected_start + saving_session_diff

    assert result[index].start == expected_start
    assert result[index].end == expected_end