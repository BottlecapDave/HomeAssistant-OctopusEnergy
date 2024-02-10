import pytest
from datetime import datetime

from custom_components.octopus_energy.greenness_forecast import greenness_forecast_to_dictionary_list
from custom_components.octopus_energy.api_client.greenness_forecast import GreennessForecast

@pytest.mark.asyncio
async def test_when_forecast_none_then_empty_dictionary_returned():
  # Arrange
  forecast = None

  # Act
  result = greenness_forecast_to_dictionary_list(forecast)

  # Assert
  assert result is not None
  assert len(result) == 0

@pytest.mark.asyncio
async def test_when_forecast_not_none_then_dictionary_list_returned():
  # Arrange
  forecast = GreennessForecast(datetime.strptime("2024-02-02T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                               datetime.strptime("2024-02-03T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                               77,
                               "HIGH",
                               False)

  # Act
  result = greenness_forecast_to_dictionary_list([forecast])

  # Assert
  assert result is not None
  assert len(result) == 1
  
  assert "start" in result[0]
  assert result[0]["start"] == forecast.start
  assert "end" in result[0]
  assert result[0]["end"] == forecast.end
  assert "greenness_index" in result[0]
  assert result[0]["greenness_index"] == forecast.greenness_index
  assert "greenness_score" in result[0]
  assert result[0]["greenness_score"] == forecast.greenness_score
  assert "is_highlighted" in result[0]
  assert result[0]["is_highlighted"] == forecast.highlight_flag