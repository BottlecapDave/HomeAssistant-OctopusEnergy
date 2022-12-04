from datetime import datetime
import pytest

from custom_components.octopus_energy.sensor_utils import get_next_season_savings_event

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

  result = get_next_season_savings_event(
    current_date,
    events,
  )

  assert result == events[1]["start"]

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

  result = get_next_season_savings_event(
    current_date,
    events,
  )

  assert result == None