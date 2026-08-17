from datetime import timedelta
import logging
from types import MappingProxyType
from unittest.mock import Mock

import pytest
import pytest_asyncio

from homeassistant.config_entries import ConfigEntries, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.helpers.entity_platform import EntityPlatform

from custom_components.octopus_energy.const import DOMAIN
from custom_components.octopus_energy.diagnostics_entities.electricity_previous_consumption_and_rates_data_last_retrieved import (
  OctopusEnergyElectricityPreviousConsumptionAndRatesDataLastRetrieved,
)
from custom_components.octopus_energy.electricity.current_accumulative_consumption import (
  OctopusEnergyCurrentAccumulativeElectricityConsumption,
)
from custom_components.octopus_energy.electricity.current_rate import (
  OctopusEnergyElectricityCurrentRate,
)
from custom_components.octopus_energy.electricity.off_peak import (
  OctopusEnergyElectricityOffPeak,
)
from custom_components.octopus_energy.electricity.previous_accumulative_cost_override import (
  OctopusEnergyPreviousAccumulativeElectricityCostOverride,
)
from custom_components.octopus_energy.gas.current_accumulative_consumption_kwh import (
  OctopusEnergyCurrentAccumulativeGasConsumptionKwh,
)
from custom_components.octopus_energy.gas.current_rate import OctopusEnergyGasCurrentRate
from custom_components.octopus_energy.gas.current_total_consumption_kwh import (
  OctopusEnergyCurrentTotalGasConsumptionKwh,
)
from custom_components.octopus_energy.octoplus.power_down_baseline import (
  OctopusEnergyPowerDownBaseline,
)


pytestmark = pytest.mark.asyncio

ELECTRICITY_SERIAL = "ELECTRICITYSERIAL"
MPAN = "1234567890123"
GAS_SERIAL = "GASSERIAL"
MPRN = "9876543210"


@pytest_asyncio.fixture
async def hass(tmp_path):
  hass = HomeAssistant(str(tmp_path))
  hass.config_entries = ConfigEntries(hass, {})
  await device_registry.async_load(hass)
  await entity_registry.async_load(hass)

  yield hass

  await hass.async_stop(force=True)


def create_config_entry(hass):
  entry = ConfigEntry(
    data={},
    discovery_keys=MappingProxyType({}),
    domain=DOMAIN,
    minor_version=1,
    options={},
    source="user",
    subentries_data=None,
    title="Octopus Energy",
    unique_id="A-TEST",
    version=1,
  )
  hass.config_entries._entries[entry.entry_id] = entry
  return entry


def create_platform(hass, entry, domain="sensor"):
  platform = EntityPlatform(
    hass=hass,
    logger=logging.getLogger(__name__),
    domain=domain,
    platform_name=DOMAIN,
    platform=None,
    scan_interval=timedelta(seconds=30),
    entity_namespace=None,
  )
  platform.config_entry = entry
  return platform


def create_coordinator():
  coordinator = Mock()
  coordinator.data = None
  coordinator.last_update_success = True
  coordinator.async_add_listener.return_value = lambda: None
  return coordinator


def electricity_meter(is_export=False):
  return {
    "serial_number": ELECTRICITY_SERIAL,
    "is_export": is_export,
    "is_smart_meter": True,
    "manufacturer": "Test Manufacturer",
    "model": "Test Model",
    "firmware": "1.0",
  }


def gas_meter():
  return {
    "serial_number": GAS_SERIAL,
    "is_smart_meter": True,
    "manufacturer": "Test Manufacturer",
    "model": "Test Model",
    "firmware": "1.0",
  }


async def test_new_electricity_entity_uses_device_entity_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyElectricityCurrentRate(
    hass,
    create_coordinator(),
    electricity_meter(),
    {"mpan": MPAN},
    None,
    "A-TEST",
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_electricity_{ELECTRICITY_SERIAL}_{MPAN}_current_rate"
  assert entity.has_entity_name is True
  assert entity.entity_id == f"sensor.octopus_energy_electricity_{ELECTRICITY_SERIAL.lower()}_{MPAN}_current_rate"

  registry_entry = entity_registry.async_get(hass).async_get(entity.entity_id)
  device = device_registry.async_get(hass).async_get(registry_entry.device_id)
  assert device.name == f"Octopus Energy Electricity ({ELECTRICITY_SERIAL}/{MPAN})"
  assert device.identifiers == {(DOMAIN, f"electricity_{ELECTRICITY_SERIAL}_{MPAN}")}


async def test_new_gas_entity_uses_device_entity_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyGasCurrentRate(
    hass,
    create_coordinator(),
    gas_meter(),
    {"mprn": MPRN},
    None,
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_gas_{GAS_SERIAL}_{MPRN}_current_rate"
  assert entity.has_entity_name is True
  assert entity.entity_id == f"sensor.octopus_energy_gas_{GAS_SERIAL.lower()}_{MPRN}_current_rate"

  registry_entry = entity_registry.async_get(hass).async_get(entity.entity_id)
  device = device_registry.async_get(hass).async_get(registry_entry.device_id)
  assert device.name == f"Octopus Energy Gas ({GAS_SERIAL}/{MPRN})"
  assert device.identifiers == {(DOMAIN, f"gas_{GAS_SERIAL}_{MPRN}")}


async def test_existing_registry_entity_id_is_preserved(hass):
  entry = create_config_entry(hass)
  unique_id = f"octopus_energy_electricity_{ELECTRICITY_SERIAL}_{MPAN}_current_rate"
  existing = entity_registry.async_get(hass).async_get_or_create(
    "sensor",
    DOMAIN,
    unique_id,
    calculated_object_id=f"octopus_energy_electricity_{ELECTRICITY_SERIAL.lower()}_{MPAN}_current_rate",
    config_entry=entry,
  )
  entity = OctopusEnergyElectricityCurrentRate(
    hass,
    create_coordinator(),
    electricity_meter(),
    {"mpan": MPAN},
    None,
    "A-TEST",
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == unique_id
  assert entity.entity_id == existing.entity_id


async def test_export_variant_preserves_human_name_order(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyElectricityOffPeak(
    hass,
    create_coordinator(),
    electricity_meter(is_export=True),
    {"mpan": MPAN},
  )

  await create_platform(hass, entry, domain="binary_sensor").async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_electricity_{ELECTRICITY_SERIAL}_{MPAN}_export_off_peak"
  assert entity.has_entity_name is True
  assert entity.name == "Off Peak Export"
  assert entity.entity_id == f"binary_sensor.octopus_energy_electricity_{ELECTRICITY_SERIAL.lower()}_{MPAN}_off_peak_export"

  registry_entry = entity_registry.async_get(hass).async_get(entity.entity_id)
  device = device_registry.async_get(hass).async_get(registry_entry.device_id)
  assert device.name == f"Octopus Energy Electricity ({ELECTRICITY_SERIAL}/{MPAN})"


async def test_meter_diagnostic_uses_preserved_human_name(hass):
  entry = create_config_entry(hass)
  entity = OctopusEnergyElectricityPreviousConsumptionAndRatesDataLastRetrieved(
    hass,
    create_coordinator(),
    electricity_meter(),
    {"mpan": MPAN},
  )

  await create_platform(hass, entry).async_add_entities([entity])

  assert entity.unique_id == f"octopus_energy_electricity_{ELECTRICITY_SERIAL}_{MPAN}_previous_consumption_rates_data_last_retrieved"
  assert entity.has_entity_name is True
  assert entity.name == "Previous Consumption and Rates Data Last Retrieved"
  assert entity.entity_id == f"sensor.octopus_energy_electricity_{ELECTRICITY_SERIAL.lower()}_{MPAN}_previous_consumption_and_rates_data_last_retrieved"

  registry_entry = entity_registry.async_get(hass).async_get(entity.entity_id)
  device = device_registry.async_get(hass).async_get(registry_entry.device_id)
  assert device.name == f"Octopus Energy Electricity ({ELECTRICITY_SERIAL}/{MPAN})"


async def test_meter_entity_names_remove_only_device_context(hass):
  electricity_point = {"mpan": MPAN}
  gas_point = {"mprn": MPRN}

  peak_consumption = OctopusEnergyCurrentAccumulativeElectricityConsumption(
    hass,
    create_coordinator(),
    create_coordinator(),
    create_coordinator(),
    electricity_meter(),
    electricity_point,
    "off_peak",
  )
  tariff_cost = OctopusEnergyPreviousAccumulativeElectricityCostOverride(
    hass,
    "A-TEST",
    create_coordinator(),
    Mock(),
    electricity_meter(),
    electricity_point,
    {"name": "Agile"},
  )
  gas_consumption = OctopusEnergyCurrentAccumulativeGasConsumptionKwh(
    hass,
    create_coordinator(),
    create_coordinator(),
    create_coordinator(),
    gas_meter(),
    gas_point,
    40,
  )
  gas_total = OctopusEnergyCurrentTotalGasConsumptionKwh(
    hass,
    create_coordinator(),
    gas_meter(),
    gas_point,
    40,
  )

  assert peak_consumption.name == "Off Peak Current Accumulative Consumption"
  assert tariff_cost.name == "Agile Previous Accumulative Cost Override"
  assert gas_consumption.name == "Current Accumulative Consumption"
  assert gas_total.name == "Current Total Consumption (kWh)"


async def test_octoplus_baseline_keeps_legacy_entity_id(hass):
  entity = OctopusEnergyPowerDownBaseline(
    hass,
    create_coordinator(),
    create_coordinator(),
    electricity_meter(),
    {"mpan": MPAN},
    False,
  )

  assert entity.unique_id == f"octopus_energy_electricity_{ELECTRICITY_SERIAL}_{MPAN}_octoplus_power_down_baseline"
  assert entity.has_entity_name is False
  assert entity.entity_id == f"sensor.octopus_energy_electricity_{ELECTRICITY_SERIAL.lower()}_{MPAN}_octoplus_power_down_baseline"
