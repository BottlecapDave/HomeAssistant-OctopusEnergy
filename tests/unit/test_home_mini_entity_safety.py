from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from custom_components.octopus_energy.electricity.current_demand import OctopusEnergyCurrentElectricityDemand
from custom_components.octopus_energy.electricity.current_total_consumption import OctopusEnergyCurrentTotalElectricityConsumption
from custom_components.octopus_energy.electricity.current_total_export import OctopusEnergyCurrentTotalElectricityExport
from custom_components.octopus_energy.gas.current_total_consumption_cubic_meters import OctopusEnergyCurrentTotalGasConsumptionCubicMeters
from custom_components.octopus_energy.gas.current_total_consumption_kwh import OctopusEnergyCurrentTotalGasConsumptionKwh


def _set_coordinator_data(entity, data):
  entity.coordinator = SimpleNamespace(data=SimpleNamespace(data=data))
  entity._attributes = {}


def _set_electricity_meter(entity):
  entity._mpan = "123"
  entity._serial_number = "abc"
  entity._is_export = False
  entity._is_smart_meter = True


def _set_gas_meter(entity):
  entity._mprn = "123"
  entity._serial_number = "abc"
  entity._is_smart_meter = True
  entity._calorific_value = 40


def test_when_current_demand_data_is_empty_then_previous_state_is_preserved():
  entity = object.__new__(OctopusEnergyCurrentElectricityDemand)
  _set_coordinator_data(entity, [])
  entity._state = 100

  with patch("homeassistant.helpers.update_coordinator.CoordinatorEntity._handle_coordinator_update"):
    entity._handle_coordinator_update()

  assert entity.native_value == 100


def test_when_latest_total_consumption_is_zero_then_electricity_state_is_unknown():
  entity = object.__new__(OctopusEnergyCurrentTotalElectricityConsumption)
  _set_coordinator_data(entity, [
    { "end": datetime(2026, 8, 1, 2), "total_consumption": None },
    { "end": datetime(2026, 8, 1, 0), "total_consumption": 10 },
    { "end": datetime(2026, 8, 1, 1), "total_consumption": 0 },
  ])
  _set_electricity_meter(entity)
  entity._state = 10
  entity._last_reset = None

  with patch("homeassistant.helpers.update_coordinator.CoordinatorEntity._handle_coordinator_update"):
    entity._handle_coordinator_update()

  assert entity.native_value is None


def test_when_latest_export_is_null_then_newest_non_null_export_is_used():
  entity = object.__new__(OctopusEnergyCurrentTotalElectricityExport)
  _set_coordinator_data(entity, [
    { "end": datetime(2026, 8, 1, 2), "total_export": None },
    { "end": datetime(2026, 8, 1, 0), "total_export": 5 },
    { "end": datetime(2026, 8, 1, 1), "total_export": 7 },
  ])
  _set_electricity_meter(entity)
  entity._state = None
  entity._last_reset = None

  with patch("homeassistant.helpers.update_coordinator.CoordinatorEntity._handle_coordinator_update"):
    entity._handle_coordinator_update()

  assert entity.native_value == 7


def test_when_latest_gas_total_is_null_then_newest_non_null_total_is_used_for_kwh():
  entity = object.__new__(OctopusEnergyCurrentTotalGasConsumptionKwh)
  _set_coordinator_data(entity, [
    { "end": datetime(2026, 8, 1, 2), "total_consumption": None, "is_kwh": True },
    { "end": datetime(2026, 8, 1, 0), "total_consumption": 5, "is_kwh": True },
    { "end": datetime(2026, 8, 1, 1), "total_consumption": 7, "is_kwh": True },
  ])
  _set_gas_meter(entity)
  entity._state = None

  with patch("homeassistant.helpers.update_coordinator.CoordinatorEntity._handle_coordinator_update"):
    entity._handle_coordinator_update()

  assert entity.native_value == 7


def test_when_latest_gas_total_is_zero_then_cubic_meter_state_is_unknown():
  entity = object.__new__(OctopusEnergyCurrentTotalGasConsumptionCubicMeters)
  _set_coordinator_data(entity, [
    { "end": datetime(2026, 8, 1, 0), "total_consumption": 5, "is_kwh": False },
    { "end": datetime(2026, 8, 1, 1), "total_consumption": 0, "is_kwh": False },
  ])
  _set_gas_meter(entity)
  entity._state = 5

  with patch("homeassistant.helpers.update_coordinator.CoordinatorEntity._handle_coordinator_update"):
    entity._handle_coordinator_update()

  assert entity.native_value is None
