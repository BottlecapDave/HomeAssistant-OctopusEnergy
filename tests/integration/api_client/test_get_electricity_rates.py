from datetime import datetime, timedelta
import os
import pytest

from homeassistant.util.dt import (now)
from integration import (get_test_context, async_get_tracker_tariff)
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

period_from = datetime.strptime("2021-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
period_to = datetime.strptime("2021-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

async def async_assert_electricity_data(tariff, is_smart_meter):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"])

    # Act
    data = await client.async_get_electricity_rates(tariff, is_smart_meter, period_from, period_to)

    # Assert
    assert len(data) == 48

    # Make sure our data is returned in 30 minute increments
    expected_valid_from = period_from
    for item in data:
        expected_valid_to = expected_valid_from + timedelta(minutes=30)

        assert "valid_from" in item
        assert item["valid_from"] == expected_valid_from
        assert "valid_to" in item
        assert item["valid_to"] == expected_valid_to

        assert "value_exc_vat" in item
        assert "value_inc_vat" in item

        expected_valid_from = expected_valid_to

    return data

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff",[
    ("E-1R-SUPER-GREEN-24M-21-07-30-A"),
    ("E-1R-GO-18-06-12-A"),
    ("E-1R-VAR-21-09-29-A"),
    ("E-1R-AGILE-18-02-21-A"),
])
async def test_when_get_electricity_rates_is_called_with_tariff_then_data_is_returned_in_thirty_minute_increments(tariff):
    await async_assert_electricity_data(tariff, False)

@pytest.mark.asyncio
async def test_when_get_electricity_rates_is_called_with_duel_rate_tariff_dumb_meter_then_data_is_returned_in_thirty_minute_increments():
    tariff = "E-2R-SUPER-GREEN-24M-21-07-30-A"
    data = await async_assert_electricity_data(tariff, False)

    cheapest_rate_from = datetime.strptime("2021-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    cheapest_rate_to = datetime.strptime("2021-12-01T07:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    cheapest_rate = None
    for item in data:
        if cheapest_rate == None or cheapest_rate > item["value_inc_vat"]:
            cheapest_rate = item["value_inc_vat"]

    # Make sure all periods within the expected cheapest period have our cheapest rate
    for item in data:
        if item["valid_from"] >= cheapest_rate_from and item["valid_to"] <= cheapest_rate_to:
            assert item["value_inc_vat"] == cheapest_rate
        else:
            assert item["value_inc_vat"] != cheapest_rate
        

@pytest.mark.asyncio
async def test_when_get_electricity_rates_is_called_with_duel_rate_tariff_smart_meter_then_data_is_returned_in_thirty_minute_increments():
    tariff = "E-2R-SUPER-GREEN-24M-21-07-30-A"
    data = await async_assert_electricity_data(tariff, True)

    cheapest_rate_from = datetime.strptime("2021-12-01T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    cheapest_rate_to = datetime.strptime("2021-12-01T07:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

    cheapest_rate = None
    for item in data:
        if cheapest_rate == None or cheapest_rate > item["value_inc_vat"]:
            cheapest_rate = item["value_inc_vat"]

    # Make sure all periods within the expected cheapest period have our cheapest rate
    for item in data:
        if item["valid_from"] >= cheapest_rate_from and item["valid_to"] <= cheapest_rate_to:
            assert item["value_inc_vat"] == cheapest_rate
        else:
            assert item["value_inc_vat"] != cheapest_rate

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff",[("E-1R-SILVER-FLEX-22-11-25-C")])
async def test_when_get_electricity_rates_is_called_with_tracker_tariff_then_rates_are_returned(tariff):
    # Arrange
    context = get_test_context()
    period_from = now().replace(hour=0, minute=0, second=0, microsecond=0)
    period_to = (now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    client = OctopusEnergyApiClient(context["api_key"])

    expected_tracker = await async_get_tracker_tariff(context["api_key"], tariff, now())
    assert expected_tracker is not None

    # Act
    data = await client.async_get_electricity_rates(tariff, False, period_from, period_to)

    # Assert
    assert data is not None
    assert len(data) == 48

    # Make sure our data is returned in 30 minute increments
    expected_valid_from = period_from
    for item in data:
        expected_valid_to = expected_valid_from + timedelta(minutes=30)

        assert "valid_from" in item
        assert item["valid_from"] == expected_valid_from
        assert "valid_to" in item
        assert item["valid_to"] == expected_valid_to

        assert "value_exc_vat" in item
        assert "value_inc_vat" in item
        assert item["value_exc_vat"] == expected_tracker["unit_rate"] - expected_tracker["breakdown"]["unit_charge"]["VAT"]
        assert item["value_inc_vat"] == expected_tracker["unit_rate"]

        expected_valid_from = expected_valid_to

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff",[("E-2R-NOT-A-TARIFF-A"), ("E-1R-NOT-A-TARIFF-A")])
async def test_when_get_electricity_rates_is_called_for_non_existent_tariff_then_none_is_returned(tariff):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"])

    # Act
    data = await client.async_get_electricity_rates(tariff, True, period_from, period_to)

    # Assert
    assert data == None