from datetime import datetime, timedelta, timezone
from unittest import mock

from custom_components.octopus_energy.coordinators.current_consumption import CurrentConsumptionCoordinatorResult
from custom_components.octopus_energy.diagnostics_entities.electricity_current_consumption_data_last_retrieved import OctopusEnergyElectricityCurrentConsumptionDataLastRetrieved


def test_current_consumption_attributes_report_telemetry_freshness():
  # Arrange
  current = datetime(2026, 8, 29, 10, 30, tzinfo=timezone.utc)
  latest_reading = current - timedelta(minutes=12, seconds=30)
  coordinator = mock.MagicMock()
  coordinator.data = CurrentConsumptionCoordinatorResult(
    current,
    1,
    1,
    [],
    last_retrieved=current - timedelta(minutes=1),
    latest_reading=latest_reading,
    first_missing_at=current - timedelta(minutes=2),
    status="empty",
  )

  entity = OctopusEnergyElectricityCurrentConsumptionDataLastRetrieved(
    mock.MagicMock(),
    coordinator,
    { "serial_number": "test-serial-number", "is_export": False, "is_smart_meter": True, "manufacturer": "test", "model": "test", "firmware": "test" },
    { "mpan": "test-mpan" },
  )
  entity.async_write_ha_state = mock.MagicMock()

  # Act
  entity._handle_coordinator_update()

  # Assert
  attributes = entity.extra_state_attributes
  assert attributes["attempts"] == 1
  assert attributes["status"] == "empty"
  assert attributes["latest_reading"] == latest_reading
  assert attributes["first_missing_at"] == current - timedelta(minutes=2)
  assert "latest_reading_age_in_minutes" not in attributes
