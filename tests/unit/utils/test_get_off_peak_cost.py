import pytest
from datetime import datetime, timedelta

from custom_components.octopus_energy.utils import get_off_peak_cost
from tests.unit import create_rate_data

@pytest.mark.asyncio
@pytest.mark.parametrize("rates,expected_off_peak_cost",[
  ([1], None),
  ([1, 2], 1),
  ([1, 2, 3], 1),
  ([1, 2, 3, 4], None),
])
async def test_when_correct_number_of_rates_available_then_off_peak_cost_retrieved(rates, expected_off_peak_cost):
  period_from = datetime.strptime("2023-10-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2023-10-15T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2023-10-14T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  rate_data = create_rate_data(period_from, period_to, rates)
  
  # Act
  result = get_off_peak_cost(current, rate_data)

  # Assert
  assert result == expected_off_peak_cost

@pytest.mark.asyncio
async def test_when_rates_spead_over_two_days_then_off_peak_cost_not_retrieved():
  period_from = datetime.strptime("2023-10-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2023-10-14T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  rate_data = create_rate_data(period_from, period_from + timedelta(days=1), [1]) + create_rate_data(period_from + timedelta(days=1), period_from + timedelta(days=2), [2])
  
  # Act
  result = get_off_peak_cost(current, rate_data)

  # Assert
  assert result is None