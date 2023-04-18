from datetime import datetime
import pytest

from custom_components.octopus_energy.saving_sessions import get_next_saving_sessions_event

@pytest.mark.asyncio
async def test_when_future_events_present_then_next_event_returned():
  events = [
    {
      "start": datetime.strptime("2022-12-06T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end": datetime.strptime("2022-12-06T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "start": datetime.strptime("2022-12-05T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end": datetime.strptime("2022-12-05T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "start": datetime.strptime("2022-12-07T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end": datetime.strptime("2022-12-07T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    }
  ]

  current_date = datetime.strptime("2022-12-04T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  result = get_next_saving_sessions_event(
    current_date,
    events,
  )

  assert result["start"] == events[1]["start"]
  assert result["end"] == events[1]["end"]
  assert result["duration_in_minutes"] == 60

@pytest.mark.asyncio
async def test_when_no_future_events_present_then_none_returned():
  events = [
    {
      "start": datetime.strptime("2022-12-06T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end": datetime.strptime("2022-12-06T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "start": datetime.strptime("2022-12-05T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end": datetime.strptime("2022-12-05T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    },
    {
      "start": datetime.strptime("2022-12-07T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end": datetime.strptime("2022-12-07T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    }
  ]

  current_date = datetime.strptime("2022-12-08T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  result = get_next_saving_sessions_event(
    current_date,
    events,
  )

  assert result == None