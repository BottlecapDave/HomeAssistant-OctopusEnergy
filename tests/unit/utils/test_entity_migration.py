import mock

from homeassistant.core import valid_entity_id

from custom_components.octopus_energy.utils.entity_migration import async_migrate_unique_ids
from custom_components.octopus_energy.const import DOMAIN

def test_when_new_unique_id_contains_hyphens_then_new_entity_id_is_valid():
  # Arrange - a real charge point id is a hyphenated UUID; the constructed
  # entity_id must be slugified (hyphens -> underscores), not just lowercased,
  # or registry.async_update_entity raises and the migration silently fails.
  old_unique_id = "octopus_energy_charge_point_00000000-0000-0000-0000-000000000000_boost_switch"
  new_unique_id = "octopus_energy_charge_point_00000000-0000-0000-0000-000000000000_boost"

  registry = mock.Mock()
  registry.async_get_entity_id = mock.Mock(return_value="switch.old_entity_id")

  hass = mock.Mock()

  with mock.patch("custom_components.octopus_energy.utils.entity_migration.er.async_get", return_value=registry):
    # Act
    async_migrate_unique_ids(hass, "switch", [{ "old": old_unique_id, "new": new_unique_id }])

  # Assert
  registry.async_get_entity_id.assert_called_once_with("switch", DOMAIN, old_unique_id)
  assert registry.async_update_entity.call_count == 1
  call_args = registry.async_update_entity.call_args
  assert call_args.args == ("switch.old_entity_id",)
  new_entity_id = call_args.kwargs["new_entity_id"]
  assert valid_entity_id(new_entity_id), f"{new_entity_id} is not a valid entity_id"
  assert call_args.kwargs["new_unique_id"] == new_unique_id

def test_when_no_existing_entity_then_nothing_migrated():
  # Arrange
  registry = mock.Mock()
  registry.async_get_entity_id = mock.Mock(return_value=None)
  hass = mock.Mock()

  with mock.patch("custom_components.octopus_energy.utils.entity_migration.er.async_get", return_value=registry):
    # Act
    async_migrate_unique_ids(hass, "switch", [{ "old": "old_id", "new": "new_id" }])

  # Assert
  registry.async_update_entity.assert_not_called()

def test_when_update_entity_raises_then_error_is_caught():
  # Arrange
  registry = mock.Mock()
  registry.async_get_entity_id = mock.Mock(return_value="switch.old_entity_id")
  registry.async_update_entity = mock.Mock(side_effect=ValueError("boom"))
  hass = mock.Mock()

  with mock.patch("custom_components.octopus_energy.utils.entity_migration.er.async_get", return_value=registry):
    # Act/Assert - should not raise
    async_migrate_unique_ids(hass, "switch", [{ "old": "old_id", "new": "new_id" }])
