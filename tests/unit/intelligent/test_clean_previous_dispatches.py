import pytest

from homeassistant.util.dt import (as_utc, parse_datetime)

from custom_components.octopus_energy.intelligent import clean_previous_dispatches

@pytest.mark.asyncio
async def test_when_clean_previous_dispatches_called_then_old_dispatches_removed():
  # Arrange
  old_dispatches = [
    {
      "start": as_utc(parse_datetime("2023-06-04T10:00:00Z")),
      "end": as_utc(parse_datetime("2023-06-04T11:00:00Z")),
    },
    {
      "start": as_utc(parse_datetime("2023-06-05T13:00:00Z")),
      "end": as_utc(parse_datetime("2023-06-05T14:00:00Z")),
    },
    {
      "start": as_utc(parse_datetime("2023-06-05T16:00:00Z")),
      "end": as_utc(parse_datetime("2023-06-05T17:00:00Z")),
    }
  ]

  new_dispatches = [
    {
      "start": as_utc(parse_datetime("2023-06-07T10:00:00Z")),
      "end": as_utc(parse_datetime("2023-06-07T11:00:00Z")),
    },
    {
      "start": as_utc(parse_datetime("2023-06-07T13:00:00Z")),
      "end": as_utc(parse_datetime("2023-06-07T14:00:00Z")),
    },
    {
      "start": as_utc(parse_datetime("2023-06-07T16:00:00Z")),
      "end": as_utc(parse_datetime("2023-06-07T17:00:00Z")),
    }
  ]

  current_date = parse_datetime("2023-06-07T10:00:00Z")
  min_date = parse_datetime("2023-06-05T00:00:00Z")

  # Act

  result = clean_previous_dispatches(current_date, old_dispatches + new_dispatches)

  ## Assert
  assert result is not None
  assert len(result) == 5

  for dispatch in result:
    assert dispatch["start"] >= min_date