from datetime import datetime, timedelta
import pytest

from custom_components.octopus_energy.utils.weightings import validate_rate_weightings

@pytest.mark.asyncio
async def test_when_weightings_is_none_then_empty_list_returned():
  weightings: list[dict] = None

  result = validate_rate_weightings(weightings)
  assert result.success == True
  assert result.weightings == []

@pytest.mark.asyncio
async def test_when_weightings_is_empty_list_then_empty_list_returned():
  weightings: list[dict] = []

  result = validate_rate_weightings(weightings)
  assert result.success == True
  assert result.weightings == []

@pytest.mark.asyncio
@pytest.mark.parametrize("start",[
  ("A"),
  ("2024-13-01T00:00:00Z"),
  ("2024-12-32T00:00:00Z"),
  ("2024-12-24T24:00:00Z"),
  ("2024-12-24T23:60:00Z"),
  ("2024-12-24T23:00:60Z"),
])
async def test_when_start_is_not_valid_iso_datetime_then_error_is_returned(start: str):
  weightings: list[dict] = [
    {
      "start": start,
      "end": "2024-12-24T00:30:00Z",
      "weighting": 1.5
    }
  ]

  result = validate_rate_weightings(weightings)
  assert result.success == False
  assert result.error_message == "start was not a valid ISO datetime in string format at index 0"

@pytest.mark.asyncio
async def test_when_start_does_not_contain_timezone_then_error_is_returned():
  weightings: list[dict] = [
    {
      "start": "2024-12-24T00:00:00",
      "end": "2024-12-24T00:30:00Z",
      "weighting": 1.5
    }
  ]

  result = validate_rate_weightings(weightings)
  assert result.success == False
  assert result.error_message == "start must include timezone at index 0"

@pytest.mark.asyncio
@pytest.mark.parametrize("end",[
  ("A"),
  ("2024-13-01T00:00:00Z"),
  ("2024-12-32T00:00:00Z"),
  ("2024-12-24T24:00:00Z"),
  ("2024-12-24T23:60:00Z"),
  ("2024-12-24T23:00:60Z"),
])
async def test_when_end_is_not_valid_iso_datetime_then_error_is_returned(end: str):
  weightings: list[dict] = [
    {
      "start": "2024-12-24T00:00:00Z",
      "end": end,
      "weighting": 1.5
    }
  ]

  result = validate_rate_weightings(weightings)
  assert result.success == False
  assert result.error_message == "end was not a valid ISO datetime in string format at index 0"

@pytest.mark.asyncio
async def test_when_end_does_not_contain_timezone_then_error_is_returned():
  weightings: list[dict] = [
    {
      "start": "2024-12-24T00:00:00Z",
      "end": "2024-12-24T00:30:00",
      "weighting": 1.5
    }
  ]

  result = validate_rate_weightings(weightings)
  assert result.success == False
  assert result.error_message == "end must include timezone at index 0"

@pytest.mark.asyncio
async def test_when_end_is_before_start_then_error_is_returned():
  weightings: list[dict] = [
    {
      "start": "2024-12-24T00:30:00Z",
      "end": "2024-12-24T00:29:59Z",
      "weighting": 1.5
    }
  ]

  result = validate_rate_weightings(weightings)
  assert result.success == False
  assert result.error_message == "start must be before end at index 0"

@pytest.mark.asyncio
@pytest.mark.parametrize("end",[
  ("2024-12-24T00:29:59Z"),
  ("2024-12-24T00:30:01Z"),
])
async def test_when_time_period_is_not_thirty_minutes_then_error_is_returned(end: str):
  weightings: list[dict] = [
    {
      "start": "2024-12-24T00:00:00Z",
      "end": end,
      "weighting": 1.5
    }
  ]

  result = validate_rate_weightings(weightings)
  assert result.success == False
  assert result.error_message == "time period must be equal to 30 minutes at index 0"

@pytest.mark.asyncio
async def test_when_start_minute_is_not_valid_then_error_is_returned():

  for minute in range(60):
    if minute == 0 or minute == 30:
      continue
    
    weightings: list[dict] = [
      {
        "start": f"2024-12-24T00:{minute:02}:00Z",
        "end": (datetime.strptime("2024-12-24T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") + timedelta(minutes=30 + minute)).isoformat(),
        "weighting": 1.5
      }
    ]

    print(weightings[0]["start"])
    result = validate_rate_weightings(weightings)
    assert result.success == False
    assert result.error_message == "start minute must equal 0 or 30 at index 0"

@pytest.mark.asyncio
@pytest.mark.parametrize("start,end",[
  ("2024-12-24T00:00:01Z", "2024-12-24T00:30:01Z"),
  ("2024-12-24T00:00:00.1Z", "2024-12-24T00:30:00.1Z"),
])
async def test_when_time_period_is_not_thirty_minutes_then_error_is_returned(start: str, end: str):
  weightings: list[dict] = [
    {
      "start": start,
      "end": end,
      "weighting": 1.5
    }
  ]

  result = validate_rate_weightings(weightings)
  assert result.success == False
  assert result.error_message == "start second and microsecond must equal 0 at index 0"

@pytest.mark.asyncio
@pytest.mark.parametrize("start,end", [
  ("2024-12-24T00:00:00Z", "2024-12-24T00:30:00Z"),
  ("2024-12-24T00:30:00Z", "2024-12-24T01:00:00Z"),
])
async def test_when_data_is_valid_then_success_is_returned(start: str, end: str):
  weightings: list[dict] = [
    {
      "start": start,
      "end": end,
      "weighting": 1.5
    }
  ]

  result = validate_rate_weightings(weightings)
  assert result.success == True
  assert len(result.weightings) == 1

  assert result.weightings[0].start == datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
  assert result.weightings[0].end == datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z")
  assert result.weightings[0].weighting == weightings[0]["weighting"]