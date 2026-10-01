from unittest import mock
import pytest

from custom_components.octopus_energy.const import DATA_WHEEL_OF_FORTUNE_SPINS_FORCE_UPDATE, DOMAIN
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.wheel_of_fortune.electricity_spins import OctopusEnergyWheelOfFortuneElectricitySpins
from custom_components.octopus_energy.wheel_of_fortune.gas_spins import OctopusEnergyWheelOfFortuneGasSpins

account_id = "ABC123"

def create_sensor(sensor_type, client: OctopusEnergyApiClient, coordinator):
  hass = mock.Mock()
  hass.data = { DOMAIN: { account_id: {} } }

  sensor = sensor_type(hass, coordinator, client, account_id)
  sensor.hass = hass
  return sensor

@pytest.mark.asyncio
@pytest.mark.parametrize("sensor_type,expected_is_electricity", [
  (OctopusEnergyWheelOfFortuneElectricitySpins, True),
  (OctopusEnergyWheelOfFortuneGasSpins, False),
])
async def test_when_wheel_is_spun_then_prize_is_returned_and_spins_are_refreshed(sensor_type, expected_is_electricity: bool):
  # Arrange
  requested_args = None
  async def async_mocked_spin_wheel_of_fortune(*args, **kwargs):
    nonlocal requested_args
    requested_args = args
    return 8

  with mock.patch.multiple(OctopusEnergyApiClient, async_spin_wheel_of_fortune=async_mocked_spin_wheel_of_fortune):
    client = OctopusEnergyApiClient("NOT_REAL")
    coordinator = mock.Mock()
    coordinator.async_refresh = mock.AsyncMock()
    sensor = create_sensor(sensor_type, client, coordinator)

    # Act
    result = await sensor.async_spin_wheel()

    # Assert
    assert result == { "prize_value": 8 }
    assert requested_args == (client, account_id, expected_is_electricity)
    assert sensor.hass.data[DOMAIN][account_id][DATA_WHEEL_OF_FORTUNE_SPINS_FORCE_UPDATE] == True
    coordinator.async_refresh.assert_awaited_once()

@pytest.mark.asyncio
@pytest.mark.parametrize("sensor_type", [
  (OctopusEnergyWheelOfFortuneElectricitySpins),
  (OctopusEnergyWheelOfFortuneGasSpins),
])
async def test_when_wheel_is_spun_and_refresh_fails_then_prize_is_still_returned(sensor_type):
  # Arrange
  async def async_mocked_spin_wheel_of_fortune(*args, **kwargs):
    return 8

  with mock.patch.multiple(OctopusEnergyApiClient, async_spin_wheel_of_fortune=async_mocked_spin_wheel_of_fortune):
    client = OctopusEnergyApiClient("NOT_REAL")
    coordinator = mock.Mock()
    coordinator.async_refresh = mock.AsyncMock(side_effect=ValueError("foo"))
    sensor = create_sensor(sensor_type, client, coordinator)

    # Act
    result = await sensor.async_spin_wheel()

    # Assert
    assert result == { "prize_value": 8 }
    coordinator.async_refresh.assert_awaited_once()

@pytest.mark.asyncio
@pytest.mark.parametrize("sensor_type", [
  (OctopusEnergyWheelOfFortuneElectricitySpins),
  (OctopusEnergyWheelOfFortuneGasSpins),
])
async def test_when_spin_fails_then_exception_is_raised_and_spins_are_not_refreshed(sensor_type):
  # Arrange
  raised_exception = RequestException("foo", [])
  async def async_mocked_spin_wheel_of_fortune(*args, **kwargs):
    raise raised_exception

  with mock.patch.multiple(OctopusEnergyApiClient, async_spin_wheel_of_fortune=async_mocked_spin_wheel_of_fortune):
    client = OctopusEnergyApiClient("NOT_REAL")
    coordinator = mock.Mock()
    coordinator.async_refresh = mock.AsyncMock()
    sensor = create_sensor(sensor_type, client, coordinator)

    # Act
    with pytest.raises(RequestException):
      await sensor.async_spin_wheel()

    # Assert
    assert DATA_WHEEL_OF_FORTUNE_SPINS_FORCE_UPDATE not in sensor.hass.data[DOMAIN][account_id]
    coordinator.async_refresh.assert_not_awaited()
