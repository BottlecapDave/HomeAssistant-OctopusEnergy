from custom_components.octopus_energy.const import EVENT_ALL_SAVING_SESSIONS, EVENT_NEW_SAVING_SESSION
import pytest
import mock
from datetime import datetime, timedelta

from custom_components.octopus_energy.coordinators.wheel_of_fortune import WheelOfFortuneSpinsCoordinatorResult, async_refresh_wheel_of_fortune_spins
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.api_client.wheel_of_fortune import WheelOfFortuneSpinsResponse

@pytest.mark.asyncio
async def test_when_now_is_not_at_30_minute_mark_and_previous_data_is_available_then_previous_data_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  account_id = "ABC123"
  previous_data = WheelOfFortuneSpinsCoordinatorResult(datetime.now(), WheelOfFortuneSpinsResponse(1, 2))

  for minute in range(0, 59):
    if (minute == 0 or minute == 30):
      continue
    
    minuteStr = f'{minute}'.zfill(2)
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minuteStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

    # Act
    result = await async_refresh_wheel_of_fortune_spins(
      current_utc_timestamp,
      client,
      account_id,
      previous_data
    )

    # Assert
    assert result == previous_data

@pytest.mark.asyncio
@pytest.mark.parametrize("minutes",[
  (0),
  (30),
])
async def test_when_results_retrieved_then_results_returned(minutes):
  # Arrange
  account_id = "ABC123"
  previous_data = None
    
  minutesStr = f'{minutes}'.zfill(2)
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")
  
  expected_result = WheelOfFortuneSpinsResponse(1, 2)
  async def async_mocked_get_wheel_of_fortune_spins(*args, **kwargs):
    return expected_result

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_wheel_of_fortune_spins=async_mocked_get_wheel_of_fortune_spins): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_wheel_of_fortune_spins(
      current_utc_timestamp,
      client,
      account_id,
      previous_data
    )

    # Assert
    assert result is not None
    assert result.last_retrieved == current_utc_timestamp
    assert result.spins == expected_result