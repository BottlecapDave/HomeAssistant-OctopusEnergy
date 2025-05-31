from datetime import datetime, timedelta
import pytest

from unit import (create_consumption_data, create_rate_data)
from custom_components.octopus_energy.cost_tracker import calculate_consumption_and_cost

@pytest.mark.asyncio
async def test_when_consumption_is_none_then_no_calculation_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  consumption_data = None
  rate_data = create_rate_data(period_from, period_to, [1, 2])
  standing_charge = 10.1

  # Act
  result = calculate_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    latest_date
  )

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_rates_is_none_then_no_calculation_is_returned():
  # Arrange
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  consumption_data = create_consumption_data(
    datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
    datetime.strptime("2022-02-28T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  rate_data = None
  standing_charge = 10.1

  # Act
  result = calculate_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    latest_date
  )

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_consumption_is_before_latest_date_then_no_calculation_is_returned():
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
  result = calculate_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    latest_date
  )

  # Assert
  assert result is None

@pytest.mark.asyncio
@pytest.mark.parametrize("latest_date",[(datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")), (None)])
async def test_when_consumption_available_then_calculation_returned(latest_date):
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
  result = calculate_consumption_and_cost(
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
async def test_when_consumption_starting_at_latest_date_then_calculation_returned():
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
  result = calculate_consumption_and_cost(
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
async def test_when_consumption_has_target_rate_then_calculations_returned_restricted_to_target_rate():
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
  result = calculate_consumption_and_cost(
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


# https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/1325
@pytest.mark.asyncio
async def test_when_consumption_is_small_then_costs_are_not_lost_due_to_rounding_error():
  # Arrange
  period_from = datetime.strptime("2025-05-25T19:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2025-05-25T21:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

  # Rate price is in pence
  expected_rate_price = 0.07

  rate_data = create_rate_data(period_from, period_to, [expected_rate_price])

  standing_charge = 10.1

  latest_date = None
  
  consumption_data = create_consumption_data(period_from, period_to, False)

  consumption_data[0]["consumption"] = 0.00010898594567265718
  consumption_data[1]["consumption"] = 0.014563223624449506
  consumption_data[2]["consumption"] = 0.01439248395307402
  consumption_data[3]["consumption"] = 0.002219051389815263

  expected_consumption_total = 0
  for consumption in consumption_data:
    expected_consumption_total = expected_consumption_total + consumption["consumption"]

  # Act
  result = calculate_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    latest_date
  )

  # Assert
  assert result is not None

  assert result["standing_charge"] == round(standing_charge / 100, 2)

  # Total is reported in pounds and pence, but rate prices are in pence, so we need to calculate our expected value
  assert result["total_cost_without_standing_charge"] == round((4 * expected_rate_price) / 100, 2)
  assert result["total_cost"] == round(((4 * expected_rate_price) + standing_charge) / 100, 2)
  
  assert result["last_evaluated"] == consumption_data[-1]["end"]
  assert result["total_consumption"] == expected_consumption_total

  # Make sure our data is returned in 30 minute increments
  assert len(result["charges"]) == 4
  expected_valid_from = period_from
  for index, item in enumerate(result["charges"]):
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

    assert "cost_raw" in item
    assert item["cost_raw"] > 0
    
    assert "consumption" in item
    assert item["consumption"] == consumption_data[index]["consumption"]

  assert "total_cost_off_peak" not in result
  assert "total_cost_peak" not in result
  assert "total_consumption_off_peak" not in result
  assert "total_consumption_peak" not in result