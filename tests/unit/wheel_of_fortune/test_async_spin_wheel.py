from unittest import mock
import pytest

from custom_components.octopus_energy.const import DATA_WHEEL_OF_FORTUNE_SPINS_FORCE_UPDATE, DOMAIN
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.wheel_of_fortune.electricity_spins import OctopusEnergyWheelOfFortuneElectricitySpins
from custom_components.octopus_energy.wheel_of_fortune.gas_spins import OctopusEnergyWheelOfFortuneGasSpins

account_id = "ABC123"

@pytest.mark.asyncio
@pytest.mark.parametrize("sensor_type,expected_is_electricity,prize_value,refresh_error", [
  (OctopusEnergyWheelOfFortuneElectricitySpins, True, 8, None),
  (OctopusEnergyWheelOfFortuneGasSpins, False, None, None),
  (OctopusEnergyWheelOfFortuneElectricitySpins, True, 8, ValueError("foo")),
])
async def test_when_wheel_is_spun_then_prize_is_returned_and_spins_are_refreshed(sensor_type, expected_is_electricity: bool, prize_value, refresh_error):
  # Arrange
  requested_args = None
  async def async_mocked_spin_wheel_of_fortune(*args, **kwargs):
    nonlocal requested_args
    requested_args = args
    return prize_value

  with mock.patch.multiple(OctopusEnergyApiClient, async_spin_wheel_of_fortune=async_mocked_spin_wheel_of_fortune):
    client = OctopusEnergyApiClient("NOT_REAL")
    coordinator = mock.Mock()
    coordinator.async_refresh = mock.AsyncMock(side_effect=refresh_error)
    hass = mock.Mock()
    hass.data = { DOMAIN: { account_id: {} } }
    sensor = sensor_type(hass, coordinator, client, account_id)
    sensor.hass = hass

    # Act
    result = await sensor.async_spin_wheel()

    # Assert
    assert result == { "prize_value": prize_value }
    assert requested_args == (client, account_id, expected_is_electricity)
    assert hass.data[DOMAIN][account_id][DATA_WHEEL_OF_FORTUNE_SPINS_FORCE_UPDATE] == True
    coordinator.async_refresh.assert_awaited_once()
