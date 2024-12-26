from datetime import datetime, timedelta
from decimal import Decimal
import pytest

from tests.unit import create_rate_data
from custom_components.octopus_energy.utils.weightings import RateWeighting, apply_weighting

period_from = datetime.strptime("2024-11-26T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
period_to = datetime.strptime("2024-11-27T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
async def test_when_applicable_rates_is_none_then_none_is_returned():
  applicable_rates = None
  rate_weightings: list[RateWeighting] = []

  new_applicable_rates = apply_weighting(applicable_rates, rate_weightings)
  assert new_applicable_rates is None

@pytest.mark.asyncio
async def test_when_rate_weightings_is_none_then_applicable_rates_is_returned():
  applicable_rates = create_rate_data(period_from, period_to, [1, 2])
  rate_weightings: list[RateWeighting] = None

  new_applicable_rates = apply_weighting(applicable_rates, rate_weightings)
  
  assert new_applicable_rates == applicable_rates
  for rate in new_applicable_rates:
    assert "weighting" not in rate

@pytest.mark.asyncio
async def test_when_rate_weightings_is_available_then_weighting_is_added():
  applicable_rates = create_rate_data(period_from, period_to, [1, 2])

  free_electricity_period_from = datetime.strptime("2024-11-26T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  free_electricity_period_to = datetime.strptime("2024-11-26T11:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_weighting = Decimal(1.5)
  rate_weightings: list[RateWeighting] = [
    RateWeighting(start=free_electricity_period_from, end=free_electricity_period_to, weighting=expected_weighting)
  ]

  new_applicable_rates = apply_weighting(applicable_rates, rate_weightings)
  
  assert new_applicable_rates is not None
  for rate in new_applicable_rates:
    if (rate["start"] == datetime.strptime("2024-11-26T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z") or
        rate["start"] == datetime.strptime("2024-11-26T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z") + timedelta(minutes=30) or
        rate["start"] == datetime.strptime("2024-11-26T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z") + timedelta(minutes=60)):
      assert "weighting" in rate
      assert rate["weighting"] == expected_weighting
    else:
      assert "weighting" not in rate