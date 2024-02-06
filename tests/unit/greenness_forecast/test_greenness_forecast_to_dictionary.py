import pytest
from datetime import datetime

from custom_components.octopus_energy.greenness_forecast import greenness_forecast_to_dictionary
from custom_components.octopus_energy.api_client.greenness_forecast import GreennessForecast

@pytest.mark.asyncio
async def test_when_forecast_none_then_empty_dictionary_returned():
  # Arrange
  forecast = None

  # Act
  result = greenness_forecast_to_dictionary(forecast)

  # Assert
  assert result == {}

@pytest.mark.asyncio
async def test_when_forecast_not_none_then_dictionary_returned():
  # Arrange
  forecast = GreennessForecast(datetime.strptime("2024-02-02T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                               datetime.strptime("2024-02-03T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                               77,
                               "HIGH",
                               False)

  # Act
  result = greenness_forecast_to_dictionary(forecast)

  # Assert
  assert result is not None
  assert "start" in result
  assert result["start"] == forecast.start
  assert "end" in result
  assert result["end"] == forecast.end
  assert "greenness_index" in result
  assert result["greenness_index"] == forecast.greenness_index
  assert "greenness_score" in result
  assert result["greenness_score"] == forecast.greenness_score
  assert "is_highlighted" in result
  assert result["is_highlighted"] == forecast.highlight_flag