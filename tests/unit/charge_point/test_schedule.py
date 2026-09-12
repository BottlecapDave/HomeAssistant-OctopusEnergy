from datetime import datetime

import pytest

from custom_components.octopus_energy.charge_point.schedule import compute_next_schedule_transition

@pytest.mark.asyncio
async def test_when_a_period_starts_later_today_then_that_is_the_next_transition():
  # Arrange - Monday 10:00, with a period from 18:00-19:00 later today
  now = datetime(2026, 8, 31, 10, 0, 0)  # a Monday
  schedule_by_day = {
    "MONDAY": [{ "start": "18:00", "end": "19:00", "action": "ON" }],
  }

  # Act
  result = compute_next_schedule_transition(schedule_by_day, now)

  # Assert - the start (18:00) is the next boundary, not the end (19:00)
  assert result == datetime(2026, 8, 31, 18, 0, 0)

@pytest.mark.asyncio
async def test_when_currently_inside_a_period_then_its_end_is_the_next_transition():
  # Arrange - Monday 18:30, mid-way through an 18:00-19:00 period
  now = datetime(2026, 8, 31, 18, 30, 0)
  schedule_by_day = {
    "MONDAY": [{ "start": "18:00", "end": "19:00", "action": "ON" }],
  }

  # Act
  result = compute_next_schedule_transition(schedule_by_day, now)

  # Assert - the start has already passed, so the end (19:00) is next
  assert result == datetime(2026, 8, 31, 19, 0, 0)

@pytest.mark.asyncio
async def test_when_todays_periods_have_all_passed_then_next_day_with_a_period_is_used():
  # Arrange - Monday 20:00 (after the only period today), next period is Wednesday
  now = datetime(2026, 8, 31, 20, 0, 0)  # a Monday
  schedule_by_day = {
    "MONDAY": [{ "start": "18:00", "end": "19:00", "action": "ON" }],
    "WEDNESDAY": [{ "start": "07:00", "end": "08:00", "action": "ON" }],
  }

  # Act
  result = compute_next_schedule_transition(schedule_by_day, now)

  # Assert
  assert result == datetime(2026, 9, 2, 7, 0, 0)  # the following Wednesday

@pytest.mark.asyncio
async def test_when_no_periods_are_scheduled_then_none_is_returned():
  # Arrange
  now = datetime(2026, 8, 31, 10, 0, 0)
  schedule_by_day = {}

  # Act
  result = compute_next_schedule_transition(schedule_by_day, now)

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_only_next_week_has_a_period_then_that_is_found():
  # Arrange - a Monday, only a single period exists next Monday
  now = datetime(2026, 8, 31, 20, 0, 0)  # a Monday, after any today's periods
  schedule_by_day = {
    "MONDAY": [{ "start": "07:00", "end": "08:00", "action": "ON" }],
  }

  # Act
  result = compute_next_schedule_transition(schedule_by_day, now)

  # Assert - wraps around to next Monday's start
  assert result == datetime(2026, 9, 7, 7, 0, 0)
