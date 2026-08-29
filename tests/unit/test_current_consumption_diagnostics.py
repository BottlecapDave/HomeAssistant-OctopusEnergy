from datetime import datetime, timedelta, timezone
from unittest import mock

from custom_components.octopus_energy.coordinators.current_consumption import CurrentConsumptionCoordinatorResult
from custom_components.octopus_energy.diagnostics_entities.base import get_current_consumption_attributes


def test_current_consumption_attributes_report_telemetry_freshness():
  current = datetime(2026, 8, 29, 10, 30, tzinfo=timezone.utc)
  latest_reading = current - timedelta(minutes=12, seconds=30)
  result = CurrentConsumptionCoordinatorResult(
    current,
    1,
    1,
    [],
    last_retrieved=current - timedelta(minutes=1),
    latest_reading=latest_reading,
    first_missing_at=current - timedelta(minutes=2),
    status="empty",
  )

  with mock.patch("custom_components.octopus_energy.diagnostics_entities.base.now", return_value=current):
    attributes = get_current_consumption_attributes(result)

  assert attributes == {
    "status": "empty",
    "latest_reading": latest_reading,
    "latest_reading_age_in_minutes": 12.5,
    "first_missing_at": current - timedelta(minutes=2),
  }
