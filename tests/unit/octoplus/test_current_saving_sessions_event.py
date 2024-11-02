from datetime import datetime
import pytest

from custom_components.octopus_energy.octoplus import current_octoplus_sessions_event
from custom_components.octopus_energy.api_client.saving_sessions import SavingSession

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date",[
  (datetime.strptime("2022-12-05T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-12-05T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"))
])
async def test_when_active_event_present_then_true_is_returned(current_date):
  events = [
    SavingSession("1", "ABC", datetime.strptime("2022-12-06T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2022-12-06T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 0),
    SavingSession("2", "ABC", datetime.strptime("2022-12-05T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2022-12-05T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 0),
    SavingSession("3", "ABC", datetime.strptime("2022-12-07T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2022-12-07T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 0)
  ]

  result = current_octoplus_sessions_event(
    current_date,
    events,
  )

  assert result is not None
  assert result == events[1]
  assert result.duration_in_minutes == 60

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date",[
  (datetime.strptime("2022-12-05T16:59:59Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-12-05T18:00:01Z", "%Y-%m-%dT%H:%M:%S%z"))
])
async def test_when_no_active_event_present_then_false_is_returned(current_date):
  events = [
    SavingSession("1", "ABC", datetime.strptime("2022-12-06T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2022-12-06T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 0),
  ]

  result = current_octoplus_sessions_event(
    current_date,
    events,
  )

  assert result is None

@pytest.mark.asyncio
async def test_when_events_is_none_then_none_returned():
  events = None
  current_date = datetime.strptime("2022-12-08T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  result = current_octoplus_sessions_event(
    current_date,
    events,
  )

  assert result is None