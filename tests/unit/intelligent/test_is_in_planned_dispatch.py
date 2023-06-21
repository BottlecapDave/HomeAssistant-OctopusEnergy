import pytest
import datetime

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.octopus_energy.intelligent import is_in_planned_dispatch

@pytest.mark.asyncio
@pytest.mark.parametrize("current_date,expected_result",[
  (parse_datetime("2023-06-07T10:00:00Z"), True),
  (parse_datetime("2023-06-07T11:00:00+01:00"), True),
  (parse_datetime("2023-06-07T11:00:00Z"), True),
  (parse_datetime("2023-06-07T12:00:00+01:00"), True),

  (parse_datetime("2023-06-07T09:59:59Z"), False),
  (parse_datetime("2023-06-07T10:59:59+01:00"), False),
  (parse_datetime("2023-06-07T12:00:01Z"), False),
  (parse_datetime("2023-06-07T12:00:01+01:00"), False),

  (parse_datetime("2023-06-07T13:00:00Z"), True),
  (parse_datetime("2023-06-07T14:00:00+01:00"), True),
  (parse_datetime("2023-06-07T14:00:00Z"), True),
  (parse_datetime("2023-06-07T15:00:00+01:00"), True),

  (parse_datetime("2023-06-07T12:59:59Z"), False),
  (parse_datetime("2023-06-07T13:59:59+01:00"), False),
  (parse_datetime("2023-06-07T14:00:01Z"), False),
  (parse_datetime("2023-06-07T15:00:01+01:00"), False),

  (parse_datetime("2023-06-07T16:00:00Z"), True),
  (parse_datetime("2023-06-07T17:00:00+01:00"), True),
  (parse_datetime("2023-06-07T17:00:00Z"), True),
  (parse_datetime("2023-06-07T18:00:00+01:00"), True),

  (parse_datetime("2023-06-07T15:59:59Z"), False),
  (parse_datetime("2023-06-07T16:59:59+01:00"), False),
  (parse_datetime("2023-06-07T17:00:01Z"), False),
  (parse_datetime("2023-06-07T18:00:01+01:00"), False),
])
async def test_when_dispatch_is_now_then_is_in_planned_dispatch_returns_correctly(current_date: datetime.datetime, expected_result: bool):
  # Arrange
  dispatches = [
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

  # Act
  result = is_in_planned_dispatch(current_date, dispatches)

  # Assert
  assert result == expected_result