from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from unit import create_consumption_data
from custom_components.octopus_energy.coordinators.previous_consumption_and_rates import extract_missing_consumption_periods
from custom_components.octopus_energy.octoplus import OctoplusSessionConsumptionDate


def period_for_day(day):
  # Matches how async_enhance_with_historic_consumption builds its local day periods
  local_start = datetime.fromisoformat(day).replace(tzinfo=ZoneInfo('Europe/London'))
  return OctoplusSessionConsumptionDate(local_start, local_start + timedelta(hours=24))


def consumption_for_period(period: OctoplusSessionConsumptionDate):
  return create_consumption_data(period.start.astimezone(timezone.utc), period.end.astimezone(timezone.utc))


@pytest.mark.parametrize('day, expected_count', [
  ('2026-03-28', 48),
  ('2026-03-29', 46),
  ('2026-07-01', 48),
  ('2026-10-25', 50),
  ('2026-10-26', 48),
])
def test_complete_local_day_is_not_missing(day, expected_count):
  period = period_for_day(day)
  consumption = consumption_for_period(period)
  assert len(consumption) == expected_count

  assert extract_missing_consumption_periods([period], consumption) == []


@pytest.mark.parametrize('day', ['2026-03-29', '2026-07-01', '2026-10-25'])
def test_local_day_missing_a_half_hour_is_missing(day):
  period = period_for_day(day)
  consumption = consumption_for_period(period)[:-1]

  assert extract_missing_consumption_periods([period], consumption) == [period]


def test_autumn_day_with_only_48_readings_is_missing():
  period = period_for_day('2026-10-25')
  consumption = consumption_for_period(period)[:-2]
  assert len(consumption) == 48

  assert extract_missing_consumption_periods([period], consumption) == [period]


def test_only_incomplete_days_are_missing():
  spring_period = period_for_day('2026-03-29')
  autumn_period = period_for_day('2026-10-25')
  consumption = consumption_for_period(spring_period) + consumption_for_period(autumn_period)[1:]

  assert extract_missing_consumption_periods([spring_period, autumn_period], consumption) == [autumn_period]
