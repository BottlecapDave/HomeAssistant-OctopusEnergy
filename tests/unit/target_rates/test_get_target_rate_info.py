from datetime import datetime, timedelta
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.target_rates import get_target_rate_info

@pytest.mark.asyncio
async def test_when_called_before_rates_then_not_active_returned():
  # Arrange
  rates = [
    {
      "valid_from": datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 10
    },
    {
      "valid_from": datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 5
    },
    {
      "valid_from": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 15
    }
  ]

  current_date = datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  # Act
  result = get_target_rate_info(
    current_date,
    rates
  )

  # Assert
  assert result != None
  assert result["is_active"] == False

  assert result["overall_average_cost"] == 10
  assert result["overall_min_cost"] == 5
  assert result["overall_max_cost"] == 15
  
  assert result["current_duration_in_hours"] == 0
  assert result["current_average_cost"] == None
  assert result["current_min_cost"] == None
  assert result["current_max_cost"] == None

  assert result["next_time"] == rates[0]["valid_from"]
  assert result["next_duration_in_hours"] == 1
  assert result["next_average_cost"] == 7.5
  assert result["next_min_cost"] == 5
  assert result["next_max_cost"] == 10

@pytest.mark.asyncio
@pytest.mark.parametrize("test",[
    ({
      "current_date": datetime.strptime("2022-02-09T10:15:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_current_duration_in_hours": 1.5,
      "expected_current_average_cost": 13.333333333333334,
      "expected_current_min_cost": 10,
      "expected_current_max_cost": 15,
      "expected_next_duration_in_hours": 1,
      "expected_next_average_cost": 12.5,
      "expected_next_min_cost": 5,
      "expected_next_max_cost": 20,
    }),
    ({
      "current_date": datetime.strptime("2022-02-09T12:35:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": datetime.strptime("2022-02-09T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_current_duration_in_hours": 1,
      "expected_current_average_cost": 12.5,
      "expected_current_min_cost": 5,
      "expected_current_max_cost": 20,
      "expected_next_duration_in_hours": 0.5,
      "expected_next_average_cost": 10,
      "expected_next_min_cost": 10,
      "expected_next_max_cost": 10,
    }),
    ({
      "current_date": datetime.strptime("2022-02-09T14:05:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "expected_next_time": None,
      "expected_current_duration_in_hours": 0.5,
      "expected_current_average_cost": 10,
      "expected_current_min_cost": 10,
      "expected_current_max_cost": 10,
      "expected_next_duration_in_hours": 0,
      "expected_next_average_cost": None,
      "expected_next_min_cost": None,
      "expected_next_max_cost": None,
    })
  ])
async def test_when_called_during_rates_then_active_returned(test):
  # Arrange
  rates = [
    {
      "valid_from": datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 10,
    },
    {
      "valid_from": datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 15,
    },
    {
      "valid_from": datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T11:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 15,
    },
    {
      "valid_from": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 5,
    },
    {
      "valid_from": datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T13:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 20,
    },
    {
      "valid_from": datetime.strptime("2022-02-09T14:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T14:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 10,
    }
  ]

  result = get_target_rate_info(
    test["current_date"],
    rates
  )

  # Assert
  assert result != None
  assert result["is_active"] == True

  assert result["overall_average_cost"] == 12.5
  assert result["overall_min_cost"] == 5
  assert result["overall_max_cost"] == 20
  
  assert result["current_duration_in_hours"] == test["expected_current_duration_in_hours"]
  assert result["current_average_cost"] == test["expected_current_average_cost"]
  assert result["current_min_cost"] == test["expected_current_min_cost"]
  assert result["current_max_cost"] == test["expected_current_max_cost"]

  assert result["next_time"] == test["expected_next_time"]
  assert result["next_duration_in_hours"] == test["expected_next_duration_in_hours"]
  assert result["next_average_cost"] == test["expected_next_average_cost"]
  assert result["next_min_cost"] == test["expected_next_min_cost"]
  assert result["next_max_cost"] == test["expected_next_max_cost"]

@pytest.mark.asyncio
async def test_when_called_after_rates_then_not_active_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1, 0.2]

  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )

  current_date = period_to + timedelta(minutes=15)

  # Act
  result = get_target_rate_info(
    current_date,
    rates
  )

  # Assert
  assert result != None
  assert result["is_active"] == False
  assert result["next_time"] == None

  assert result["overall_average_cost"] == 0.15
  assert result["overall_min_cost"] == 0.1
  assert result["overall_max_cost"] == 0.2

  assert result["current_average_cost"] == None
  assert result["current_min_cost"] == None
  assert result["current_max_cost"] == None

  assert result["next_average_cost"] == None
  assert result["next_min_cost"] == None
  assert result["next_max_cost"] == None

@pytest.mark.asyncio
async def test_when_offset_set_then_active_at_correct_current_time():
  # Arrange
  offset = "-01:00:00"

  rates = [
    {
      "valid_from": datetime.strptime("2022-02-09T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 10,
    },
    {
      "valid_from": datetime.strptime("2022-02-09T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 15,
    },
    {
      "valid_from": datetime.strptime("2022-02-09T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "valid_to":  datetime.strptime("2022-02-09T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      "value_inc_vat": 5,
    }
  ]

  # Check where we're before the offset
  current_date = rates[0]["valid_from"] - timedelta(hours=1, minutes=1)

  result = get_target_rate_info(
    current_date,
    rates,
    offset
  )

  assert result != None
  assert result["is_active"] == False
  assert result["next_time"] == datetime.strptime("2022-02-09T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert result["overall_average_cost"] == 10
  assert result["overall_min_cost"] == 5
  assert result["overall_max_cost"] == 15

  assert result["current_average_cost"] == None
  assert result["current_min_cost"] == None
  assert result["current_max_cost"] == None

  assert result["next_average_cost"] == 12.5
  assert result["next_min_cost"] == 10
  assert result["next_max_cost"] == 15

  # Check where's within our rates and our offset
  for minutes_to_add in range(60):
    current_date = rates[0]["valid_from"] - timedelta(hours=1) + timedelta(minutes=minutes_to_add)

    result = get_target_rate_info(
      current_date,
      rates,
      offset
    )

    assert result != None
    assert result["is_active"] == True
    assert result["next_time"] is not None

    assert result["overall_average_cost"] == 10
    assert result["overall_min_cost"] == 5
    assert result["overall_max_cost"] == 15

    assert result["current_average_cost"] == 12.5
    assert result["current_min_cost"] == 10
    assert result["current_max_cost"] == 15

    assert result["next_average_cost"] == 5
    assert result["next_min_cost"] == 5
    assert result["next_max_cost"] == 5

  # Check when within rate but after offset
  current_date = rates[0]["valid_from"] - timedelta(hours=1) + timedelta(minutes=61)

  result = get_target_rate_info(
    current_date,
    rates,
    offset
  )

  assert result != None
  assert result["is_active"] == False
  assert result["next_time"] == datetime.strptime("2022-02-09T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert result["overall_average_cost"] == 10
  assert result["overall_min_cost"] == 5
  assert result["overall_max_cost"] == 15

  assert result["current_average_cost"] == None
  assert result["current_min_cost"] == None
  assert result["current_max_cost"] == None

  assert result["next_average_cost"] == 5
  assert result["next_min_cost"] == 5
  assert result["next_max_cost"] == 5

@pytest.mark.asyncio
async def test_when_current_date_is_equal_to_last_end_date_then_not_active():
  # Arrange
  period_from = datetime.strptime("2022-10-09T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-10-09T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_rates = [0.1]
  rates = create_rate_data(
    period_from,
    period_to,
    expected_rates
  )

  current_date = datetime.strptime("2022-10-09T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

  result = get_target_rate_info(
    current_date,
    rates,
    None
  )

  assert result != None
  assert result["is_active"] == False
  assert result["next_time"] == None

  assert result["overall_average_cost"] == 0.1
  assert result["overall_min_cost"] == 0.1
  assert result["overall_max_cost"] == 0.1

  assert result["current_average_cost"] == None
  assert result["current_min_cost"] == None
  assert result["current_max_cost"] == None

  assert result["next_average_cost"] == None
  assert result["next_min_cost"] == None
  assert result["next_max_cost"] == None