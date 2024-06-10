from datetime import datetime, timedelta
import pytest

from homeassistant.util.dt import (now)

from integration import (get_test_context)
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

period_from = datetime.strptime("2021-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
period_to = datetime.strptime("2021-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
@pytest.mark.parametrize("product_code,tariff_code",[("SUPER-GREEN-24M-21-07-30", "G-1R-SUPER-GREEN-24M-21-07-30-A")])
async def test_when_get_gas_standing_charge_is_called_for_existent_tariff_then_rates_are_returned(product_code, tariff_code):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)

    # Act
    result = await client.async_get_gas_standing_charge(product_code, tariff_code, period_from, period_to)

    # Assert
    assert result is not None
    assert "value_inc_vat" in result
    assert result["value_inc_vat"] == 26.586

@pytest.mark.asyncio
@pytest.mark.parametrize("product_code,tariff_code",[("SILVER-FLEX-22-11-25", "G-1R-SILVER-FLEX-22-11-25-C")])
async def test_when_get_gas_standing_charge_is_called_with_tracker_tariff_then_rates_are_returned(product_code, tariff_code):
    # Arrange
    context = get_test_context()
    client = OctopusEnergyApiClient(context.api_key)

    period_from = datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    # Act
    result = await client.async_get_gas_standing_charge(product_code, tariff_code, period_from, period_to)

    # Assert
    assert result is not None
    assert "value_inc_vat" in result
    assert result["value_inc_vat"] is not None

@pytest.mark.asyncio
@pytest.mark.parametrize("product_code,tariff_code",[
    ("SUPER-GREEN-24M-21-07-30", "G-1R-NOT-A-TARIFF-A"),
    ("SUPER-GREEN-24M-21-07-30", "NOT-A-TARIFF"),
    ("NOT-A-PRODUCT", "G-1R-SILVER-FLEX-22-11-25-C")
])
async def test_when_get_gas_standing_charge_is_called_for_non_existent_tariff_then_none_is_returned(product_code, tariff_code):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)

    # Act
    result = await client.async_get_gas_standing_charge(product_code, tariff_code, period_from, period_to)

    # Assert
    assert result is None