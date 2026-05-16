from datetime import datetime, timedelta
import pytest

from unit import (create_consumption_data, create_rate_data)
from custom_components.octopus_energy.electricity import calculate_electricity_consumption_and_cost

@pytest.mark.asyncio
async def test_when_electricity_consumption_is_none_then_no_calculation_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  consumption_data = None
  rate_data = create_rate_data(period_from, period_to, [1, 2])
  standing_charge = 10.1

  # Act
  result = calculate_electricity_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    latest_date
  )

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_electricity_rates_is_none_then_no_calculation_is_returned():
  # Arrange
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  consumption_data = create_consumption_data(
    datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
    datetime.strptime("2022-02-28T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  rate_data = None
  standing_charge = 10.1

  # Act
  result = calculate_electricity_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    latest_date
  )

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_electricity_consumption_is_before_latest_date_then_no_calculation_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-03-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  standing_charge = 10.1

  consumption_data = create_consumption_data(period_from, period_to)
  assert consumption_data is not None
  assert len(consumption_data) > 0
  
  rate_data = create_rate_data(period_from, period_to, [1, 2])

  # Act
  result = calculate_electricity_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    latest_date
  )

  # Assert
  assert result is None

@pytest.mark.asyncio
@pytest.mark.parametrize("latest_date",[(datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")), (None)])
async def test_when_electricity_consumption_available_then_calculation_returned(latest_date):
  # Arrange
  
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Rate price is in pence
  expected_rate_price = 50

  rate_data = create_rate_data(period_from, period_to, [expected_rate_price])

  standing_charge = 10.1
  
  consumption_data = create_consumption_data(period_from, period_to)
  assert consumption_data is not None
  assert len(consumption_data) == 48
  assert consumption_data[-1]["end"] == period_to
  assert consumption_data[0]["start"] == period_from

  expected_consumption_total = 0
  for consumption in consumption_data:
    expected_consumption_total = expected_consumption_total + consumption["consumption"]

  # Act
  result = calculate_electricity_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    latest_date
  )

  # Assert
  assert result is not None

  assert result["standing_charge"] == round(standing_charge / 100, 2)
  assert result["total_cost_without_standing_charge"] == round((48 * expected_rate_price) / 100, 2)
  assert result["total_cost"] == round(((48 * expected_rate_price) + standing_charge) / 100, 2)
  assert result["last_evaluated"] == consumption_data[-1]["end"]
  assert result["total_consumption"] == expected_consumption_total

  # Make sure our data is returned in 30 minute increments
  assert len(result["charges"]) == 48
  expected_valid_from = period_from
  for item in result["charges"]:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "start" in item
    assert item["start"] == expected_valid_from
    assert "end" in item
    assert item["end"] == expected_valid_to

    expected_valid_from = expected_valid_to

    assert "rate" in item
    assert item["rate"] == round(expected_rate_price / 100, 6)
    
    assert "cost" in item
    assert item["cost"] == round(expected_rate_price / 100, 2)
    
    assert "consumption" in item
    assert item["consumption"] == 1

@pytest.mark.asyncio
async def test_when_electricity_consumption_starting_at_latest_date_then_calculation_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Rate price is in pence
  expected_rate_price = 50

  rate_data = create_rate_data(period_from, period_to, [expected_rate_price])

  standing_charge = 10.1

  latest_date = None
  
  consumption_data = create_consumption_data(period_from, period_to, True)
  assert consumption_data is not None
  assert len(consumption_data) > 0
  assert consumption_data[0]["end"] == period_to
  assert consumption_data[-1]["start"] == period_from

  expected_consumption_total = 0
  for consumption in consumption_data:
    expected_consumption_total = expected_consumption_total + consumption["consumption"]

  # Act
  result = calculate_electricity_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    latest_date
  )

  # Assert
  assert result is not None

  assert result["standing_charge"] == round(standing_charge / 100, 2)

  # Total is reported in pounds and pence, but rate prices are in pence, so we need to calculate our expected value
  assert result["total_cost_without_standing_charge"] == round((48 * expected_rate_price) / 100, 2)
  assert result["total_cost"] == round(((48 * expected_rate_price) + standing_charge) / 100, 2)
  
  assert result["last_evaluated"] == consumption_data[0]["end"]
  assert result["total_consumption"] == expected_consumption_total

  # Make sure our data is returned in 30 minute increments
  assert len(result["charges"]) == 48
  expected_valid_from = period_from
  for item in result["charges"]:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "start" in item
    assert item["start"] == expected_valid_from
    assert "end" in item
    assert item["end"] == expected_valid_to

    expected_valid_from = expected_valid_to

    assert "rate" in item
    assert item["rate"] == round(expected_rate_price / 100, 6)
    
    assert "cost" in item
    assert item["cost"] == round(expected_rate_price / 100, 2)
    
    assert "consumption" in item
    assert item["consumption"] == 1

  assert "total_cost_off_peak" not in result
  assert "total_cost_peak" not in result
  assert "total_consumption_off_peak" not in result
  assert "total_consumption_peak" not in result

@pytest.mark.asyncio
async def test_when_electricity_consumption_has_target_rate_then_calculations_returned_restricted_to_target_rate():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  peak_from =  datetime.strptime("2022-02-28T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-28T06:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Rate price is in pence
  expected_peak_rate_price = 2
  expected_off_peak_rate_price = 1

  rate_data = create_rate_data(period_from, peak_from, [expected_off_peak_rate_price]) + create_rate_data(peak_from, period_to, [expected_peak_rate_price])

  standing_charge = 10.1
  
  consumption_data = create_consumption_data(period_from, period_to)
  assert consumption_data != None
  assert len(consumption_data) == 12
  assert consumption_data[-1]["end"] == period_to
  assert consumption_data[0]["start"] == period_from

  # Act
  result = calculate_electricity_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    latest_date,
    target_rate=expected_peak_rate_price
  )

  # Assert
  assert result is not None

  assert "total_consumption" in result
  assert result["total_consumption"] == 2

  assert "total_cost" in result
  assert result["total_cost"] == round(((2 * expected_peak_rate_price) + standing_charge) / 100, 2)

  assert "total_cost_without_standing_charge" in result
  assert result["total_cost_without_standing_charge"] == round((2 * expected_peak_rate_price) / 100, 2)

@pytest.mark.asyncio
async def test_electricity_consumption_with_website_data():

  consumption_data = [
    { "consumption": 0.064000, "expected_cost": 0.0153, "start": datetime.strptime("2026-05-09T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T00:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.060000, "expected_cost": 0.0143, "start": datetime.strptime("2026-05-09T00:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T01:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.062000, "expected_cost": 0.0148, "start": datetime.strptime("2026-05-09T01:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T01:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.063000, "expected_cost":  0.015, "start": datetime.strptime("2026-05-09T01:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T02:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.059000, "expected_cost": 0.0141, "start": datetime.strptime("2026-05-09T02:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T02:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.070000, "expected_cost": 0.0167, "start": datetime.strptime("2026-05-09T02:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T03:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.056000, "expected_cost": 0.0134, "start": datetime.strptime("2026-05-09T03:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T03:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.069000, "expected_cost": 0.0165, "start": datetime.strptime("2026-05-09T03:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T04:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.056000, "expected_cost": 0.0134, "start": datetime.strptime("2026-05-09T04:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T04:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.068000, "expected_cost": 0.0162, "start": datetime.strptime("2026-05-09T04:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T05:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.051000, "expected_cost": 0.0122, "start": datetime.strptime("2026-05-09T05:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T05:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.065000, "expected_cost": 0.0155, "start": datetime.strptime("2026-05-09T05:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T06:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.052000, "expected_cost": 0.0124, "start": datetime.strptime("2026-05-09T06:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T06:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.061000, "expected_cost": 0.0146, "start": datetime.strptime("2026-05-09T06:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T07:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.056000, "expected_cost": 0.0134, "start": datetime.strptime("2026-05-09T07:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T07:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.218000, "expected_cost":  0.052, "start": datetime.strptime("2026-05-09T07:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T08:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.101000, "expected_cost": 0.0241, "start": datetime.strptime("2026-05-09T08:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T08:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.100000, "expected_cost": 0.0239, "start": datetime.strptime("2026-05-09T08:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T09:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.109000, "expected_cost":  0.026, "start": datetime.strptime("2026-05-09T09:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T09:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.080000, "expected_cost": 0.0191, "start": datetime.strptime("2026-05-09T09:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T10:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.093000, "expected_cost": 0.0222, "start": datetime.strptime("2026-05-09T10:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.186000, "expected_cost": 0.0444, "start": datetime.strptime("2026-05-09T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T11:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.248000, "expected_cost": 0.0592, "start": datetime.strptime("2026-05-09T11:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T11:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.202000, "expected_cost": 0.0482, "start": datetime.strptime("2026-05-09T11:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.204000, "expected_cost": 0.0487, "start": datetime.strptime("2026-05-09T12:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T12:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.072000, "expected_cost": 0.0172, "start": datetime.strptime("2026-05-09T12:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T13:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.070000, "expected_cost": 0.0167, "start": datetime.strptime("2026-05-09T13:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T13:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.068000, "expected_cost": 0.0162, "start": datetime.strptime("2026-05-09T13:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T14:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.105000, "expected_cost":  0.025, "start": datetime.strptime("2026-05-09T14:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T14:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.177000, "expected_cost": 0.0422, "start": datetime.strptime("2026-05-09T14:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T15:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.112000, "expected_cost": 0.0267, "start": datetime.strptime("2026-05-09T15:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T15:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.303000, "expected_cost": 0.0723, "start": datetime.strptime("2026-05-09T15:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T16:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.265000, "expected_cost": 0.0632, "start": datetime.strptime("2026-05-09T16:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T16:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.182000, "expected_cost": 0.0434, "start": datetime.strptime("2026-05-09T16:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.075000, "expected_cost": 0.0179, "start": datetime.strptime("2026-05-09T17:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T17:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.056000, "expected_cost": 0.0134, "start": datetime.strptime("2026-05-09T17:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.069000, "expected_cost": 0.0165, "start": datetime.strptime("2026-05-09T18:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T18:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.079000, "expected_cost": 0.0188, "start": datetime.strptime("2026-05-09T18:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T19:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.088000, "expected_cost":  0.021, "start": datetime.strptime("2026-05-09T19:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T19:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.072000, "expected_cost": 0.0172, "start": datetime.strptime("2026-05-09T19:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T20:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.142000, "expected_cost": 0.0339, "start": datetime.strptime("2026-05-09T20:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T20:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.143000, "expected_cost": 0.0341, "start": datetime.strptime("2026-05-09T20:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T21:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.243000, "expected_cost":  0.058, "start": datetime.strptime("2026-05-09T21:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T21:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.115000, "expected_cost": 0.0274, "start": datetime.strptime("2026-05-09T21:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T22:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.086000, "expected_cost": 0.0205, "start": datetime.strptime("2026-05-09T22:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T22:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.093000, "expected_cost": 0.0222, "start": datetime.strptime("2026-05-09T22:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T23:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.060000, "expected_cost": 0.0143, "start": datetime.strptime("2026-05-09T23:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-09T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
    { "consumption": 0.069000, "expected_cost": 0.0165, "start": datetime.strptime("2026-05-09T23:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2026-05-10T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z") },
  ]

  rate_data = create_rate_data(
    datetime.strptime("2026-05-09T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2026-05-10T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    [23.856]
  )

  standing_charge = 53.0

  # Act
  result = calculate_electricity_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    None
  )

  assert result is not None

  assert "total_consumption" in result
  assert result["total_consumption"] == 5.197000000000001
  
  assert "total_cost" in result
  assert result["total_cost"] == 1.77

  assert "total_cost_without_standing_charge" in result
  assert result["total_cost_without_standing_charge"] == 1.24

  assert len(result["charges"]) == len(consumption_data)
  for index, item in enumerate(result["charges"]):
    assert "start" in item
    assert item["start"] == consumption_data[index]["start"]
    assert "end" in item
    assert item["end"] == consumption_data[index]["end"]

    assert "rate" in item
    assert item["rate"] == 0.23856
    
    assert "cost" in item
    assert round(item["raw_cost"], 4) == consumption_data[index]["expected_cost"]
    
    assert "consumption" in item
    assert item["consumption"] == consumption_data[index]["consumption"]
  