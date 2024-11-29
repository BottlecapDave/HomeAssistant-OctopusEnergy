from datetime import (datetime, timedelta)
import pytest


from custom_components.octopus_energy.coordinators.current_consumption import CurrentConsumptionCoordinatorResult
from custom_components.octopus_energy.utils.consumption import calculate_current_consumption

consumption = [
  {
    "consumption": 10.1
  },
  {
    "consumption": 20.5
  },
  {
    "consumption": 5.3
  }
]

expected_consumption_total = 35.9

@pytest.mark.asyncio
async def test_when_previous_updated_is_none_then_none_returned():
  # Arrange
  last_retrieved = datetime.strptime("2023-08-04T10:09:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  current_date = datetime.strptime("2023-08-04T10:10:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_updated = None
  previous_total_consumption = None
  consumption_result = CurrentConsumptionCoordinatorResult(last_retrieved, 1, 30, consumption)
  current_state = None

  # Act
  result = calculate_current_consumption(
    current_date,
    consumption_result,
    current_state,
    previous_updated,
    previous_total_consumption
  )

  # Assert
  assert result is not None
  assert result.state is None
  assert result.total_consumption == expected_consumption_total
  assert result.data_last_retrieved == last_retrieved
  assert result.last_evaluated == previous_updated

@pytest.mark.asyncio
async def test_when_consumption_data_is_not_updated_on_same_day_then_current_data_returned():
  # Arrange
  last_retrieved = datetime.strptime("2023-08-04T10:09:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  current_date = datetime.strptime("2023-08-04T10:10:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  original_previous_updated = datetime.strptime("2023-08-04T10:09:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_updated = original_previous_updated
  original_previous_total_consumption = 30.1
  previous_total_consumption = original_previous_total_consumption
  consumption_result = CurrentConsumptionCoordinatorResult(last_retrieved, 1, 30, consumption)
  original_current_state = 10.1
  current_state = original_current_state

  # Act
  for index in range(5):
    result = calculate_current_consumption(
      current_date,
      consumption_result,
      current_state,
      previous_updated,
      previous_total_consumption
    )

    current_date += timedelta(minutes=1)
    current_state = result.state
    previous_updated = result.last_evaluated
    previous_total_consumption = result.total_consumption

  # Assert
  assert result is not None
  assert result.state == original_current_state
  assert result.total_consumption == original_previous_total_consumption
  assert result.data_last_retrieved == last_retrieved
  assert result.last_evaluated == original_previous_updated

@pytest.mark.asyncio
async def test_when_consumption_data_is_updated_on_same_day_then_difference_returned():
  # Arrange
  last_retrieved = datetime.strptime("2023-08-04T10:09:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  current_date = datetime.strptime("2023-08-04T10:10:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_updated = datetime.strptime("2023-08-04T10:08:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_total_consumption = 30.1
  consumption_result = CurrentConsumptionCoordinatorResult(last_retrieved, 1, 30, consumption)
  current_state = 10.1

  # Act
  result = calculate_current_consumption(
    current_date,
    consumption_result,
    current_state,
    previous_updated,
    previous_total_consumption
  )

  # Assert
  assert result is not None
  assert result.state == expected_consumption_total - previous_total_consumption
  assert result.total_consumption == expected_consumption_total
  assert result.data_last_retrieved == last_retrieved
  assert result.last_evaluated == current_date

@pytest.mark.asyncio
async def test_when_called_on_new_date_and_consumption_data_is_not_updated_then_zero_returned():
  # Arrange
  start_of_day = datetime.strptime("2023-08-04T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  last_retrieved = datetime.strptime("2023-08-03T23:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  current_date = datetime.strptime("2023-08-04T10:10:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_updated = last_retrieved
  previous_total_consumption = 30.1
  consumption_result = CurrentConsumptionCoordinatorResult(last_retrieved, 1, 30, consumption)
  current_state = 10.1

  # Act
  for index in range(10):
    result = calculate_current_consumption(
      current_date,
      consumption_result,
      current_state,
      previous_updated,
      previous_total_consumption
    )

    current_date += timedelta(minutes=1)
    current_state = result.state
    previous_updated = result.last_evaluated
    previous_total_consumption = result.total_consumption

  # Assert
  assert result is not None
  assert result.state == 0
  assert result.total_consumption == 0
  assert result.data_last_retrieved == last_retrieved
  assert result.last_evaluated == start_of_day

@pytest.mark.asyncio
async def test_when_called_on_new_date_and_consumption_data_is_not_updated_and_then_updated_then_consumption_total_returned():
  # Arrange
  last_retrieved = datetime.strptime("2023-08-03T23:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  current_date = datetime.strptime("2023-08-04T10:10:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_updated = last_retrieved
  previous_total_consumption = 30.1
  consumption_result = CurrentConsumptionCoordinatorResult(last_retrieved, 1, 30, consumption)
  current_state = 10.1

  # Act

  # Ensure that our state is reset for a new day
  result = calculate_current_consumption(
    current_date,
    consumption_result,
    current_state,
    previous_updated,
    previous_total_consumption
  )

  current_date += timedelta(minutes=1)
  current_state = result.state
  previous_updated = result.last_evaluated
  previous_total_consumption = result.total_consumption
  consumption_result = CurrentConsumptionCoordinatorResult(result.last_evaluated + timedelta(seconds=30), 1, 30, consumption)

  # Update with new consumption data
  result = calculate_current_consumption(
    current_date,
    consumption_result,
    current_state,
    previous_updated,
    previous_total_consumption
  )

  # Assert
  assert result is not None
  assert result.state == expected_consumption_total
  assert result.total_consumption == expected_consumption_total
  assert result.data_last_retrieved == consumption_result.last_evaluated
  assert result.last_evaluated == current_date

@pytest.mark.asyncio
async def test_when_called_on_new_date_and_consumption_data_is_updated_then_consumption_total_returned():
  # Arrange
  last_retrieved = datetime.strptime("2023-08-04T10:09:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  current_date = datetime.strptime("2023-08-04T10:10:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_updated = datetime.strptime("2023-08-03T10:08:59+01:00", "%Y-%m-%dT%H:%M:%S%z")
  previous_total_consumption = 30.1
  consumption_result = CurrentConsumptionCoordinatorResult(last_retrieved, 1, 30, consumption)
  current_state = 10.1

  # Act
  result = calculate_current_consumption(
    current_date,
    consumption_result,
    current_state,
    previous_updated,
    previous_total_consumption
  )

  # Assert
  assert result is not None
  assert result.state == expected_consumption_total
  assert result.total_consumption == expected_consumption_total
  assert result.data_last_retrieved == last_retrieved
  assert result.last_evaluated == current_date