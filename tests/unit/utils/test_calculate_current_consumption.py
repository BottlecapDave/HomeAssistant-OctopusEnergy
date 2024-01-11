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