from datetime import datetime, timedelta
import pytest

from homeassistant.util.dt import (now)

from integration import (get_test_context)
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

default_period_from = datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
default_period_to = datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

async def async_assert_electricity_data(tariff, is_smart_meter, price_cap, period_from = default_period_from, period_to = default_period_to, expected_rates = None):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"], price_cap)

    # Act
    data = await client.async_get_electricity_rates(tariff, is_smart_meter, period_from, period_to)

    diff = period_to - period_from

    # Assert
    assert len(data) == diff.days * 48

    # Make sure our data is returned in 30 minute increments
    expected_valid_from = period_from
    for item in data:
        expected_valid_to = expected_valid_from + timedelta(minutes=30)

        assert "start" in item
        assert item["start"] == expected_valid_from
        assert "end" in item
        assert item["end"] == expected_valid_to

        assert "value_inc_vat" in item
        
        expected_value = None
        if expected_rates is not None:
            for rate in expected_rates:
                if rate["start"] <= item["start"] and rate["end"] >= item["end"]:
                    expected_value = rate["value_inc_vat"]
        
        if price_cap is not None:
            assert item["value_inc_vat"] <= price_cap
        elif expected_value is not None:
            assert item["value_inc_vat"] == expected_value

        expected_valid_from = expected_valid_to

    return data

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff,price_cap,period_from,period_to",[
    ("E-1R-SUPER-GREEN-24M-21-07-30-A", None, datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-GO-18-06-12-A", None, datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-VAR-21-09-29-A", None, datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-AGILE-18-02-21-A", None, datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-AGILE-FLEX-22-11-25-D", None, datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-SILVER-FLEX-22-11-25-C", None, datetime.strptime("2023-07-01T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2023-07-02T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-SUPER-GREEN-24M-21-07-30-A", 10, datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-GO-18-06-12-A", 10, datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-VAR-21-09-29-A", 10, datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-AGILE-18-02-21-A", 10, datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-AGILE-FLEX-22-11-25-D", 10, datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2022-12-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    ("E-1R-SILVER-FLEX-22-11-25-C", 10, datetime.strptime("2023-07-01T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),  datetime.strptime("2023-07-02T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
])
async def test_when_get_electricity_rates_is_called_with_tariff_then_data_is_returned_in_thirty_minute_increments(tariff, price_cap, period_from,period_to):
    await async_assert_electricity_data(tariff, False, price_cap, period_from, period_to)

@pytest.mark.asyncio
@pytest.mark.parametrize("price_cap",[
    (None),
    (35),
])
async def test_when_get_electricity_rates_is_called_with_flux_tariff_then_data_is_returned_in_thirty_minute_increments(price_cap):
    expected_flux_rates = [{
        "value_exc_vat": 32.1207,
        "value_inc_vat": 33.726735,
        "start": datetime.strptime("2023-03-27T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2023-03-28T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value_exc_vat": 44.969,
        "value_inc_vat": 47.21745,
        "start": datetime.strptime("2023-03-27T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2023-03-27T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value_exc_vat": 32.1207,
        "value_inc_vat": 33.726735,
        "start": datetime.strptime("2023-03-27T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2023-03-27T15:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value_exc_vat": 19.2724,
        "value_inc_vat": 20.23602,
        "start": datetime.strptime("2023-03-27T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2023-03-27T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    },
    {
        "value_exc_vat": 32.1207,
        "value_inc_vat": 33.726735,
        "start": datetime.strptime("2023-03-26T18:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.strptime("2023-03-27T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    }]

    await async_assert_electricity_data(
        "E-1R-FLUX-IMPORT-23-02-14-E",
        False,
        price_cap,
        datetime.strptime("2023-03-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2023-03-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        expected_flux_rates
    )

@pytest.mark.asyncio
@pytest.mark.parametrize("price_cap",[(None), (15)])
async def test_when_get_electricity_rates_is_called_with_duel_rate_tariff_dumb_meter_then_data_is_returned_in_thirty_minute_increments(price_cap):
    tariff = "E-2R-SUPER-GREEN-24M-21-07-30-A"
    data = await async_assert_electricity_data(tariff, False, price_cap)

    cheapest_rate_from = datetime.strptime("2022-12-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    cheapest_rate_to = datetime.strptime("2022-12-01T07:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    cheapest_rate = None
    for item in data:
        if cheapest_rate is None or cheapest_rate > item["value_inc_vat"]:
            cheapest_rate = item["value_inc_vat"]

    # Make sure all periods within the expected cheapest period have our cheapest rate
    for item in data:
        if item["start"] >= cheapest_rate_from and item["end"] <= cheapest_rate_to:
            if price_cap is not None and item["value_inc_vat"] > price_cap:
                assert item["value_inc_vat"] == price_cap
            else:
                assert item["value_inc_vat"] == cheapest_rate
        else:
            assert item["value_inc_vat"] != cheapest_rate

@pytest.mark.asyncio
@pytest.mark.parametrize("price_cap",[(None), (15)])
async def test_when_get_electricity_rates_is_called_with_duel_rate_tariff_smart_meter_then_data_is_returned_in_thirty_minute_increments(price_cap):
    tariff = "E-2R-SUPER-GREEN-24M-21-07-30-A"
    data = await async_assert_electricity_data(tariff, True, price_cap)

    cheapest_rate_from = datetime.strptime("2022-12-01T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    cheapest_rate_to = datetime.strptime("2022-12-01T07:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

    cheapest_rate = None
    for item in data:
        if cheapest_rate is None or cheapest_rate > item["value_inc_vat"]:
            cheapest_rate = item["value_inc_vat"]

    # Make sure all periods within the expected cheapest period have our cheapest rate
    for item in data:
        if item["start"] >= cheapest_rate_from and item["end"] <= cheapest_rate_to:
            if price_cap is not None and item["value_inc_vat"] > price_cap:
                assert item["value_inc_vat"] == price_cap
            else:
                assert item["value_inc_vat"] == cheapest_rate
        else:
            assert item["value_inc_vat"] != cheapest_rate

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff",[("E-2R-NOT-A-TARIFF-A"), ("E-1R-NOT-A-TARIFF-A"), ("NOT-A-TARIFF")])
async def test_when_get_electricity_rates_is_called_for_non_existent_tariff_then_none_is_returned(tariff):
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context["api_key"])

    # Act
    data = await client.async_get_electricity_rates(tariff, True, default_period_from, default_period_to)

    # Assert
    assert data is None

@pytest.mark.asyncio
async def test_when_get_electricity_rates_is_called_with_cosy_tariff_then_data_is_returned_in_thirty_minute_increments():
    # Arrange
    tariff = "E-1R-COSY-22-12-08-H"
    period_from = datetime.strptime("2023-10-15T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2023-10-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    # Act
    data = await async_assert_electricity_data(tariff, False, None, period_from, period_to)

    # Assert
    cheapest_rate = None
    for item in data:
        if cheapest_rate is None or cheapest_rate > item["value_inc_vat"]:
            cheapest_rate = item["value_inc_vat"]

    expensive_rate = None
    for item in data:
        if expensive_rate is None or expensive_rate < item["value_inc_vat"]:
            expensive_rate = item["value_inc_vat"]

    # Make sure all periods within the expected cheapest/expensive period have our cheapest/expensive rate
    for item in data:
        if (item["start"].hour >= 3 and item["start"].hour < 6):
            assert item["value_inc_vat"] == cheapest_rate
        elif (item["start"].hour >= 12 and item["start"].hour < 15):
            assert item["value_inc_vat"] == cheapest_rate
        elif (item["start"].hour >= 15 and item["start"].hour < 18):
            assert item["value_inc_vat"] == expensive_rate
        else:
            assert item["value_inc_vat"] != cheapest_rate
            assert item["value_inc_vat"] != expensive_rate

    