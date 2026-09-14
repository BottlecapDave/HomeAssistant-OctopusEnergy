import mock
import pytest

from custom_components.octopus_energy import _async_get_device_by_identifier


def test_async_get_device_by_identifier_uses_modern_method():
  registry = mock.MagicMock()
  registry.async_get_device_by_identifier = mock.MagicMock(return_value="mock_device")
  registry.async_get_device = mock.MagicMock()

  result = _async_get_device_by_identifier(
    registry,
    ("octopus_energy", "electricity_12345_67890"),
    "config_entry_abc",
  )

  assert result == "mock_device"
  registry.async_get_device_by_identifier.assert_called_once_with(
    ("octopus_energy", "electricity_12345_67890"),
    "config_entry_abc",
  )
  registry.async_get_device.assert_not_called()


def test_async_get_device_by_identifier_falls_back_when_missing_method():
  # Legacy device registry without async_get_device_by_identifier attribute
  registry = mock.MagicMock(spec=["async_get_device"])
  registry.async_get_device.return_value = "legacy_device"

  result = _async_get_device_by_identifier(
    registry,
    ("octopus_energy", "gas_12345_67890"),
    "config_entry_abc",
  )

  assert result == "legacy_device"
  registry.async_get_device.assert_called_once_with(
    identifiers={("octopus_energy", "gas_12345_67890")}
  )


def test_async_get_device_by_identifier_falls_back_when_no_entry_id():
  registry = mock.MagicMock()
  registry.async_get_device_by_identifier = mock.MagicMock()
  registry.async_get_device = mock.MagicMock(return_value="fallback_device")

  result = _async_get_device_by_identifier(
    registry,
    ("octopus_energy", "gas_12345_67890"),
    None,
  )

  assert result == "fallback_device"
  registry.async_get_device.assert_called_once_with(
    identifiers={("octopus_energy", "gas_12345_67890")}
  )
  registry.async_get_device_by_identifier.assert_not_called()
