from datetime import datetime, timedelta

from custom_components.octopus_energy.const import (
    CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY,
    CONFIG_MAIN_INTELLIGENT_RATE_MODE_PENDING_AND_STARTED_DISPATCHES,
    INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS
)
from custom_components.octopus_energy.intelligent import get_applicable_dispatches
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatchItem, SimpleIntelligentDispatchItem

def test_when_get_applicable_dispatches_called_with_no_planned_dispatches_it_returns_empty_list():
  # Arrange
  planned_dispatches = None
  started_dispatches = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY

  # Act
  result = get_applicable_dispatches(planned_dispatches, started_dispatches, mode)

  # Assert
  assert result == []

def test_when_get_applicable_dispatches_called_with_no_started_dispatches_and_mode_is_started_only_it_returns_empty_list():
  # Arrange
  now = datetime.now()
  planned_dispatches = [
    IntelligentDispatchItem(
      start=now,
      end=now + timedelta(hours=1),
      charge_in_kwh=1.0,
      source="source",
      location="location"
    )
  ]
  started_dispatches = None
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY

  # Act
  result = get_applicable_dispatches(planned_dispatches, started_dispatches, mode)

  # Assert
  assert result == []

def test_when_get_applicable_dispatches_called_with_started_dispatches_it_returns_them():
  # Arrange
  now = datetime.now()
  planned_dispatches = None
  started_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now,
      end=now + timedelta(hours=1)
    )
  ]
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY

  # Act
  result = get_applicable_dispatches(planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(result) == 1
  assert result[0].start == now
  assert result[0].end == now + timedelta(hours=1)

def test_when_get_applicable_dispatches_called_with_pending_and_started_mode_and_non_smart_charge_dispatch_it_includes_planned_dispatch():
  # Arrange
  now = datetime.now()
  planned_dispatches = [
    IntelligentDispatchItem(
      start=now,
      end=now + timedelta(hours=1),
      charge_in_kwh=1.0,
      source="not-smart-charge",
      location="location"
    )
  ]
  started_dispatches = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PENDING_AND_STARTED_DISPATCHES

  # Act
  result = get_applicable_dispatches(planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(result) == 1
  assert result[0].start == now
  assert result[0].end == now + timedelta(hours=1)

def test_when_get_applicable_dispatches_called_with_pending_and_started_mode_and_smart_charge_dispatch_it_excludes_planned_dispatch():
  # Arrange
  now = datetime.now()
  planned_dispatches = [
    IntelligentDispatchItem(
      start=now,
      end=now + timedelta(hours=1),
      charge_in_kwh=1.0,
      source=INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS[0],
      location="location"
    )
  ]
  started_dispatches = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PENDING_AND_STARTED_DISPATCHES

  # Act
  result = get_applicable_dispatches(planned_dispatches, started_dispatches, mode)

  # Assert
  assert result == []

def test_when_get_applicable_dispatches_called_with_overlapping_dispatches_it_merges_them():
  # Arrange
  now = datetime.now()
  started_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now,
      end=now + timedelta(hours=2)
    ),
    SimpleIntelligentDispatchItem(
      start=now + timedelta(hours=1),
      end=now + timedelta(hours=3)
    )
  ]
  planned_dispatches = None
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY

  # Act
  result = get_applicable_dispatches(planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(result) == 1
  assert result[0].start == now
  assert result[0].end == now + timedelta(hours=3)

def test_when_get_applicable_dispatches_called_with_adjacent_dispatches_it_merges_them():
  # Arrange
  now = datetime.now()
  started_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now,
      end=now + timedelta(hours=1)
    ),
    SimpleIntelligentDispatchItem(
      start=now + timedelta(hours=1),
      end=now + timedelta(hours=2)
    )
  ]
  planned_dispatches = None
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY

  # Act
  result = get_applicable_dispatches(planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(result) == 1
  assert result[0].start == now
  assert result[0].end == now + timedelta(hours=2)

def test_when_get_applicable_dispatches_called_with_multiple_dispatches_it_sorts_them_by_start_time():
  # Arrange
  now = datetime.now()
  started_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now + timedelta(hours=3),
      end=now + timedelta(hours=4)
    ),
    SimpleIntelligentDispatchItem(
      start=now,
      end=now + timedelta(hours=1)
    )
  ]
  planned_dispatches = None
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY

  # Act
  result = get_applicable_dispatches(planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(result) == 2
  assert result[0].start == now
  assert result[0].end == now + timedelta(hours=1)
  assert result[1].start == now + timedelta(hours=3)
  assert result[1].end == now + timedelta(hours=4)

def test_when_get_applicable_dispatches_called_with_both_planned_and_started_it_combines_them_correctly():
  # Arrange
  now = datetime.now()
  planned_dispatches = [
    IntelligentDispatchItem(
      start=now,
      end=now + timedelta(hours=1),
      charge_in_kwh=1.0,
      source="not-smart-charge",
      location="location"
    )
  ]
  started_dispatches = [
    SimpleIntelligentDispatchItem(
      start=now + timedelta(hours=2),
      end=now + timedelta(hours=3)
    )
  ]
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PENDING_AND_STARTED_DISPATCHES

  # Act
  result = get_applicable_dispatches(planned_dispatches, started_dispatches, mode)

  # Assert
  assert len(result) == 2
  assert result[0].start == now
  assert result[0].end == now + timedelta(hours=1)
  assert result[1].start == now + timedelta(hours=2)
  assert result[1].end == now + timedelta(hours=3)

def test_when_get_applicable_dispatches_called_with_source_none_it_excludes_from_planned():
  # Arrange
  now = datetime.now()
  planned_dispatches = [
    IntelligentDispatchItem(
      start=now,
      end=now + timedelta(hours=1),
      charge_in_kwh=1.0,
      source=None,
      location="location"
    )
  ]
  started_dispatches = []
  mode = CONFIG_MAIN_INTELLIGENT_RATE_MODE_PENDING_AND_STARTED_DISPATCHES

  # Act
  result = get_applicable_dispatches(planned_dispatches, started_dispatches, mode)

  # Assert
  # Source as none counts as smart charge and should be excluded
  assert result == []