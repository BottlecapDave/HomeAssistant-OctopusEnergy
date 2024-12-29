from datetime import datetime, timedelta
import pytest

from custom_components.octopus_energy.cost_tracker import add_consumption

def assert_consumption(consumption_data: list, expected_start: datetime, expected_end: datetime, expected_consumption: float):
  assert len(consumption_data) == 1

  assert consumption_data[0]["start"] == expected_start
  assert consumption_data[0]["end"] == expected_end
  assert round(consumption_data[0]["consumption"], 8) == round(expected_consumption, 8)

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_accumulative_value_false_then_new_value_recorded_as_is(is_tracking: bool):
  # Arrange
  current = datetime.strptime("2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  tracked_consumption_data = []
  untracked_consumption_data = []
  new_value = 1.2
  old_value = 1.1
  new_last_reset = None
  old_last_reset = None
  is_accumulative_value = False

  # Act
  result = add_consumption(current,
                           tracked_consumption_data,
                           untracked_consumption_data,
                           new_value,
                           old_value,
                           new_last_reset,
                           old_last_reset,
                           is_accumulative_value,
                           is_tracking)

  # Assert
  assert result is not None

  if is_tracking:
    assert_consumption(result.tracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), new_value)
    assert len(result.untracked_consumption_data) == 0
  else:
    assert len(result.tracked_consumption_data) == 0
    assert_consumption(result.untracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), new_value)

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_accumulative_value_true_and_old_value_none_then_none_returned(is_tracking: bool):
  # Arrange
  current = datetime.strptime("2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  tracked_consumption_data = []
  untracked_consumption_data = []
  new_value = 1.2
  old_value = None
  new_last_reset = None
  old_last_reset = None
  is_accumulative_value = False

  # Act
  result = add_consumption(current,
                           tracked_consumption_data,
                           untracked_consumption_data,
                           new_value,
                           old_value,
                           new_last_reset,
                           old_last_reset,
                           is_accumulative_value,
                           is_tracking)

  # Assert
  assert result is not None

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_accumulative_value_true_and_old_value_not_none_then_new_value_recorded_as_is(is_tracking: bool):
  # Arrange
  current = datetime.strptime("2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  tracked_consumption_data = []
  untracked_consumption_data = []
  new_value = 1.2
  old_value = 1.1
  new_last_reset = None
  old_last_reset = None
  is_accumulative_value = True

  # Act
  result = add_consumption(current,
                           tracked_consumption_data,
                           untracked_consumption_data,
                           new_value,
                           old_value,
                           new_last_reset,
                           old_last_reset,
                           is_accumulative_value,
                           is_tracking)

  # Assert
  assert result is not None

  if is_tracking:
    assert_consumption(result.tracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), 0.1)
    assert len(result.untracked_consumption_data) == 0
  else:
    assert len(result.tracked_consumption_data) == 0
    assert_consumption(result.untracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), 0.1)

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_last_reset_not_changed_then_new_value_recorded_as_is(is_tracking: bool):
  # Arrange
  current = datetime.strptime("2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  tracked_consumption_data = []
  untracked_consumption_data = []
  new_value = 1.2
  old_value = 1.1
  new_last_reset = datetime.strptime("2022-02-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  old_last_reset = datetime.strptime("2022-02-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  is_accumulative_value = True

  # Act
  result = add_consumption(current,
                           tracked_consumption_data,
                           untracked_consumption_data,
                           new_value,
                           old_value,
                           new_last_reset,
                           old_last_reset,
                           is_accumulative_value,
                           is_tracking)

  # Assert
  assert result is not None

  if is_tracking:
    assert_consumption(result.tracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), 0.1)
    assert len(result.untracked_consumption_data) == 0
  else:
    assert len(result.tracked_consumption_data) == 0
    assert_consumption(result.untracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), 0.1)

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_last_reset_changed_then_new_value_recorded_as_is(is_tracking: bool):
  # Arrange
  current = datetime.strptime("2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  tracked_consumption_data = []
  untracked_consumption_data = []
  new_value = 1.2
  old_value = 1.1
  new_last_reset = datetime.strptime("2022-02-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  old_last_reset = datetime.strptime("2022-02-27T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  is_accumulative_value = True

  # Act
  result = add_consumption(current,
                           tracked_consumption_data,
                           untracked_consumption_data,
                           new_value,
                           old_value,
                           new_last_reset,
                           old_last_reset,
                           is_accumulative_value,
                           is_tracking)

  # Assert
  assert result is not None

  if is_tracking:
    assert_consumption(result.tracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), new_value)
    assert len(result.untracked_consumption_data) == 0
  else:
    assert len(result.tracked_consumption_data) == 0
    assert_consumption(result.untracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), new_value)

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_state_class_total_increasing_and_new_value_less_than_old_value_and_greater_than_ten_percent_different_then_new_value_recorded_as_is(is_tracking: bool):
  # Arrange
  current = datetime.strptime("2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  tracked_consumption_data = []
  untracked_consumption_data = []
  new_value = 1.2
  old_value = 1.5
  new_last_reset = datetime.strptime("2022-02-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  old_last_reset = datetime.strptime("2022-02-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  is_accumulative_value = True

  # Act
  result = add_consumption(current,
                           tracked_consumption_data,
                           untracked_consumption_data,
                           new_value,
                           old_value,
                           new_last_reset,
                           old_last_reset,
                           is_accumulative_value,
                           is_tracking,
                           False,
                           "total_increasing")

  # Assert
  assert result is not None

  if is_tracking:
    assert_consumption(result.tracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), new_value)
    assert len(result.untracked_consumption_data) == 0
  else:
    assert len(result.tracked_consumption_data) == 0
    assert_consumption(result.untracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), new_value)

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_state_class_total_increasing_and_new_value_less_than_old_value_and_less_than_ten_percent_different_then_difference_is_recorded(is_tracking: bool):
  # Arrange
  current = datetime.strptime("2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  tracked_consumption_data = []
  untracked_consumption_data = []
  new_value = 1.35
  old_value = 1.5
  expected_value = new_value - old_value
  new_last_reset = datetime.strptime("2022-02-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  old_last_reset = datetime.strptime("2022-02-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  is_accumulative_value = True

  # Act
  result = add_consumption(current,
                           tracked_consumption_data,
                           untracked_consumption_data,
                           new_value,
                           old_value,
                           new_last_reset,
                           old_last_reset,
                           is_accumulative_value,
                           is_tracking,
                           False,
                           "total_increasing")

  # Assert
  assert result is not None

  if is_tracking:
    assert_consumption(result.tracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), expected_value)
    assert len(result.untracked_consumption_data) == 0
  else:
    assert len(result.tracked_consumption_data) == 0
    assert_consumption(result.untracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), expected_value)

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_state_class_total_increasing_and_new_value_greater_than_old_value_then_difference_recorded(is_tracking: bool):
  # Arrange
  current = datetime.strptime("2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  tracked_consumption_data = []
  untracked_consumption_data = []
  new_value = 1.2
  old_value = 1.1
  new_last_reset = datetime.strptime("2022-02-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  old_last_reset = datetime.strptime("2022-02-28T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  is_accumulative_value = True

  # Act
  result = add_consumption(current,
                           tracked_consumption_data,
                           untracked_consumption_data,
                           new_value,
                           old_value,
                           new_last_reset,
                           old_last_reset,
                           is_accumulative_value,
                           is_tracking,
                           False,
                           "total_increasing")

  # Assert
  assert result is not None

  if is_tracking:
    assert_consumption(result.tracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), 0.1)
    assert len(result.untracked_consumption_data) == 0
  else:
    assert len(result.tracked_consumption_data) == 0
    assert_consumption(result.untracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), 0.1)

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_consumption_exists_then_consumption_added_to_existing_consumption(is_tracking: bool):

  for minute in range(0, 59):
    # Arrange
    minuteStr = f"{minute}".rjust(2, "0")
    expected_start = datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z") + timedelta(minutes=0 if minute < 30 else 30)
    expected_end = expected_start + timedelta(minutes=30)

    current = datetime.strptime(f"2022-02-28T10:{minuteStr}:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
    tracked_consumption_data = []
    untracked_consumption_data = []

    if is_tracking:
      tracked_consumption_data.append({
        "start": expected_start,
        "end": expected_end,
        "consumption": 0.2
      })
    else:
      untracked_consumption_data.append({
        "start": expected_start,
        "end": expected_end,
        "consumption": 0.2
      })

    new_value = 1.2
    old_value = 1.1
    new_last_reset = None
    old_last_reset = None
    is_accumulative_value = True

    # Act
    result = add_consumption(current,
                            tracked_consumption_data,
                            untracked_consumption_data,
                            new_value,
                            old_value,
                            new_last_reset,
                            old_last_reset,
                            is_accumulative_value,
                            is_tracking)

    # Assert
    assert result is not None

    if is_tracking:
      assert_consumption(result.tracked_consumption_data, expected_start,  expected_end, 0.3)
      assert len(result.untracked_consumption_data) == 0
    else:
      assert len(result.tracked_consumption_data) == 0
      assert_consumption(result.untracked_consumption_data, expected_start,  expected_end, 0.3)

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_consumption_exists_and_new_day_starts_then_consumption_added_to_new_day(is_tracking: bool):

  # Arrange
  expected_start = datetime.strptime("2022-02-27T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = expected_start + timedelta(minutes=30)

  current = datetime.strptime(f"2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  tracked_consumption_data = []
  untracked_consumption_data = []

  if is_tracking:
    tracked_consumption_data.append({
      "start": expected_start,
      "end": expected_end,
      "consumption": 0.2
    })
  else:
    untracked_consumption_data.append({
      "start": expected_start,
      "end": expected_end,
      "consumption": 0.2
    })

  new_value = 1.2
  old_value = 1.1
  new_last_reset = None
  old_last_reset = None
  is_accumulative_value = True

  # Act
  result = add_consumption(current,
                          tracked_consumption_data,
                          untracked_consumption_data,
                          new_value,
                          old_value,
                          new_last_reset,
                          old_last_reset,
                          is_accumulative_value,
                          is_tracking)

  # Assert
  assert result is not None

  if is_tracking:
    assert_consumption(result.tracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), 0.1)
    assert len(result.untracked_consumption_data) == 0
  else:
    assert len(result.tracked_consumption_data) == 0
    assert_consumption(result.untracked_consumption_data, datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-02-28T10:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z"), 0.1)

@pytest.mark.asyncio
@pytest.mark.parametrize("is_tracking", [(True),(False)])
async def test_when_consumption_exists_and_new_day_starts_and_manual_reset_is_enabled_then_consumption_added_to_existing_day(is_tracking: bool):

  # Arrange
  existing_start = datetime.strptime("2022-02-27T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  existing_end = existing_start + timedelta(minutes=30)

  current = datetime.strptime(f"2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_start = datetime.strptime("2022-02-28T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_end = expected_start + timedelta(minutes=30)

  tracked_consumption_data = []
  untracked_consumption_data = []

  if is_tracking:
    tracked_consumption_data.append({
      "start": existing_start,
      "end": existing_end,
      "consumption": 0.2
    })
  else:
    untracked_consumption_data.append({
      "start": existing_start,
      "end": existing_end,
      "consumption": 0.2
    })

  new_value = 1.2
  old_value = 1.1
  new_last_reset = None
  old_last_reset = None
  is_accumulative_value = True

  # Act
  result = add_consumption(current,
                          tracked_consumption_data,
                          untracked_consumption_data,
                          new_value,
                          old_value,
                          new_last_reset,
                          old_last_reset,
                          is_accumulative_value,
                          is_tracking,
                          is_manual_reset_enabled=True)

  # Assert
  assert result is not None

  if is_tracking:
    assert len(result.untracked_consumption_data) == 0

    assert len(result.tracked_consumption_data) == 2
    assert result.tracked_consumption_data[0]["start"] == tracked_consumption_data[0]["start"]
    assert result.tracked_consumption_data[0]["end"] == tracked_consumption_data[0]["end"]
    assert round(result.tracked_consumption_data[0]["consumption"], 8) == round(tracked_consumption_data[0]["consumption"], 8)

    assert result.tracked_consumption_data[1]["start"] == expected_start
    assert result.tracked_consumption_data[1]["end"] == expected_end
    assert round(result.tracked_consumption_data[1]["consumption"], 8) == round(0.1, 8)
  else:
    assert len(result.tracked_consumption_data) == 0
    
    assert len(result.untracked_consumption_data) == 2
    assert result.untracked_consumption_data[0]["start"] == untracked_consumption_data[0]["start"]
    assert result.untracked_consumption_data[0]["end"] == untracked_consumption_data[0]["end"]
    assert round(result.untracked_consumption_data[0]["consumption"], 8) == round(untracked_consumption_data[0]["consumption"], 8)

    assert result.untracked_consumption_data[1]["start"] == expected_start
    assert result.untracked_consumption_data[1]["end"] == expected_end
    assert round(result.untracked_consumption_data[1]["consumption"], 8) == round(0.1, 8)

@pytest.mark.asyncio
@pytest.mark.parametrize("new_value,old_value", [(None, None),
                                                 (0, None),
                                                 (None, 0),
                                                 (0, 0)
                                                 ])
async def test_when_mean_cannot_be_calculated_then_none_is_returned(new_value: float, old_value: float):
  # Arrange
  current = datetime.strptime("2022-02-28T10:15:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  tracked_consumption_data = []
  untracked_consumption_data = []
  new_last_reset = None
  old_last_reset = None
  is_accumulative_value = False

  # Act
  result = add_consumption(current,
                           tracked_consumption_data,
                           untracked_consumption_data,
                           new_value,
                           old_value,
                           new_last_reset,
                           old_last_reset,
                           is_accumulative_value,
                           True)

  # Assert
  assert result is None