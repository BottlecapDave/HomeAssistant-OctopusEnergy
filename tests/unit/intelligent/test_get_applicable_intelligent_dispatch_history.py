from datetime import datetime
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatchItem, IntelligentDispatches
from custom_components.octopus_energy.intelligent import get_applicable_intelligent_dispatch_history
from custom_components.octopus_energy.storage.intelligent_dispatches_history import IntelligentDispatchesHistory, IntelligentDispatchesHistoryItem

def test_when_history_is_none_then_none_returned():
  # Arrange
  point_in_time = datetime.fromisoformat("2025-10-01T12:00:00+00:00")
  history = None

  # Act
  result = get_applicable_intelligent_dispatch_history(history, point_in_time)

  # Assert
  assert result is None

def test_when_history_is_empty_then_none_returned():
  # Arrange
  point_in_time = datetime.fromisoformat("2025-10-01T12:00:00+00:00")
  history = IntelligentDispatchesHistory([])

  # Act
  result = get_applicable_intelligent_dispatch_history(history, point_in_time)

  # Assert
  assert result is None

def test_when_history_is_not_available_for_point_in_time_then_none_returned():
  # Arrange
  point_in_time = datetime.fromisoformat("2025-10-01T12:00:00+00:00")
  history = IntelligentDispatchesHistory([
    IntelligentDispatchesHistoryItem(
      datetime.fromisoformat("2025-10-01T12:00:01+00:00"),
      IntelligentDispatches(
        "TEST_STATE",
        [],
        [],
        []
      )
    ),
  ])

  # Act
  result = get_applicable_intelligent_dispatch_history(history, point_in_time)

  # Assert
  assert result is None

def test_when_history_is_available_for_point_in_time_then_latest_dispatch_returned():
  # Arrange
  point_in_time = datetime.fromisoformat("2025-10-01T12:00:00+00:00")
  history = IntelligentDispatchesHistory([
    IntelligentDispatchesHistoryItem(
      datetime.fromisoformat("2025-10-01T10:00:01+00:00"),
      IntelligentDispatches(
        "TEST_STATE_1",
        [],
        [],
        []
      )
    ),
    IntelligentDispatchesHistoryItem(
      datetime.fromisoformat("2025-10-01T11:00:01+00:00"),
      IntelligentDispatches(
        "TEST_STATE_2",
        [],
        [],
        []
      )
    ),
    IntelligentDispatchesHistoryItem(
      datetime.fromisoformat("2025-10-01T12:00:01+00:00"),
      IntelligentDispatches(
        "TEST_STATE_3",
        [],
        [],
        []
      )
    ),
  ])

  # Act
  result = get_applicable_intelligent_dispatch_history(history, point_in_time)

  # Assert
  assert result is not None
  assert result == history.history[1]