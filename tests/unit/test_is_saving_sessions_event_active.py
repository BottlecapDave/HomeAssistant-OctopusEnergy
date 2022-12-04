from datetime import datetime
import pytest

from custom_components.octopus_energy.sensor_utils import is_saving_sessions_event_active

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date",[
  (datetime.strptime("2022-12-05T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2022-12-05T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"))
])
async def test_when_active_event_present_then_true_is_returned(current_date):
  events = [
    {
      "start": datetime.strptime("2022-12-05T17:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "end": datetime.strptime("2022-12-05T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    }
  ]

  result = is_saving_sessions_event_active(
    current_date,
    events,
  )

  assert result == True

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

  result = is_saving_sessions_event_active(
    current_date,
    events,
  )

  assert result == False