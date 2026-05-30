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

  expected_consumption_cost = round((expected_total_values * expected_rate_price * 48) / 100, 2)
  assert result["total_cost_without_standing_charge"] == expected_consumption_cost
  assert result["total_cost"] == round((expected_total_values * expected_rate_price * 48 + standing_charge) / 100, 2)

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

  expected_consumption_cost = round((expected_total_values * 48 * expected_rate_price) / 100, 2)
  assert result["total_cost_without_standing_charge"] == expected_consumption_cost
  assert result["total_cost"] == round(((expected_total_values * 48 * expected_rate_price) + standing_charge) / 100, 2)

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
async def test_gas_consumption_with_website_data():

  consumption_data = [
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T00:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T00:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T01:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T01:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T01:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T01:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T02:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T02:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T02:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T02:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T03:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T03:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T03:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T03:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T04:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T04:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T04:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T04:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T05:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T05:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T05:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T05:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T06:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T06:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T06:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T06:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T07:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T07:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T07:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0226, "expected_cost": 0.0014, "start": datetime.strptime("2026-05-09T07:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T08:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.2261, "expected_cost": 0.0141, "start": datetime.strptime("2026-05-09T08:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T08:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.4409, "expected_cost": 0.0275, "start": datetime.strptime("2026-05-09T08:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T09:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 2.0351, "expected_cost": 0.1271, "start": datetime.strptime("2026-05-09T09:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T09:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T09:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T10:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.1357, "expected_cost": 0.0085, "start": datetime.strptime("2026-05-09T10:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.6331, "expected_cost": 0.0396, "start": datetime.strptime("2026-05-09T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T11:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 1.0401, "expected_cost": 0.065, "start": datetime.strptime("2026-05-09T11:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T11:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T11:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0226, "expected_cost": 0.0014, "start": datetime.strptime("2026-05-09T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T12:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T12:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T13:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T13:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T13:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T13:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T14:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.1922, "expected_cost": 0.012, "start": datetime.strptime("2026-05-09T14:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T14:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0113, "expected_cost": 0.0007, "start": datetime.strptime("2026-05-09T14:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T15:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0113, "expected_cost": 0.0007, "start": datetime.strptime("2026-05-09T15:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T15:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T15:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T16:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T16:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T16:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0565, "expected_cost": 0.0035, "start": datetime.strptime("2026-05-09T16:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T17:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T17:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T18:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.1583, "expected_cost": 0.0099, "start": datetime.strptime("2026-05-09T18:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T19:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T19:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T19:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T19:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T20:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T20:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T20:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T20:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T21:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T21:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T21:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T21:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T22:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0226, "expected_cost": 0.0014, "start": datetime.strptime("2026-05-09T22:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T22:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0904, "expected_cost": 0.0056, "start": datetime.strptime("2026-05-09T22:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T23:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T23:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.0000, "expected_cost": 0.0, "start": datetime.strptime("2026-05-09T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-10T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
  ]

  rate_data = create_rate_data(
    datetime.strptime("2026-05-09T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2026-05-10T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [6.2475]
  )

  standing_charge = 32.68

  # Act
  result = calculate_gas_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    None,
    "kWh",
    40
  )

  assert result is not None

  assert "total_consumption_kwh" in result
  assert result["total_consumption_kwh"] == 5.098799999999999
  
  assert "total_cost" in result
  assert result["total_cost"] == 0.65

  assert "total_cost_without_standing_charge" in result
  assert result["total_cost_without_standing_charge"] == 0.32

  assert len(result["charges"]) == len(consumption_data)
  for index, item in enumerate(result["charges"]):
    assert "start" in item
    assert item["start"] == consumption_data[index]["start"]
    assert "end" in item
    assert item["end"] == consumption_data[index]["end"]

    assert "rate" in item
    assert item["rate"] == 0.062475
    
    assert "cost" in item
    assert round(item["raw_cost"], 4) == consumption_data[index]["expected_cost"]
    
    assert "consumption_kwh" in item
    assert item["consumption_kwh"] == consumption_data[index]["consumption"]