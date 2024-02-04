import pytest
from datetime import timedelta

from homeassistant.util.dt import (utcnow)

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_greenness_forecast_is_called_then_points_are_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"])

    # Act
    result = await client.async_get_greenness_forecast()

    # Assert
    assert result is not None
    assert len(result) > 0

    highlighted_forecast_found = False
    now = utcnow()
    previous_end = None
    
    for forecast in result:
        assert forecast.end >= now
        assert forecast.start <= forecast.end

        if previous_end is not None:
            assert forecast.start > previous_end

        previous_end = forecast.end

        assert forecast.greennessScore >= 0
        assert forecast.greennessIndex != "" and forecast.greennessIndex is not None
        assert forecast.greennessIndex is not None
        assert forecast.highlightFlag == True or forecast.highlightFlag == False
        if forecast.highlightFlag == True:
            highlighted_forecast_found = True

    assert highlighted_forecast_found == True