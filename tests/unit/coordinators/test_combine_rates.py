from datetime import datetime, timedelta
import pytest

from custom_components.octopus_energy.coordinators import combine_rates
from .. import create_rate_data

@pytest.mark.asyncio
async def test_when_combine_rates_is_called_with_new_rates_is_none_then_none_returned():
  # Arrange
  period_from = datetime.strptime(f'2024-11-19T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime(f'2024-11-20T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  old_rates = create_rate_data(period_from, period_from + timedelta(hours=12), [1, 2])
  new_rates = None

  # Act
  combined_rates = combine_rates(old_rates, new_rates, period_from, period_to)

  # Assert
  assert combined_rates is None

@pytest.mark.asyncio
async def test_when_combine_rates_is_called_with_no_old_rates_then_new_rates_returned():
  # Arrange
  period_from = datetime.strptime(f'2024-11-19T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime(f'2024-11-20T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  expected_new_rate = 2
  old_rates = None
  new_rates = create_rate_data(period_to - timedelta(hours=14), period_to, [expected_new_rate])

  # Act
  combined_rates = combine_rates(old_rates, new_rates, period_from, period_to)

  # Assert
  assert combined_rates is not None

  current_start = period_to - timedelta(hours=14)
  for i in range(28):
    assert combined_rates[i]["start"] == current_start
    current_start += timedelta(minutes=30)
    assert combined_rates[i]["end"] == current_start
    assert combined_rates[i]["value_inc_vat"] == expected_new_rate

@pytest.mark.asyncio
async def test_when_combine_rates_is_called_with_overlapping_rates_then_combined_rates_returned():
  # Arrange
  period_from = datetime.strptime(f'2024-11-19T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime(f'2024-11-20T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  expected_old_rate = 1
  expected_new_rate = 2
  old_rates = create_rate_data(period_from, period_from + timedelta(hours=12), [expected_old_rate])
  new_rates = create_rate_data(period_to - timedelta(hours=14), period_to, [expected_new_rate])

  # Act
  combined_rates = combine_rates(old_rates, new_rates, period_from, period_to)

  # Assert
  assert combined_rates is not None

  current_start = period_from
  for i in range(48):
    assert combined_rates[i]["start"] == current_start
    current_start += timedelta(minutes=30)
    assert combined_rates[i]["end"] == current_start

    if i < 20:
      assert combined_rates[i]["value_inc_vat"] == expected_old_rate
    else:
      assert combined_rates[i]["value_inc_vat"] == expected_new_rate