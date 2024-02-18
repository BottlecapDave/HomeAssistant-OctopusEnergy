from datetime import datetime, timedelta
import pytest

from homeassistant.util.dt import (now)

from integration import (get_test_context)
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff,price_cap,period_from,period_to",[
    ("G-1R-SUPER-GREEN-24M-21-07-30-A", None, datetime.strptime("2021-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2021-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("G-1R-SUPER-GREEN-24M-21-07-30-A", 2, datetime.strptime("2021-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2021-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("G-1R-SILVER-FLEX-22-11-25-C", None, datetime.strptime("2023-06-01T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-06-02T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
    ("G-1R-SILVER-FLEX-22-11-25-C", 2, datetime.strptime("2023-06-01T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-06-02T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
])
async def test_when_get_gas_rates_is_called_for_existent_tariff_then_rates_are_returned(tariff, price_cap, period_from, period_to):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key, None, price_cap)

    # Act
    data = await client.async_get_gas_rates(tariff, period_from, period_to)

    # Assert
    assert data is not None
    assert len(data) == 48

    # Make sure our data is returned in 30 minute increments
    expected_valid_from = period_from
    for item in data:
        expected_valid_to = expected_valid_from + timedelta(minutes=30)

        assert "start" in item
        assert item["start"] == expected_valid_from
        assert "end" in item
        assert item["end"] == expected_valid_to

        assert "value_inc_vat" in item
        if price_cap is not None:
            assert item["value_inc_vat"] <= price_cap

        expected_valid_from = expected_valid_to

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff",[("G-1R-NOT-A-TARIFF-A"), ("NOT-A-TARIFF")])
async def test_when_get_gas_rates_is_called_for_non_existent_tariff_then_none_is_returned(tariff):
    # Arrange
    context = get_test_context()
    period_from = now().replace(hour=0, minute=0, second=0, microsecond=0)
    period_to = (now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    client = OctopusEnergyApiClient(context.api_key)

    # Act
    data = await client.async_get_gas_rates(tariff, period_from, period_to)

    # Assert
    assert data is None