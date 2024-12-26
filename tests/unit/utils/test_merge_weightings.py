from datetime import datetime, timedelta
from decimal import Decimal
import pytest

from custom_components.octopus_energy.utils.weightings import RateWeighting, merge_weightings

def create_weightings(start: datetime, end: datetime, weighting: Decimal):
  weightings = []
  current = start
  while current < end:
    weightings.append(RateWeighting(start=current, end=current + timedelta(minutes=30), weighting=weighting))
    current = current + timedelta(minutes=30)

  return weightings

@pytest.mark.asyncio
async def test_when_new_weightings_is_none_then_current_weightings_returned():
  current_date = datetime.strptime("2024-12-24T10:16:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  new_weightings: list[RateWeighting] = None
  current_weightings: list[RateWeighting] = []

  merged_weightings = merge_weightings(current_date, new_weightings, current_weightings)
  assert merged_weightings == []

@pytest.mark.asyncio
async def test_when_current_weightings_is_none_then_new_weightings_returned():
  current_date = datetime.strptime("2024-12-24T10:16:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  new_weightings: list[RateWeighting] = []
  current_weightings: list[RateWeighting] = None

  merged_weightings = merge_weightings(current_date, new_weightings, current_weightings)
  assert merged_weightings == []

@pytest.mark.asyncio
async def test_when_new_weightings_in_past_then_weightings_returned():
  current_date = datetime.strptime("2024-12-24T10:16:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_weighting = 1.5
  new_weightings: list[RateWeighting] = create_weightings(
    datetime.strptime("2024-12-22T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-12-22T11:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    expected_weighting
  )
  current_weightings: list[RateWeighting] = None

  merged_weightings = merge_weightings(current_date, new_weightings, current_weightings)
  assert merged_weightings == new_weightings

@pytest.mark.asyncio
async def test_when_current_weightings_in_past_then_current_weightings_more_than_24_hours_removed():
  current_date = datetime.strptime("2024-12-24T10:16:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_weighting = 1.5
  new_weightings: list[RateWeighting] = []
  current_weightings: list[RateWeighting] = create_weightings(
    datetime.strptime("2024-12-23T09:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-12-23T11:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    expected_weighting
  )

  merged_weightings = merge_weightings(current_date, new_weightings, current_weightings)
  assert len(current_weightings) == 4
  assert len(merged_weightings) == 2
  
  assert merged_weightings[0].start == datetime.strptime("2024-12-23T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  assert merged_weightings[0].end == datetime.strptime("2024-12-23T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  assert merged_weightings[0].weighting == expected_weighting

  assert merged_weightings[1].start == datetime.strptime("2024-12-23T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  assert merged_weightings[1].end == datetime.strptime("2024-12-23T11:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  assert merged_weightings[1].weighting == expected_weighting

@pytest.mark.asyncio
async def test_when_new_weightings_and_current_weightings_exist_for_same_period_then_new_weighting_wins():
  current_date = datetime.strptime("2024-12-24T10:16:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_weighting = 1.5
  new_weightings: list[RateWeighting] = create_weightings(
    datetime.strptime("2024-12-24T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-12-24T11:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    expected_weighting
  )
  current_weightings: list[RateWeighting] = create_weightings(
    datetime.strptime("2024-12-24T09:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-12-24T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
    expected_weighting + 0.5
  )

  merged_weightings = merge_weightings(current_date, new_weightings, current_weightings)
  assert len(merged_weightings) == 4

  current = datetime.strptime("2024-12-24T09:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  for i in range(len(merged_weightings)):
    assert merged_weightings[i].start == current
    current += timedelta(minutes=30)
    assert merged_weightings[i].end == current

    if merged_weightings[i].start >= datetime.strptime("2024-12-24T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"):
      assert merged_weightings[i].weighting == expected_weighting
    else:
      assert merged_weightings[i].weighting != expected_weighting