from custom_components.octopus_energy.intelligent import has_dispatches_changed
import pytest

from datetime import datetime
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatchItem, IntelligentDispatches, SimpleIntelligentDispatchItem


def test_when_nothing_has_changed_then_false_returned():
  # Arrange
  existing_dispatches = IntelligentDispatches(
    current_state="STATE_1",
    completed=[
      SimpleIntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T10:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T11:00:00+01:00")
      )
    ],
    planned=[
      SimpleIntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T12:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T13:00:00+01:00")
      )
    ],
    started=[
      SimpleIntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T09:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T10:00:00+01:00")
      )
    ]
  )
  new_dispatches = IntelligentDispatches(
    current_state="STATE_1",
    completed=[
      SimpleIntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T10:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T11:00:00+01:00")
      )
    ],
    planned=[
      SimpleIntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T12:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T13:00:00+01:00")
      )
    ],
    started=[
      SimpleIntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T09:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T10:00:00+01:00")
      )
    ]
  )

  # Act
  result = has_dispatches_changed(existing_dispatches, new_dispatches)

  # Assert
  assert result is False

def test_when_state_has_changed_then_true_returned():
  # Arrange
  existing_dispatches = IntelligentDispatches(
    current_state="STATE_1",
    completed=[],
    planned=[],
    started=[]
  )
  new_dispatches = IntelligentDispatches(
    current_state="STATE_2",
    completed=[],
    planned=[],
    started=[]
  )

  # Act
  result = has_dispatches_changed(existing_dispatches, new_dispatches)

  # Assert
  assert result is True

def test_when_completed_dispatch_is_different_length_then_true_returned():
  # Arrange
  existing_dispatches = IntelligentDispatches(
    current_state="STATE_1",
    completed=[
      SimpleIntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T10:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T11:00:00+01:00")
      )
    ],
    planned=[],
    started=[]
  )
  new_dispatches = IntelligentDispatches(
    current_state="STATE_1",
    completed=[],
    planned=[],
    started=[]
  )

  # Act
  result = has_dispatches_changed(existing_dispatches, new_dispatches)

  # Assert
  assert result is True

@pytest.mark.parametrize(
  "completed_start_time_changed,completed_end_time_changed,planned_start_time_changed,planned_end_time_changed,started_start_time_changed,started_end_time_changed",
  [
    (True, False, False, False, False, False),
    (False, True, False, False, False, False),
    (False, False, True, False, False, False),
    (False, False, False, True, False, False),
    (False, False, False, False, True, False),
    (False, False, False, False, False, True),
  ]
)
def test_when_dispatch_time_changed_the_true_returned(
    completed_start_time_changed: bool,
    completed_end_time_changed: bool,
    planned_start_time_changed: bool,
    planned_end_time_changed: bool,
    started_start_time_changed: bool,
    started_end_time_changed: bool,
    
  ):
  # Arrange
  existing_dispatches = IntelligentDispatches(
    current_state="STATE_1",
    completed=[
      IntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T12:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T13:00:00+01:00"),
        charge_in_kwh=1.0,
        source="TEST",
        location="location"
      )
    ],
    planned=[
      IntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T12:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T13:00:00+01:00"),
        charge_in_kwh=1.0,
        source="TEST",
        location="location"
      )
    ],
    started=[
      SimpleIntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T12:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T13:00:00+01:00")
      )
    ]
  )
  new_dispatches = IntelligentDispatches(
    current_state="STATE_1",
    completed=[
      IntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T10:00:01+01:00") if completed_start_time_changed else datetime.fromisoformat("2025-09-14T10:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T11:00:01+01:00") if completed_end_time_changed else datetime.fromisoformat("2025-09-14T11:00:00+01:00"),
        charge_in_kwh=1.0,
        source="TEST",
        location="location"
      )
    ],
    planned=[
      IntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T12:00:01+01:00") if planned_start_time_changed else datetime.fromisoformat("2025-09-14T12:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T13:00:01+01:00") if planned_end_time_changed else datetime.fromisoformat("2025-09-14T13:00:00+01:00"),
        charge_in_kwh=1.0,
        source="TEST",
        location="location"
      )
    ],
    started=[
      SimpleIntelligentDispatchItem(
        start=datetime.fromisoformat("2025-09-14T12:00:01+01:00") if started_start_time_changed else datetime.fromisoformat("2025-09-14T12:00:00+01:00"),
        end=datetime.fromisoformat("2025-09-14T13:00:01+01:00") if started_end_time_changed else datetime.fromisoformat("2025-09-14T13:00:00+01:00")
      )
    ]
  )

  # Act
  result = has_dispatches_changed(existing_dispatches, new_dispatches)

  # Assert
  assert result is True