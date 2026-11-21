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


def test_when_rate_is_missing_then_consumption_continues_to_be_reported():
  # Arrange
  entity, rates_coordinator = create_entity(OctopusEnergyCurrentAccumulativeElectricityConsumption)
  entity._handle_coordinator_update()
  expected_consumption = entity.native_value

  rates_coordinator.data.rates.pop(1)

  # Act
  entity._handle_coordinator_update()

  # Assert
  assert expected_consumption is not None
  assert entity.native_value == expected_consumption
  assert "error" not in entity._attributes


def test_when_rate_is_missing_then_cost_is_none_with_error_and_recovers(caplog):
  # Arrange
  entity, rates_coordinator = create_entity(OctopusEnergyCurrentAccumulativeElectricityCost)
  entity._handle_coordinator_update()
  expected_cost = entity.native_value

  missing_rate = rates_coordinator.data.rates.pop(1)

  # Act
  with caplog.at_level(logging.WARNING):
    for _ in range(3):
      entity._handle_coordinator_update()

  # Assert
  assert entity.native_value is None
  assert str(missing_rate["start"]) in entity._attributes["error"]
  assert [record for record in caplog.records if record.levelno >= logging.WARNING] == []

  rates_coordinator.data.rates.insert(1, missing_rate)
  entity._handle_coordinator_update()

  assert entity.native_value == expected_cost
  assert "error" not in entity._attributes


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
