from datetime import datetime, timedelta
import pytest

from custom_components.octopus_energy.utils.requests import calculate_next_refresh

@pytest.mark.asyncio
@pytest.mark.parametrize("request_attempts,expected_next_refresh",[
  (1, datetime.strptime("2023-07-14T10:35:01+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (2, datetime.strptime("2023-07-14T10:36:01+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (3, datetime.strptime("2023-07-14T10:38:01+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (4, datetime.strptime("2023-07-14T10:41:01+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (5, datetime.strptime("2023-07-14T10:45:01+01:00", "%Y-%m-%dT%H:%M:%S%z"))
])
async def test_when_data_provided_then_expected_rate_is_returned(request_attempts, expected_next_refresh):
  # Arrange
  refresh_rate_in_minutes = 5
  request_datetime = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  current = request_datetime + timedelta(minutes=refresh_rate_in_minutes) + timedelta(minutes=request_attempts - 1)
  
  # Act
  next_refresh = calculate_next_refresh(request_datetime, request_attempts, refresh_rate_in_minutes)

  # Assert
  assert next_refresh == expected_next_refresh
  assert current <= next_refresh