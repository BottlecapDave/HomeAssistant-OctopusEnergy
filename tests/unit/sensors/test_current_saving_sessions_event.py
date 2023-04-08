from datetime import datetime
import pytest

from custom_components.octopus_energy.sensors import current_saving_sessions_event

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date",[
  (datetime.strptime("2022-12-05T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-12-05T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"))
])
async def test_when_active_event_present_then_true_is_returned(current_date):
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

  result = current_saving_sessions_event(
    current_date,
    events,
  )

  assert result is not None
  assert result["start"] == events[1]["start"]
  assert result["end"] == events[1]["end"]
  assert result["duration_in_minutes"] == 60

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date",[
  (datetime.strptime("2022-12-05T16:59:59Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-12-05T18:00:01Z", "%Y-%m-%dT%H:%M:%S%z"))
])
async def test_when_no_active_event_present_then_false_is_returned(current_date):
  events = [
    {
      "start": datetime.strptime("2022-12-05T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end": datetime.strptime("2022-12-05T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    }
  ]

  result = current_saving_sessions_event(
    current_date,
    events,
  )

  assert result is None