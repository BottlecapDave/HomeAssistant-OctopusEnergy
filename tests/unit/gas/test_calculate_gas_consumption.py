from datetime import datetime, timedelta
import pytest

from unit import (create_consumption_data)
from custom_components.octopus_energy.gas import calculate_gas_consumption

@pytest.mark.asyncio
async def test_when_gas_consumption_is_none_then_no_calculation_is_returned():
  # Arrange
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Act
  consumption = calculate_gas_consumption(
    None,
    latest_date,
    "m³",
    40
  )

  # Assert
  assert consumption == None

@pytest.mark.asyncio
async def test_when_gas_consumption_is_less_than_three_records_then_no_calculation_is_returned():
  # Arrange
  latest_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  consumption_data = create_consumption_data(
    datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 
    datetime.strptime("2022-02-28T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )

  # Act
  consumption = calculate_gas_consumption(
    consumption_data,
    latest_date,
    "m³",
    40
  )

  # Assert
  assert consumption == None

@pytest.mark.asyncio
async def test_when_gas_consumption_is_before_latest_date_then_no_calculation_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  latest_date = datetime.strptime("2022-03-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  consumption_data = create_consumption_data(period_from, period_to)

  # Act
  consumption = calculate_gas_consumption(
    consumption_data,
    latest_date,
    "m³",
    40
  )

  # Assert
  assert consumption == None

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

  consumption_data = create_consumption_data(period_from, period_to)
  assert consumption_data != None
  assert len(consumption_data) > 0
  assert consumption_data[-1]["interval_end"] == period_to
  assert consumption_data[0]["interval_start"] == period_from

  # Act
  consumption = calculate_gas_consumption(
    consumption_data,
    latest_date,
    consumption_units,
    40
  )

  # Assert
  assert consumption != None
  assert consumption["last_calculated_timestamp"] == consumption_data[-1]["interval_end"]
  
  if consumption_units == "m³":
    assert consumption["total_kwh"] == round(48 * 11.363, 3)
    assert consumption["total_m3"] == 48 * 1
  else:
    assert consumption["total_kwh"] == 48 * 1
    assert consumption["total_m3"] == round(48 * 0.088, 3)

  assert len(consumption["consumptions"]) == len(consumption_data)

  # Make sure our data is returned in 30 minute increments
  expected_valid_from = period_from
  for item in consumption["consumptions"]:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "from" in item
    assert item["from"] == expected_valid_from
    assert "to" in item
    assert item["to"] == expected_valid_to

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
  latest_date = None

  consumption_data = create_consumption_data(period_from, period_to, True)
  assert consumption_data != None
  assert len(consumption_data) > 0
  assert consumption_data[0]["interval_end"] == period_to
  assert consumption_data[-1]["interval_start"] == period_from

  # Act
  consumption = calculate_gas_consumption(
    consumption_data,
    latest_date,
    consumption_units,
    40
  )

  # Assert
  assert consumption != None
  assert consumption["last_calculated_timestamp"] == consumption_data[0]["interval_end"]
  
  if consumption_units == "m³":
    assert consumption["total_kwh"] == round(48 * 11.363, 3)
    assert consumption["total_m3"] == 48 * 1
  else:
    assert consumption["total_kwh"] == 48 * 1
    assert consumption["total_m3"] == round(48 * 0.088, 3)

  assert len(consumption["consumptions"]) == len(consumption_data)

  # Make sure our data is returned in 30 minute increments
  expected_valid_from = period_from
  for item in consumption["consumptions"]:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "from" in item
    assert item["from"] == expected_valid_from
    assert "to" in item
    assert item["to"] == expected_valid_to

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