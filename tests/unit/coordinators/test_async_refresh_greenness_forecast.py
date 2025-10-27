import pytest
import mock
from datetime import datetime, timedelta

from custom_components.octopus_energy.const import REFRESH_RATE_IN_MINUTES_GREENNESS_FORECAST
from custom_components.octopus_energy.coordinators.greenness_forecast import GreennessForecastCoordinatorResult, async_refresh_greenness_forecast
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
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
  async def async_mocked_get_greener_nights_forecast(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return expected_result

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_greener_nights_forecast=async_mocked_get_greener_nights_forecast): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_greenness_forecast(
      current_utc_timestamp,
      client,
      previous_data
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp
    assert result.next_refresh == current_utc_timestamp.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_GREENNESS_FORECAST)
    assert result.forecast == expected_result

    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_exception_raised_then_existing_results_returned_and_exception_captured():
  # Arrange
  current_utc_timestamp = datetime.strptime(f'2024-02-04T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  previous_data = GreennessForecastCoordinatorResult(current_utc_timestamp - timedelta(days=1), 1, greenness_forecast)
  
  mock_api_called = False
  raised_exception = RequestException("My exception", [])
  async def async_mocked_get_greener_nights_forecast(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    raise raised_exception

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_greener_nights_forecast=async_mocked_get_greener_nights_forecast): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_greenness_forecast(
      current_utc_timestamp,
      client,
      previous_data
    )

    # Assert
    assert mock_api_called == True

    assert result is not None
    assert result.last_evaluated == previous_data.last_evaluated
    assert result.last_error == raised_exception
    assert result.forecast == previous_data.forecast
    assert result.request_attempts == previous_data.request_attempts + 1
    assert result.next_refresh == previous_data.next_refresh + timedelta(minutes=1)
