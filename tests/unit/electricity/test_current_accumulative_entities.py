from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
import logging

import pytest

from unit import create_consumption_data, create_rate_data
from custom_components.octopus_energy.electricity import current_accumulative_consumption, current_accumulative_cost
from custom_components.octopus_energy.electricity.current_accumulative_consumption import OctopusEnergyCurrentAccumulativeElectricityConsumption
from custom_components.octopus_energy.electricity.current_accumulative_cost import OctopusEnergyCurrentAccumulativeElectricityCost


def create_entity(entity_class):
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-28T01:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

  hass = MagicMock()
  hass.states.async_entity_ids.return_value = []

  consumption_coordinator = MagicMock()
  consumption_coordinator.data = SimpleNamespace(data=create_consumption_data(period_from, period_to))

  rates_coordinator = MagicMock()
  rates_coordinator.data = SimpleNamespace(rates=create_rate_data(period_from, period_to, [50]))

  standing_charge_coordinator = MagicMock()
  standing_charge_coordinator.data = SimpleNamespace(standing_charge={"value_inc_vat": 10.1})

  entity = entity_class(
    hass,
    consumption_coordinator,
    rates_coordinator,
    standing_charge_coordinator,
    {
      "serial_number": "test-serial-number",
      "is_export": False,
      "is_smart_meter": True,
      "manufacturer": "test-manufacturer",
      "model": "test-model",
      "firmware": "test-firmware",
    },
    {"mpan": "test-mpan"}
  )
  entity.async_write_ha_state = MagicMock()

  return entity, rates_coordinator


@pytest.mark.parametrize("entity_class", [
  OctopusEnergyCurrentAccumulativeElectricityConsumption,
  OctopusEnergyCurrentAccumulativeElectricityCost,
])
def test_when_rate_is_missing_then_repeated_updates_are_suppressed_and_complete_rates_recover(entity_class, caplog):
  # Arrange
  entity, rates_coordinator = create_entity(entity_class)
  entity._handle_coordinator_update()
  previous_value = entity.native_value
  previous_state = entity._state
  previous_last_reset = entity._last_reset
  previous_attributes = entity._attributes

  missing_rate = rates_coordinator.data.rates.pop(1)

  # Act
  with caplog.at_level(logging.WARNING):
    for _ in range(3):
      entity._handle_coordinator_update()

  # Assert
  assert entity.native_value is None
  assert entity._state == previous_state
  assert entity._last_reset == previous_last_reset
  assert entity._attributes == previous_attributes
  warning_records = [record for record in caplog.records if record.levelno == logging.WARNING]
  assert len(warning_records) == 1
  assert str(missing_rate["start"]) in caplog.text
  assert str(missing_rate["end"]) in caplog.text

  rates_coordinator.data.rates.insert(1, missing_rate)
  entity._handle_coordinator_update()

  assert entity.native_value == previous_value
  assert entity._missing_rate_error is None
  assert entity.async_write_ha_state.call_count == 5

  rates_coordinator.data.rates.pop(1)
  with caplog.at_level(logging.WARNING):
    entity._handle_coordinator_update()

  warning_records = [record for record in caplog.records if record.levelno == logging.WARNING]
  assert len(warning_records) == 2


@pytest.mark.parametrize("entity_class, entity_module", [
  (OctopusEnergyCurrentAccumulativeElectricityConsumption, current_accumulative_consumption),
  (OctopusEnergyCurrentAccumulativeElectricityCost, current_accumulative_cost),
])
def test_when_calculation_raises_unexpected_error_then_error_is_not_suppressed(entity_class, entity_module, monkeypatch):
  # Arrange
  entity, _ = create_entity(entity_class)

  def raise_unexpected_error(*args, **kwargs):
    raise RuntimeError("unexpected error")

  monkeypatch.setattr(entity_module, "calculate_electricity_consumption_and_cost", raise_unexpected_error)

  # Act/Assert
  with pytest.raises(RuntimeError, match="unexpected error"):
    entity._handle_coordinator_update()
