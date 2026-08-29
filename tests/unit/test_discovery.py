from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from custom_components.octopus_energy.discovery import DiscoveryManager


@pytest.mark.asyncio
async def test_discovery_manager_unload_cancels_interval_and_stop_listener():
  cancel_interval = Mock()
  cancel_stop_listener = Mock()
  hass = MagicMock()
  hass.bus.async_listen_once.return_value = cancel_stop_listener
  manager = DiscoveryManager(hass, "A-TEST")
  manager._async_start_discovery = AsyncMock()

  with patch(
    "custom_components.octopus_energy.discovery.async_track_time_interval",
    return_value=cancel_interval,
  ):
    await manager.async_setup()

  manager.async_unload()
  manager.async_unload()

  cancel_interval.assert_called_once()
  cancel_stop_listener.assert_called_once()
