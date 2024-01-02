from datetime import (datetime)
import pytest

from custom_components.octopus_energy.utils import is_off_peak
from tests.unit import create_rate_data

@pytest.mark.asyncio
async def test_when_off_peak_not_available_then_false_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-01T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2022-02-01T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  
  rate_data = create_rate_data(period_from, period_to, [10, 20, 30, 40, 40])

  # Act
  assert is_off_peak(current, rate_data) == False

@pytest.mark.asyncio
async def test_when_off_peak_available_and_current_not_off_peak_then_false_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-01T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2022-02-01T01:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  
  rate_data = create_rate_data(period_from, period_to, [10, 10, 30, 30])

  # Act
  assert is_off_peak(current, rate_data) == False

@pytest.mark.asyncio
async def test_when_off_peak_available_and_current_off_peak_then_true_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-01T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2022-02-01T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  
  rate_data = create_rate_data(period_from, period_to, [10, 10, 30, 30])

  # Act
  assert is_off_peak(current, rate_data) == True

@pytest.mark.asyncio
async def test_when_off_peak_available_and_current_off_peak_and_intelligent_adjusted_then_false_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-01T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2022-02-01T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  
  rate_data = create_rate_data(period_from, period_to, [10, 10, 30, 30])
  for rate in rate_data:
    rate["is_intelligent_adjusted"] = True

  # Act
  assert is_off_peak(current, rate_data) == False