from datetime import datetime, timedelta
import os
import pytest

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

async def async_assert_electricity_data(tariff):
    # Arrange
    client = OctopusEnergyApiClient(os.environ["API_KEY"])
    period_from = datetime.strptime("2021-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2021-12-03T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    # Act
    data = await client.async_get_rates(tariff, period_from, period_to)

    # Assert
    assert len(data) == 96

    expected_valid_from = period_from
    for item in data:
        expected_valid_to = expected_valid_from + timedelta(minutes=30)

        assert "valid_from" in item
        assert item["valid_from"] == expected_valid_from
        assert "valid_to" in item
        assert item["valid_to"] == expected_valid_to

        expected_valid_from = expected_valid_to

@pytest.mark.asyncio
async def test_when_get_rates_is_called_with_fixed_tariff_then_data_is_returned_in_thirty_minute_increments():
    tariff = "E-1R-SUPER-GREEN-24M-21-07-30-A"
    await async_assert_electricity_data(tariff)

@pytest.mark.asyncio
async def test_when_get_rates_is_called_with_go_tariff_then_data_is_returned_in_thirty_minute_increments():
    tariff = "E-1R-GO-18-06-12-A"
    await async_assert_electricity_data(tariff)

@pytest.mark.asyncio
async def test_when_get_rates_is_called_with_variable_tariff_then_data_is_returned_in_thirty_minute_increments():
    tariff = "E-1R-VAR-21-09-29-A"
    await async_assert_electricity_data(tariff)

@pytest.mark.asyncio
async def test_when_get_rates_is_called_with_agile_tariff_then_data_is_returned_in_thirty_minute_increments():
    tariff = "E-1R-AGILE-18-02-21-A"
    await async_assert_electricity_data(tariff)

@pytest.mark.asyncio
async def test_when_get_rates_is_called_with_duel_rate_tariff_then_data_is_returned_in_thirty_minute_increments():
    tariff = "E-2R-SUPER-GREEN-24M-21-07-30-A"
    await async_assert_electricity_data(tariff)