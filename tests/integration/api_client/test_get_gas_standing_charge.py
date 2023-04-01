from datetime import datetime, timedelta
import os
import pytest

from homeassistant.util.dt import (now)
from integration import (get_test_context, async_get_tracker_tariff)
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

period_from = datetime.strptime("2021-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
period_to = datetime.strptime("2021-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff",[("G-1R-SUPER-GREEN-24M-21-07-30-A")])
async def test_when_get_gas_standing_charge_is_called_for_existent_tariff_then_rates_are_returned(tariff):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"])

    # Act
    result = await client.async_get_gas_standing_charge(tariff, period_from, period_to)

    # Assert
    assert result is not None
    assert "value_inc_vat" in result
    assert result["value_inc_vat"] == 26.586

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff",[("G-1R-SILVER-FLEX-22-11-25-C")])
async def test_when_get_gas_standing_charge_is_called_with_tracker_tariff_then_rates_are_returned(tariff):
    # Arrange
    context = get_test_context()
    period_from = now().replace(hour=0, minute=0, second=0, microsecond=0)
    period_to = (now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    client = OctopusEnergyApiClient(context["api_key"])

    expected_tracker = await async_get_tracker_tariff(context["api_key"], tariff, now())
    assert expected_tracker is not None

    # Act
    result = await client.async_get_gas_standing_charge(tariff, period_from, period_to)

    # Assert
    assert result is not None
    assert "value_inc_vat" in result
    assert result["value_inc_vat"] == expected_tracker["standing_charge"]

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff",[("G-1R-NOT-A-TARIFF-A"), ("NOT-A-TARIFF")])
async def test_when_get_gas_standing_charge_is_called_for_non_existent_tariff_then_none_is_returned(tariff):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"])

    # Act
    result = await client.async_get_gas_standing_charge(tariff, period_from, period_to)

    # Assert
    assert result == None