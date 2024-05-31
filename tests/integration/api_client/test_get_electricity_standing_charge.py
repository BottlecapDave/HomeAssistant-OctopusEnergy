from datetime import datetime, timedelta
import pytest

from homeassistant.util.dt import (now)

from integration import (get_test_context)
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

period_from = datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
period_to = datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
@pytest.mark.parametrize("product_code,tariff_code,expected_value_inc_vat",[
    ("SUPER-GREEN-24M-21-07-30", "E-1R-SUPER-GREEN-24M-21-07-30-A", 24.0135),
    ("GO-18-06-12", "E-1R-GO-18-06-12-A", 25.0005),
    ("VAR-21-09-29", "E-1R-VAR-21-09-29-A", 37.29243),
    ("AGILE-18-02-21", "E-1R-AGILE-18-02-21-A", 21.0),
    ("AGILE-FLEX-22-11-25", "E-1R-AGILE-FLEX-22-11-25-D", 46.956)
])
async def test_when_get_electricity_standing_charge_is_called_for_existent_tariff_then_rates_are_returned(product_code, tariff_code, expected_value_inc_vat):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)

    # Act
    result = await client.async_get_electricity_standing_charge(product_code, tariff_code, period_from, period_to)

    # Assert
    assert result is not None
    assert "value_inc_vat" in result
    assert result["value_inc_vat"] == expected_value_inc_vat

@pytest.mark.asyncio
@pytest.mark.parametrize("product_code,tariff_code",[("SILVER-FLEX-22-11-25", "E-1R-SILVER-FLEX-22-11-25-C")])
async def test_when_get_electricity_standing_charge_is_called_with_tracker_tariff_then_rates_are_returned(product_code, tariff_code):
    # Arrange
    context = get_test_context()
    client = OctopusEnergyApiClient(context.api_key)

    # Act
    result = await client.async_get_electricity_standing_charge(product_code, tariff_code, period_from, period_to)

    # Assert
    assert result is not None
    assert "value_inc_vat" in result
    assert result["value_inc_vat"] is not None

@pytest.mark.asyncio
@pytest.mark.parametrize("product_code,tariff_code",[
    ("NOT-A-PRODUCT", "E-1R-NOT-A-TARIFF-A"),
    ("AGILE-FLEX-22-11-25", "NOT-A-TARIFF"),
    ("AGILE-FLEX-22-11-25", "E-1R-NOT-A-PRODUCT-D")
])
async def test_when_get_electricity_standing_charge_is_called_for_non_existent_tariff_then_none_is_returned(product_code, tariff_code):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)

    # Act
    result = await client.async_get_electricity_standing_charge(product_code, tariff_code, period_from, period_to)

    # Assert
    assert result is None