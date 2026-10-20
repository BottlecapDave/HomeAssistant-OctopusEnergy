from datetime import datetime, timedelta

from custom_components.octopus_energy.intelligent import get_dispatch_hours_for_intelligent_day
from custom_components.octopus_energy.api_client.intelligent_dispatches import SimpleIntelligentDispatchItem

# The intelligent day runs from noon on the day before `current` to noon on `current`'s day
current = datetime.strptime("2025-09-14T09:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
window_start = datetime.strptime("2025-09-13T12:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
window_end = datetime.strptime("2025-09-14T12:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

def test_when_no_dispatches_then_returns_zero_hours():
  # Arrange
  dispatches = []

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  assert result == 0

def test_when_dispatch_is_entirely_before_window_then_it_is_not_counted():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start - timedelta(hours=2),
      end=window_start - timedelta(hours=1)
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  assert result == 0

def test_when_dispatch_ends_exactly_at_window_start_then_it_is_not_counted():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start - timedelta(hours=1),
      end=window_start
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  assert result == 0

def test_when_dispatch_starts_exactly_at_window_end_then_it_is_not_counted():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_end,
      end=window_end + timedelta(hours=1)
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  assert result == 0

def test_when_single_dispatch_aligned_to_half_hours_then_it_returns_its_duration():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8), # 20:00
      end=window_start + timedelta(hours=8, minutes=30) # 20:30
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  assert result == 0.5

def test_when_dispatch_is_not_aligned_to_half_hours_then_it_is_rounded_to_the_nearest_half_hour_slot():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8, minutes=10), # 20:10
      end=window_start + timedelta(hours=8, minutes=20) # 20:20
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  # Rounded down to 20:00 and up to 20:30
  assert result == 0.5

def test_when_dispatch_starts_before_window_but_ends_within_it_then_only_the_portion_within_the_window_is_counted():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start - timedelta(hours=1), # 11:00
      end=window_start + timedelta(hours=1) # 13:00
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  # 12:00 - 13:00. 11:00 - 12:00 belongs to the previous cap period and has already been counted there
  assert result == 1.0

def test_when_dispatches_do_not_overlap_then_hours_are_summed():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8), # 20:00
      end=window_start + timedelta(hours=8, minutes=30) # 20:30
    ),
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=10), # 22:00
      end=window_start + timedelta(hours=11) # 23:00
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  # 0.5 (20:00 - 20:30) + 1.5 (22:00 - 23:00)
  assert result == 1.5

def test_when_dispatches_overlap_then_they_are_merged_and_only_counted_once():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8), # 20:00
      end=window_start + timedelta(hours=8, minutes=30) # 20:30
    ),
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8, minutes=15), # 20:15
      end=window_start + timedelta(hours=8, minutes=45) # 20:45
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  # 20:00 - 21:00 (the second dispatch's end of 20:45 rounds up to 21:00)
  assert result == 1.0

def test_when_dispatch_extends_the_end_of_an_already_merged_dispatch_then_the_extended_duration_is_counted():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8), # 20:00
      end=window_start + timedelta(hours=9) # 21:00
    ),
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8, minutes=30), # 20:30
      end=window_start + timedelta(hours=11, seconds=1) # 23:00:01
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  # 20:00 - 23:30 (23:00 rounded up to the nearest half hour)
  assert result == 3.5

def test_when_dispatch_extends_the_start_of_an_already_merged_dispatch_then_the_extended_duration_is_counted():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=9), # 21:00
      end=window_start + timedelta(hours=10) # 22:00
    ),
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8), # 20:00
      end=window_start + timedelta(hours=9, minutes=30) # 21:30
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  # 20:00 - 22:00
  assert result == 2.0

def test_when_dispatch_is_shorter_than_half_an_hour_then_it_is_rounded_up_to_a_full_half_hour_slot():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8), # 20:00
      end=window_start + timedelta(hours=8, minutes=2) # 20:02
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  assert result == 0.5

def test_when_dispatch_straddles_window_start_then_time_before_noon_is_not_counted_in_either_direction():
  # Arrange
  # A single started dispatch covering 08:30 - 13:30, as reported by Octopus when a charge runs across noon
  previous_window_current = window_start - timedelta(minutes=1) # 11:59, still in the previous cap period
  new_window_current = window_start + timedelta(hours=9, minutes=37) # 21:37, in the new cap period
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start - timedelta(hours=3, minutes=30), # 08:30
      end=window_start + timedelta(hours=1, minutes=30) # 13:30
    )
  ]

  # Act
  previous_window_result = get_dispatch_hours_for_intelligent_day(previous_window_current, dispatches, True)
  new_window_result = get_dispatch_hours_for_intelligent_day(new_window_current, dispatches, True)

  # Assert
  # 08:30 - 12:00 counts against the previous period, 12:00 - 13:30 against the new one
  assert previous_window_result == 3.5
  assert new_window_result == 1.5

def test_when_capped_to_current_and_dispatch_has_not_started_yet_then_it_does_not_reduce_the_total():
  # Arrange
  capped_current = window_start + timedelta(hours=7) # 19:00
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=1), # 13:00
      end=window_start + timedelta(hours=2) # 14:00
    ),
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8), # 20:00
      end=window_start + timedelta(hours=14) # 02:00
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(capped_current, dispatches, True)

  # Assert
  # Only 13:00 - 14:00 has happened by 19:00. The future dispatch must count as zero, not as negative time
  assert result == 1.0

def test_when_dispatches_abut_existing_blocks_on_both_sides_then_each_half_hour_is_counted_once():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=9, minutes=30), # 21:30
      end=window_start + timedelta(hours=10) # 22:00
    ),
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=10, minutes=30), # 22:30
      end=window_start + timedelta(hours=11) # 23:00
    ),
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=10), # 22:00
      end=window_start + timedelta(hours=10, minutes=30) # 22:30
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  # 21:30 - 23:00
  assert result == 1.5

def test_when_a_shorter_dispatch_sits_inside_a_longer_one_then_the_longer_one_is_not_shortened():
  # Arrange
  dispatches = [
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8), # 20:00
      end=window_start + timedelta(hours=11) # 23:00
    ),
    SimpleIntelligentDispatchItem(
      start=window_start + timedelta(hours=8, minutes=30), # 20:30
      end=window_start + timedelta(hours=9) # 21:00
    )
  ]

  # Act
  result = get_dispatch_hours_for_intelligent_day(current, dispatches)

  # Assert
  # 20:00 - 23:00
  assert result == 3.0

def test_when_current_is_utc_during_british_summer_time_then_the_period_still_starts_at_local_noon():
  # Arrange
  import zoneinfo
  from homeassistant.util.dt import (set_default_time_zone, UTC)
  set_default_time_zone(zoneinfo.ZoneInfo("Europe/London"))
  try:
    # 12:15 BST, expressed in UTC as rates from the API are
    bst_current = datetime.strptime("2026-09-28T11:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
    dispatches = [
      # 11:00 - 11:30 BST, which belongs to the previous cap period
      SimpleIntelligentDispatchItem(
        start=datetime.strptime("2026-09-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
        end=datetime.strptime("2026-09-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
      ),
      # 12:00 - 12:30 BST, which belongs to the current cap period
      SimpleIntelligentDispatchItem(
        start=datetime.strptime("2026-09-28T11:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
        end=datetime.strptime("2026-09-28T11:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
      )
    ]

    # Act
    result = get_dispatch_hours_for_intelligent_day(bst_current, dispatches, True)

    # Assert
    # Only 12:00 - 12:15 BST, rounded to a single half hour slot
    assert result == 0.5
  finally:
    set_default_time_zone(UTC)
