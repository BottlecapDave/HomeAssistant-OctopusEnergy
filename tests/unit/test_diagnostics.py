from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.octopus_energy.api_client.intelligent_device import IntelligentDevice
from custom_components.octopus_energy.diagnostics import async_get_diagnostics


@pytest.mark.asyncio
async def test_diagnostics_redacts_intelligent_device_id():
  client = Mock()
  client.async_get_intelligent_devices = AsyncMock(return_value=[
    IntelligentDevice(
      "device-secret",
      "OCTOPUS",
      "make",
      "model",
      60.0,
      None,
      "ELECTRIC_VEHICLES",
    ),
  ])
  client.async_get_intelligent_settings = AsyncMock(return_value=None)
  client.async_get_heat_pump_ids = AsyncMock(return_value=[])

  result = await async_get_diagnostics(
    client,
    "account-id",
    {
      "id": "account-id",
      "property_ids": [],
      "electricity_meter_points": [],
      "gas_meter_points": [],
    },
    None,
    lambda _redacted_mappings: {},
  )

  assert result["intelligent_devices"] == [{
    "id": "**REDACTED**",
    "provider": "OCTOPUS",
    "make": "make",
    "model": "model",
    "vehicleBatterySizeInKwh": 60.0,
    "chargePointPowerInKw": None,
    "device_type": "ELECTRIC_VEHICLES",
    "settings": None,
  }]
