from datetime import datetime, timedelta
import pytest
from tests.unit import create_rate_data

from unit import (create_consumption_data)
from custom_components.octopus_energy.gas import calculate_gas_consumption_and_cost
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_gas_consumption_is_none_then_no_calculation_is_returned():
  # Arrange
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  consumption_data = None
  rates_data = create_rate_data(
    datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
    datetime.strptime("2022-02-28T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    [1, 2]
  )
  standing_charge = 27.0

  # Act
  consumption_cost = calculate_gas_consumption_and_cost(
    consumption_data,
    rates_data,
    standing_charge,
    latest_date,
    "m³",
    40
  )

  # Assert
  assert consumption_cost is None

@pytest.mark.asyncio
async def test_when_gas_rates_is_none_then_no_calculation_is_returned():
  # Arrange
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  rates_data = None
  consumption_data = create_consumption_data(
    datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
    datetime.strptime("2022-02-28T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  standing_charge = 27.0

  # Act
  consumption_cost = calculate_gas_consumption_and_cost(
    consumption_data,
    rates_data,
    standing_charge,
    latest_date,
    "m³",
    40
  )

  # Assert
  assert consumption_cost is None

@pytest.mark.asyncio
async def test_when_gas_consumption_is_before_latest_date_then_no_calculation_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-03-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  consumption_data = create_consumption_data(period_from, period_to)
  assert consumption_data is not None
  assert len(consumption_data) > 0

  rates_data = create_rate_data(
    datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
    datetime.strptime("2022-02-28T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    [1, 2]
  )
  standing_charge = 27.0

  # Act
  consumption_cost = calculate_gas_consumption_and_cost(
    consumption_data,
    rates_data,
    standing_charge,
    latest_date,
    "m³",
    40
  )

  # Assert
  assert consumption_cost is None

@pytest.mark.asyncio
@pytest.mark.parametrize("latest_date,consumption_units",[
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "m³"), 
  (None, "m³"),
  (datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "kWh"), 
  (None, "kWh")
])
async def test_when_gas_consumption_available_then_calculation_returned(latest_date, consumption_units):
  # Arrange
  
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Price is in pence
  expected_rate_price = 50

  rates_data = create_rate_data(period_from, period_to, [expected_rate_price])

  standing_charge = 27.0
  
  consumption_data = create_consumption_data(period_from, period_to)
  assert consumption_data is not None
  assert len(consumption_data) > 0
  assert consumption_data[-1]["end"] == period_to
  assert consumption_data[0]["start"] == period_from

  # Act
  result = calculate_gas_consumption_and_cost(
    consumption_data,
    rates_data,
    standing_charge,
    latest_date,
    consumption_units,
    40
  )

  # Assert
  assert result is not None
  assert len(result["charges"]) == 48

  assert result["standing_charge"] == round(standing_charge / 100, 2)
  
  assert result["last_evaluated"] == consumption_data[-1]["end"]
  
  # Total is reported in pounds and pence, but rate prices are in pence, so we need to calculate our expected value
  if consumption_units == "m³":
    expected_total_values = 11.363
    assert round(result["total_consumption_kwh"], 3) == round(48 * 11.363, 3)
    assert result["total_consumption_m3"] == 48 * 1
  else:
    expected_total_values = 1
    assert result["total_consumption_kwh"] == 48 * 1
    assert round(result["total_consumption_m3"], 3) == round(48 * 0.088, 3)

  expected_consumption_cost = round((round(expected_total_values, 2) * round(expected_rate_price, 2)) / 100, 2)
  assert result["total_cost_without_standing_charge"] == expected_consumption_cost * 48
  assert result["total_cost"] == (expected_consumption_cost * 48) + round(standing_charge / 100, 2)

  # Make sure our data is returned in 30 minute increments
  expected_valid_from = period_from
  for item in result["charges"]:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "start" in item
    assert item["start"] == expected_valid_from
    assert "end" in item
    assert item["end"] == expected_valid_to

    assert "rate" in item
    assert item["rate"] == round(expected_rate_price / 100, 6)

    assert "consumption_m3" in item
    if consumption_units == "m³":
      assert item["consumption_m3"] == 1
    else:
      assert item["consumption_m3"] == 0.088

    assert "consumption_kwh" in item
    if consumption_units == "m³":
      assert item["consumption_kwh"] == 11.363
    else:
      assert item["consumption_kwh"] == 1

    expected_valid_from = expected_valid_to

@pytest.mark.asyncio
@pytest.mark.parametrize("consumption_units",[
  ("m³"), 
  ("kWh")
])
async def test_when_gas_consumption_starting_at_latest_date_then_calculation_returned(consumption_units):
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Price is in pence
  expected_rate_price = 50

  rates_data = create_rate_data(period_from, period_to, [expected_rate_price])

  tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"
  latest_date = None

  standing_charge = 27.0
  
  consumption_data = create_consumption_data(period_from, period_to, True)
  assert consumption_data is not None
  assert len(consumption_data) > 0
  assert consumption_data[0]["end"] == period_to
  assert consumption_data[-1]["start"] == period_from

  # Act
  result = calculate_gas_consumption_and_cost(
    consumption_data,
    rates_data,
    standing_charge,
    latest_date,
    consumption_units,
    40
  )

  # Assert
  assert result is not None
  assert len(result["charges"]) == 48

  assert result["last_evaluated"] == consumption_data[0]["end"]
  assert result["standing_charge"] == round(standing_charge / 100, 2)

  # Total is reported in pounds and pence, but rate prices are in pence, so we need to calculate our expected value
  if consumption_units == "m³":
    expected_total_values = 11.363
    assert round(result["total_consumption_kwh"], 3) == round(48 * 11.363, 3)
    assert result["total_consumption_m3"] == 48 * 1
  else:
    expected_total_values = 1
    assert result["total_consumption_kwh"] == 48 * 1
    assert round(result["total_consumption_m3"], 3) == round(48 * 0.088, 3)

  expected_consumption_cost = round((round(expected_total_values, 2) * round(expected_rate_price, 2)) / 100, 2)
  assert result["total_cost_without_standing_charge"] == expected_consumption_cost * 48
  assert result["total_cost"] == (expected_consumption_cost * 48) + round(standing_charge / 100, 2)

  # Make sure our data is returned in 30 minute increments
  expected_valid_from = period_from
  for item in result["charges"]:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "start" in item
    assert item["start"] == expected_valid_from
    assert "end" in item
    assert item["end"] == expected_valid_to

    assert "rate" in item
    assert item["rate"] == round(expected_rate_price / 100, 6)

    assert "consumption_m3" in item
    if consumption_units == "m³":
      assert item["consumption_m3"] == 1
    else:
      assert item["consumption_m3"] == 0.088

    assert "consumption_kwh" in item
    if consumption_units == "m³":
      assert item["consumption_kwh"] == 11.363
    else:
      assert item["consumption_kwh"] == 1

    expected_valid_from = expected_valid_to