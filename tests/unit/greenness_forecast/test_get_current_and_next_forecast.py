import pytest
from datetime import datetime

from custom_components.octopus_energy.greenness_forecast import get_current_and_next_forecast
from custom_components.octopus_energy.api_client.greenness_forecast import GreennessForecast

forecast: list[GreennessForecast] = [
  GreennessForecast(datetime.strptime("2024-02-02T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                    datetime.strptime("2024-02-03T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                    77,
                    "HIGH",
                    False),
  GreennessForecast(datetime.strptime("2024-02-03T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                    datetime.strptime("2024-02-04T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                    77,
                    "HIGH",
                    True),
  GreennessForecast(datetime.strptime("2024-02-04T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                  datetime.strptime("2024-02-05T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                  60,
                  "HIGH",
                  False),
  GreennessForecast(datetime.strptime("2024-02-05T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                  datetime.strptime("2024-02-06T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
                  77,
                  "HIGH",
                  True)
]

@pytest.mark.asyncio
async def test_when_forecast_none_then_none_returned():
  # Arrange
  current = datetime.strptime("2024-02-02T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  restrict_highlighted = False

  # Act
  result = get_current_and_next_forecast(current, None, restrict_highlighted)

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_current_not_available_then_current_none():
  # Arrange
  current = datetime.strptime("2024-02-02T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  restrict_highlighted = False

  # Act
  result = get_current_and_next_forecast(current, forecast, restrict_highlighted)

  # Assert
  assert result is not None

  assert result.current is None

  assert result.next == forecast[0]

@pytest.mark.asyncio
async def test_when_next_not_available_then_next_none():
  # Arrange
  current = datetime.strptime("2024-02-06T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  restrict_highlighted = False

  # Act
  result = get_current_and_next_forecast(current, forecast, restrict_highlighted)

  # Assert
  assert result is not None

  assert result.current == forecast[3]

  assert result.next is None

@pytest.mark.asyncio
@pytest.mark.parametrize("current_highlighted",[
  (True),
  (False)
])
async def test_when_restrict_highlighted_then_nonhighlighed_ignored(current_highlighted: bool):
  # Arrange
  current = datetime.strptime("2024-02-04T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z") if current_highlighted else datetime.strptime("2024-02-03T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  restrict_highlighted = True

  # Act
  result = get_current_and_next_forecast(current, forecast, restrict_highlighted)

  # Assert
  assert result is not None

  if current_highlighted:
    assert result.current == forecast[1]
    assert result.next == forecast[3]
  else:
    assert result.current is None
    assert result.next == forecast[1]
