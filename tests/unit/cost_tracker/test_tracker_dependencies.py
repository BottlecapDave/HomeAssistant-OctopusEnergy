from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from homeassistant.components.sensor import RestoreSensor

from custom_components.octopus_energy import sensor as sensor_module
from custom_components.octopus_energy.const import (
  CONFIG_ACCOUNT_ID,
  CONFIG_COST_TRACKER_MPAN,
  CONFIG_COST_TRACKER_NAME,
  CONFIG_COST_TRACKER_TARGET_ENTITY_ID,
  DATA_ACCOUNT,
  DATA_CLIENT,
  DATA_ELECTRICITY_RATES_COORDINATOR_KEY,
  DOMAIN,
)
from custom_components.octopus_energy.cost_tracker.base import get_cost_tracker_unique_id
from custom_components.octopus_energy.cost_tracker.cost_tracker_month import OctopusEnergyCostTrackerMonthSensor
from custom_components.octopus_energy.cost_tracker.cost_tracker_week import OctopusEnergyCostTrackerWeekSensor


@pytest.mark.parametrize(
  ("peak_type", "expected_unique_id"),
  [
    (None, "octopus_energy_cost_tracker_washing_machine"),
    ("peak", "octopus_energy_cost_tracker_washing_machine_peak"),
  ],
)
def test_cost_tracker_unique_id_is_unchanged(peak_type, expected_unique_id):
  assert get_cost_tracker_unique_id("washing_machine", peak_type) == expected_unique_id


@pytest.mark.asyncio
async def test_setup_cost_sensors_passes_daily_unique_ids_to_accumulators():
  account_id = "A-123"
  mpan = "1234567890123"
  serial_number = "S123456"
  config = {
    CONFIG_ACCOUNT_ID: account_id,
    CONFIG_COST_TRACKER_MPAN: mpan,
    CONFIG_COST_TRACKER_NAME: "washing_machine",
    CONFIG_COST_TRACKER_TARGET_ENTITY_ID: None,
  }

  hass = SimpleNamespace(
    data={
      DOMAIN: {
        account_id: {
          DATA_ACCOUNT: SimpleNamespace(
            account={
              "electricity_meter_points": [
                {
                  "mpan": mpan,
                  "agreements": [],
                  "meters": [{"serial_number": serial_number}],
                }
              ]
            }
          ),
          DATA_CLIENT: Mock(),
          DATA_ELECTRICITY_RATES_COORDINATOR_KEY.format(mpan, serial_number): Mock(),
        }
      }
    }
  )

  daily_sensor = SimpleNamespace(
    unique_id="octopus_energy_cost_tracker_washing_machine"
  )
  peak_sensor = SimpleNamespace(
    unique_id="octopus_energy_cost_tracker_washing_machine_peak"
  )

  daily_sensor_class = Mock(side_effect=[daily_sensor, peak_sensor])
  week_sensor_class = Mock()
  month_sensor_class = Mock()
  async_add_entities = Mock()
  entry = Mock()

  with (
    patch.object(sensor_module, "get_active_tariff", return_value=Mock()),
    patch.object(sensor_module.dr, "async_get", return_value=Mock()),
    patch.object(sensor_module.er, "async_get", return_value=Mock()),
    patch.object(sensor_module, "OctopusEnergyCostTrackerSensor", daily_sensor_class),
    patch.object(sensor_module, "OctopusEnergyCostTrackerWeekSensor", week_sensor_class),
    patch.object(sensor_module, "OctopusEnergyCostTrackerMonthSensor", month_sensor_class),
    patch.object(sensor_module, "async_get_meter_debug_override", new=AsyncMock(return_value=None)),
    patch.object(sensor_module, "get_unique_electricity_rates", new=AsyncMock(return_value=1)),
    patch.object(sensor_module, "has_peak_rates", return_value=True),
    patch.object(sensor_module, "get_peak_type", return_value="peak"),
  ):
    await sensor_module.async_setup_cost_sensors(hass, entry, config, async_add_entities)

  assert week_sensor_class.call_args_list == [
    call(hass, entry, config, None, daily_sensor.unique_id),
    call(hass, entry, config, None, peak_sensor.unique_id, "peak"),
  ]
  assert month_sensor_class.call_args_list == [
    call(hass, entry, config, None, daily_sensor.unique_id),
    call(hass, entry, config, None, peak_sensor.unique_id, "peak"),
  ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
  ("sensor_class", "module_name"),
  [
    (
      OctopusEnergyCostTrackerWeekSensor,
      "custom_components.octopus_energy.cost_tracker.cost_tracker_week",
    ),
    (
      OctopusEnergyCostTrackerMonthSensor,
      "custom_components.octopus_energy.cost_tracker.cost_tracker_month",
    ),
  ],
)
async def test_accumulator_resolves_current_entity_id_from_unique_id(sensor_class, module_name):
  tracked_unique_id = "octopus_energy_cost_tracker_washing_machine"
  current_entity_id = "sensor.renamed_washing_machine_cost"
  config = {
    CONFIG_COST_TRACKER_NAME: "washing_machine",
    CONFIG_COST_TRACKER_TARGET_ENTITY_ID: "sensor.washing_machine_energy",
  }

  hass = Mock()
  config_entry = SimpleNamespace(entry_id="entry-id")
  registry = Mock()
  registry.async_get_entity_id.return_value = current_entity_id

  with (
    patch(
      "custom_components.octopus_energy.cost_tracker.base.async_entity_id_to_device",
      return_value=None,
    ),
    patch(f"{module_name}.generate_entity_id", return_value="sensor.accumulator"),
    patch(f"{module_name}.er.async_get", return_value=registry),
    patch.object(RestoreSensor, "async_added_to_hass", new=AsyncMock()),
    patch(f"{module_name}.async_track_state_change_event", return_value=Mock()) as track_state,
    patch(
      f"{module_name}.async_track_entity_registry_updated_event",
      return_value=Mock(),
    ) as track_registry,
  ):
    tracker = sensor_class(hass, config_entry, config, None, tracked_unique_id)
    tracker.async_get_last_state = AsyncMock(return_value=None)
    tracker.async_get_last_sensor_data = AsyncMock(return_value=None)
    tracker.async_on_remove = Mock()

    await tracker.async_added_to_hass()

  registry.async_get_entity_id.assert_called_once_with("sensor", DOMAIN, tracked_unique_id)
  assert tracker._tracked_entity_id == current_entity_id
  assert track_state.call_args.args[1] == [current_entity_id]
  assert track_registry.call_args.args[1] == [current_entity_id]
