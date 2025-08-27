import pytest
from datetime import datetime
from homeassistant.util.dt import (as_utc, parse_datetime)

from custom_components.octopus_energy.greenness_forecast import get_current_and_next_forecast
from custom_components.octopus_energy.api_client.greenness_forecast import GreennessForecast

forecast: list[GreennessForecast] = [
  GreennessForecast(as_utc(parse_datetime("2025-03-30T23:00:00+00:00")),
                    as_utc(parse_datetime("2025-03-31T05:00:00+00:00")),
                    77,
                    "HIGH",
                    False),
  GreennessForecast(as_utc(parse_datetime("2025-03-31T22:00:00+00:00")),
                    as_utc(parse_datetime("2025-04-01T05:00:00+00:00")),
                    77,
                    "HIGH",
                    True),
  GreennessForecast(as_utc(parse_datetime("2025-04-01T22:00:00+00:00")),
                    as_utc(parse_datetime("2025-04-02T05:00:00+00:00")),
                    60,
                    "HIGH",
                    False),
  GreennessForecast(as_utc(parse_datetime("2025-04-02T22:00:00+00:00")),
                    as_utc(parse_datetime("2025-04-03T05:00:00+00:00")),
                    77,
                    "HIGH",
                    True)
]

@pytest.mark.asyncio
async def test_when_forecast_none_then_none_returned():
  # Arrange
  current = datetime.strptime("2025-03-30T02:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  restrict_highlighted = False

  # Act
  result = get_current_and_next_forecast(current, None, restrict_highlighted)

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_current_not_available_then_current_none():
  # Arrange
  current = datetime.strptime("2025-03-30T02:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
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
  current = datetime.strptime("2025-04-03T02:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
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
  current = datetime.strptime("2025-04-01T02:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") if current_highlighted else datetime.strptime("2025-03-31T02:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
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
