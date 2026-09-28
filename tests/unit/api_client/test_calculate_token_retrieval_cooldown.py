from datetime import timedelta
import pytest

from custom_components.octopus_energy.api_client import (
  MAXIMUM_TOKEN_RETRIEVAL_COOLDOWN_IN_MINUTES,
  MINIMUM_TOKEN_RETRIEVAL_COOLDOWN_IN_MINUTES,
  calculate_token_retrieval_cooldown
)

@pytest.mark.parametrize("failure_count",[-1, 0])
def test_when_no_failures_have_occurred_then_no_cooldown_is_returned(failure_count: int):
  # Act
  result = calculate_token_retrieval_cooldown(failure_count)

  # Assert
  assert result == timedelta(minutes=0)

def test_when_one_failure_has_occurred_then_minimum_cooldown_is_returned():
  # Act
  result = calculate_token_retrieval_cooldown(1)

  # Assert
  assert result == timedelta(minutes=MINIMUM_TOKEN_RETRIEVAL_COOLDOWN_IN_MINUTES)

@pytest.mark.parametrize("failure_count,expected_minutes",[
  (1, 1),
  (2, 2),
  (3, 4),
  (4, 8),
  (5, 16),
])
def test_when_failures_have_occurred_then_cooldown_doubles(failure_count: int, expected_minutes: int):
  # Act
  result = calculate_token_retrieval_cooldown(failure_count)

  # Assert
  assert result == timedelta(minutes=expected_minutes)

@pytest.mark.parametrize("failure_count",[6, 10, 100])
def test_when_many_failures_have_occurred_then_cooldown_is_capped(failure_count: int):
  # Act
  result = calculate_token_retrieval_cooldown(failure_count)

  # Assert
  assert result == timedelta(minutes=MAXIMUM_TOKEN_RETRIEVAL_COOLDOWN_IN_MINUTES)
