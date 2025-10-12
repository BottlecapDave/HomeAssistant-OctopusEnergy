from datetime import datetime, timedelta

from custom_components.octopus_energy.intelligent import get_current_and_next_dispatching_periods
from custom_components.octopus_energy.api_client.intelligent_dispatches import SimpleIntelligentDispatchItem

now = datetime.strptime("2025-09-14T10:40:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

def test_when_get_current_and_next_dispatching_periods_called_and_dispatches_empty_then_current_and_next_dispatch_is_none():
  # Arrange
  applicable_dispatches = []

  # Act
  (current_dispatch, next_dispatch) = get_current_and_next_dispatching_periods(now, applicable_dispatches)

  # Assert
  assert current_dispatch is None
  assert next_dispatch is None

def test_when_get_current_and_next_dispatching_periods_called_and_dispatches_is_none_then_current_and_next_dispatch_is_none():
  # Arrange
  applicable_dispatches = None

  # Act
  (current_dispatch, next_dispatch) = get_current_and_next_dispatching_periods(now, applicable_dispatches)

  # Assert
  assert current_dispatch is None
  assert next_dispatch is None

def test_when_get_current_and_next_dispatching_periods_called_with_current_time_inside_dispatch_then_current_is_set_and_next_is_none():
  # Arrange
  applicable_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now - timedelta(hours=1),
      end=now + timedelta(hours=1)
    )
  ]

  # Act
  (current_dispatch, next_dispatch) = get_current_and_next_dispatching_periods(now, applicable_dispatches)

  # Assert
  assert current_dispatch is not None
  assert current_dispatch.start == applicable_dispatches[0].start
  assert current_dispatch.end == applicable_dispatches[0].end
  assert next_dispatch is None

def test_when_get_current_and_next_dispatching_periods_called_with_current_time_before_dispatch_then_current_is_none_and_next_is_set():
  # Arrange
  applicable_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now + timedelta(hours=1),
      end=now + timedelta(hours=2)
    )
  ]

  # Act
  (current_dispatch, next_dispatch) = get_current_and_next_dispatching_periods(now, applicable_dispatches)

  # Assert
  assert current_dispatch is None
  assert next_dispatch is not None
  assert next_dispatch.start == applicable_dispatches[0].start
  assert next_dispatch.end == applicable_dispatches[0].end

def test_when_get_current_and_next_dispatching_periods_called_with_current_time_after_all_dispatches_then_current_and_next_are_none():
  # Arrange
  applicable_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now - timedelta(hours=2),
      end=now - timedelta(hours=1)
    )
  ]

  # Act
  (current_dispatch, next_dispatch) = get_current_and_next_dispatching_periods(now, applicable_dispatches)

  # Assert
  assert current_dispatch is None
  assert next_dispatch is None

def test_when_get_current_and_next_dispatching_periods_called_with_multiple_dispatches_and_current_and_next_dispatch_is_set():
  # Arrange
  applicable_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now - timedelta(hours=1),
      end=now + timedelta(hours=1)
    ),
    SimpleIntelligentDispatchItem(
      start=now + timedelta(hours=2),
      end=now + timedelta(hours=3)
    ),
    SimpleIntelligentDispatchItem(
      start=now + timedelta(hours=4),
      end=now + timedelta(hours=5)
    )
  ]

  # Act
  (current_dispatch, next_dispatch) = get_current_and_next_dispatching_periods(now, applicable_dispatches)

  # Assert
  assert current_dispatch is not None
  assert current_dispatch.start == applicable_dispatches[0].start
  assert current_dispatch.end == applicable_dispatches[0].end
  assert next_dispatch is not None
  assert next_dispatch.start == applicable_dispatches[1].start
  assert next_dispatch.end == applicable_dispatches[1].end

def test_when_get_current_and_next_dispatching_periods_called_with_multiple_dispatches_and_current_between_them_then_current_is_none_and_next_is_next_upcoming():
  # Arrange
  applicable_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now - timedelta(hours=3),
      end=now - timedelta(hours=2)
    ),
    SimpleIntelligentDispatchItem(
      start=now + timedelta(hours=1),
      end=now + timedelta(hours=2)
    ),
    SimpleIntelligentDispatchItem(
      start=now + timedelta(hours=3),
      end=now + timedelta(hours=4)
    )
  ]

  # Act
  (current_dispatch, next_dispatch) = get_current_and_next_dispatching_periods(now, applicable_dispatches)

  # Assert
  assert current_dispatch is None
  assert next_dispatch is not None
  assert next_dispatch.start == applicable_dispatches[1].start
  assert next_dispatch.end == applicable_dispatches[1].end

def test_when_get_current_and_next_dispatching_periods_called_with_current_time_exactly_at_start_then_current_is_set():
  # Arrange
  applicable_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now,
      end=now + timedelta(hours=1)
    )
  ]

  # Act
  (current_dispatch, next_dispatch) = get_current_and_next_dispatching_periods(now, applicable_dispatches)

  # Assert
  assert current_dispatch is not None
  assert current_dispatch.start == applicable_dispatches[0].start
  assert current_dispatch.end == applicable_dispatches[0].end
  assert next_dispatch is None

def test_when_get_current_and_next_dispatching_periods_called_with_current_time_exactly_at_end_then_current_is_not_set():
  # Arrange
  end_time = now
  applicable_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now - timedelta(hours=1),
      end=end_time
    )
  ]

  # Act
  (current_dispatch, next_dispatch) = get_current_and_next_dispatching_periods(end_time, applicable_dispatches)

  # Assert
  assert current_dispatch is None
  assert next_dispatch is None