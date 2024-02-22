import pytest
import datetime

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.octopus_energy.intelligent import is_in_bump_charge
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatchItem

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

  # During bump charge
  (parse_datetime("2023-06-07T18:00:00Z"), False),
  (parse_datetime("2023-06-07T19:00:00+01:00"), False),
  (parse_datetime("2023-06-07T19:00:00Z"), False),
  (parse_datetime("2023-06-07T20:00:00+01:00"), False),

  (parse_datetime("2023-06-07T15:59:59Z"), False),
  (parse_datetime("2023-06-07T16:59:59+01:00"), False),
  (parse_datetime("2023-06-07T17:00:01Z"), False),
  (parse_datetime("2023-06-07T18:00:01+01:00"), False),
])
async def test_when_dispatch_is_now_then_is_in_bump_charge_returns_correctly(current_date: datetime.datetime, expected_result: bool):
  # Arrange
  dispatches: list[IntelligentDispatchItem] = [
    IntelligentDispatchItem(
      as_utc(parse_datetime("2023-06-07T10:00:00Z")),
      as_utc(parse_datetime("2023-06-07T11:00:00Z")),
      1,
      "bump-charge",
      "home"
    ),
    IntelligentDispatchItem(
      as_utc(parse_datetime("2023-06-07T13:00:00Z")),
      as_utc(parse_datetime("2023-06-07T14:00:00Z")),
      1,
      "bump-charge",
      "home"
    ),
    IntelligentDispatchItem(
      as_utc(parse_datetime("2023-06-07T16:00:00Z")),
      as_utc(parse_datetime("2023-06-07T17:00:00Z")),
      1,
      "bump-charge",
      "home"
    ),
    IntelligentDispatchItem(
      as_utc(parse_datetime("2023-06-07T18:00:00Z")),
      as_utc(parse_datetime("2023-06-07T19:00:00Z")),
      1,
      "smart-charge",
      "home"
    ),
    IntelligentDispatchItem(
      as_utc(parse_datetime("2023-06-07T20:00:00Z")),
      as_utc(parse_datetime("2023-06-07T21:00:00Z")),
      1,
      None,
      "home"
    )
  ]

  # Act
  result = is_in_bump_charge(current_date, dispatches)

  # Assert
  assert result == expected_result