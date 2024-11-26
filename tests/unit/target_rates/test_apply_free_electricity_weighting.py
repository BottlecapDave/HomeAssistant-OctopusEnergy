from datetime import datetime, timedelta
from decimal import Decimal
import pytest

from custom_components.octopus_energy.target_rates import apply_free_electricity_weighting
from custom_components.octopus_energy.api_client.free_electricity_sessions import FreeElectricitySession
from tests.unit import create_rate_data

period_from = datetime.strptime("2024-11-26T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
period_to = datetime.strptime("2024-11-27T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
async def test_when_applicable_rates_is_none_then_none_is_returned():
  applicable_rates = None
  free_electricity_sessions: list[FreeElectricitySession] = []
  weighting = Decimal(1.5)

  new_applicable_rates = apply_free_electricity_weighting(applicable_rates, free_electricity_sessions, weighting)
  assert new_applicable_rates is None

@pytest.mark.asyncio
async def test_when_free_electricity_sessions_is_none_then_applicable_rates_is_returned():
  applicable_rates = create_rate_data(period_from, period_to, [1, 2])
  free_electricity_sessions: list[FreeElectricitySession] = None
  weighting = Decimal(1.5)

  new_applicable_rates = apply_free_electricity_weighting(applicable_rates, free_electricity_sessions, weighting)
  
  assert new_applicable_rates == applicable_rates
  for rate in new_applicable_rates:
    assert "weighting" not in rate

@pytest.mark.asyncio
async def test_when_free_electricity_sessions_is_available_then_weighting_is_added():
  applicable_rates = create_rate_data(period_from, period_to, [1, 2])

  free_electricity_period_from = datetime.strptime("2024-11-26T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  free_electricity_period_to = datetime.strptime("2024-11-26T11:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  free_electricity_sessions: list[FreeElectricitySession] = [
    FreeElectricitySession("1", free_electricity_period_from, free_electricity_period_to)
  ]
  weighting = Decimal(1.5)

  new_applicable_rates = apply_free_electricity_weighting(applicable_rates, free_electricity_sessions, weighting)
  
  assert new_applicable_rates is not None
  for rate in new_applicable_rates:
    if (rate["start"] == datetime.strptime("2024-11-26T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z") or
        rate["start"] == datetime.strptime("2024-11-26T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z") + timedelta(minutes=30) or
        rate["start"] == datetime.strptime("2024-11-26T10:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z") + timedelta(minutes=60)):
      assert "weighting" in rate
      assert rate["weighting"] == weighting
    else:
      assert "weighting" not in rate