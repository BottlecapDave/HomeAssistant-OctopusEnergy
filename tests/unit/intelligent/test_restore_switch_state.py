import mock
import pytest

from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import State
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.octopus_energy.api_client.intelligent_device import IntelligentDevice
from custom_components.octopus_energy.const import INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS
from custom_components.octopus_energy.intelligent.bump_charge import OctopusEnergyIntelligentBumpCharge
from custom_components.octopus_energy.intelligent.smart_charge import OctopusEnergyIntelligentSmartCharge

def create_device():
  return IntelligentDevice(
    "device-id",
    "MYENERGI",
    "Myenergi",
    "Zappi smart EV",
    None,
    6.5,
    INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS
  )

@pytest.mark.asyncio
@pytest.mark.parametrize("entity_class", [OctopusEnergyIntelligentSmartCharge, OctopusEnergyIntelligentBumpCharge])
@pytest.mark.parametrize("last_state,expected_is_on", [
  (STATE_ON, True),
  (STATE_OFF, False),
  (STATE_UNAVAILABLE, False),
  (STATE_UNKNOWN, False),
  (None, False),
])
async def test_when_restored_then_is_on_reflects_last_state(entity_class, last_state, expected_is_on):
  # Arrange
  hass = mock.MagicMock()
  hass.states.async_available.return_value = True
  entity = entity_class(hass, mock.MagicMock(), mock.MagicMock(), create_device(), "A-123", False)
  restored_state = State(entity.entity_id, last_state) if last_state is not None else None
  entity.async_get_last_state = mock.AsyncMock(return_value=restored_state)

  # Act
  with mock.patch.object(CoordinatorEntity, "async_added_to_hass", mock.AsyncMock()):
    await entity.async_added_to_hass()

  # Assert
  assert entity.is_on is expected_is_on
