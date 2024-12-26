from datetime import datetime, timedelta
from custom_components.octopus_energy.const import (
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST,
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST,
  CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS
)
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.target_rates import get_target_rate_info, should_evaluate_target_rates

@pytest.mark.asyncio
@pytest.mark.parametrize("evaluation_mode",[
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST),
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST),
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS),
])
async def test_when_target_rates_is_none_then_return_true(evaluation_mode: str):
  # Arrange
  current_date = datetime.strptime("2024-09-21T10:15:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_rates = None

  # Act
  result = should_evaluate_target_rates(current_date, target_rates, evaluation_mode)

  # Assert
  assert result == True

@pytest.mark.asyncio
@pytest.mark.parametrize("evaluation_mode",[
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST),
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST),
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS),
])
async def test_when_target_rates_is_empty_then_return_true(evaluation_mode: str):
  # Arrange
  current_date = datetime.strptime("2024-09-21T10:15:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_rates = []

  # Act
  result = should_evaluate_target_rates(current_date, target_rates, evaluation_mode)

  # Assert
  assert result == True

@pytest.mark.asyncio
@pytest.mark.parametrize("evaluation_mode,expected_result",[
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST, False),
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST, True),
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS, True),
])
async def test_when_target_rates_is_in_the_future_then_return_expected_result(evaluation_mode: str, expected_result: bool):
  # Arrange
  current_date = datetime.strptime("2024-09-21T10:15:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_rates = create_rate_data(
    datetime.strptime("2024-09-21T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-09-21T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    [0.1]
  )

  # Act
  result = should_evaluate_target_rates(current_date, target_rates, evaluation_mode)

  # Assert
  assert result == expected_result

@pytest.mark.asyncio
@pytest.mark.parametrize("evaluation_mode,expected_result",[
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST, False),
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST, False),
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS, True),
])
async def test_when_target_rates_started_then_return_expected_result(evaluation_mode: str, expected_result: bool):
  # Arrange
  current_date = datetime.strptime("2024-09-21T10:15:00Z", "%Y-%m-%dT%H:%M:%S%z")
  target_rates = create_rate_data(
    datetime.strptime("2024-09-21T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-09-21T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    [0.1]
  )

  # Act
  result = should_evaluate_target_rates(current_date, target_rates, evaluation_mode)

  # Assert
  assert result == expected_result

@pytest.mark.asyncio
@pytest.mark.parametrize("evaluation_mode,expected_result",[
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_PAST, True),
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALL_IN_FUTURE_OR_PAST, True),
  (CONFIG_TARGET_TARGET_TIMES_EVALUATION_MODE_ALWAYS, True),
])
async def test_when_target_rates_in_past_then_return_expected_result(evaluation_mode: str, expected_result: bool):
  # Arrange
  current_date = datetime.strptime("2024-09-21T11:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  target_rates = create_rate_data(
    datetime.strptime("2024-09-21T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2024-09-21T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    [0.1]
  )

  # Act
  result = should_evaluate_target_rates(current_date, target_rates, evaluation_mode)

  # Assert
  assert result == expected_result