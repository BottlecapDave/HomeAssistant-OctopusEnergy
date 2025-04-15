import pytest
import mock
from datetime import datetime, timedelta

from custom_components.octopus_energy.const import REFRESH_RATE_IN_MINUTES_OCTOPLUS_WHEEL_OF_FORTUNE
from custom_components.octopus_energy.coordinators.wheel_of_fortune import WheelOfFortuneSpinsCoordinatorResult, async_refresh_wheel_of_fortune_spins
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.wheel_of_fortune import WheelOfFortuneSpinsResponse

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_and_previous_data_is_available_then_previous_data_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  account_id = "ABC123"
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  previous_data = WheelOfFortuneSpinsCoordinatorResult(current_utc_timestamp, 1, WheelOfFortuneSpinsResponse(1, 2))

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
async def test_when_results_retrieved_then_results_returned():
  # Arrange
  account_id = "ABC123"
  previous_data = None
    
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  
  expected_result = WheelOfFortuneSpinsResponse(1, 2)
  mock_api_called = False
  async def async_mocked_get_wheel_of_fortune_spins(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
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
    assert result.last_evaluated == current_utc_timestamp
    assert result.next_refresh == current_utc_timestamp.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_OCTOPLUS_WHEEL_OF_FORTUNE)
    assert result.spins == expected_result

    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_exception_raised_then_previous_result_returned_and_exception_captured():
  # Arrange
  account_id = "ABC123"
    
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  previous_data = WheelOfFortuneSpinsCoordinatorResult(current_utc_timestamp - timedelta(days=1), 1, WheelOfFortuneSpinsResponse(1, 2))
  
  mock_api_called = False
  raised_exception = RequestException("foo", [])
  async def async_mocked_get_wheel_of_fortune_spins(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    raise raised_exception

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
    assert result.spins == previous_data.spins
    assert result.last_evaluated == previous_data.last_evaluated
    assert result.request_attempts == previous_data.request_attempts + 1
    assert result.next_refresh == previous_data.next_refresh + timedelta(minutes=1)
    assert result.last_error == raised_exception

    assert mock_api_called == True