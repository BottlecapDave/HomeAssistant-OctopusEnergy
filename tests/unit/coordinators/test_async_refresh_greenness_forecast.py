import pytest
import mock
from datetime import datetime, timedelta

from custom_components.octopus_energy.const import REFRESH_RATE_IN_MINUTES_GREENNESS_FORECAST
from custom_components.octopus_energy.coordinators.greenness_forecast import GreennessForecastCoordinatorResult, async_refresh_greenness_forecast
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.api_client.greenness_forecast import GreennessForecast

greenness_forecast = [
  GreennessForecast(datetime.strptime(f'2024-02-04T23:00:00Z', "%Y-%m-%dT%H:%M:%S%z"),
                    datetime.strptime(f'2024-02-05T06:00:00Z', "%Y-%m-%dT%H:%M:%S%z"),
                    70,
                    "HIGH",
                    False),
  GreennessForecast(datetime.strptime(f'2024-02-05T23:00:00Z', "%Y-%m-%dT%H:%M:%S%z"),
                    datetime.strptime(f'2024-02-06T06:00:00Z', "%Y-%m-%dT%H:%M:%S%z"),
                    80,
                    "HIGH",
                    True)
]

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_and_previous_data_is_available_then_previous_data_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  current_utc_timestamp = datetime.strptime(f'2024-02-04T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  previous_data = GreennessForecastCoordinatorResult(current_utc_timestamp, 1, greenness_forecast)

  # Act
  result = await async_refresh_greenness_forecast(
    current_utc_timestamp,
    client,
    previous_data
  )

  # Assert
  assert result == previous_data

@pytest.mark.asyncio
async def test_when_results_retrieved_then_results_returned():
  # Arrange
  previous_data = None
    
  current_utc_timestamp = datetime.strptime(f'2024-02-04T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  
  expected_result = greenness_forecast
  mock_api_called = False
  async def async_mocked_get_greenness_forecast(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_result

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_greenness_forecast=async_mocked_get_greenness_forecast): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_greenness_forecast(
      current_utc_timestamp,
      client,
      previous_data
    )

    # Assert
    assert result is not None
    assert result.last_retrieved == current_utc_timestamp
    assert result.next_refresh == current_utc_timestamp + timedelta(minutes=REFRESH_RATE_IN_MINUTES_GREENNESS_FORECAST)
    assert result.forecast == expected_result

    assert mock_api_called == True