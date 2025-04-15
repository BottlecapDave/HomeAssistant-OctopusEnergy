from datetime import datetime, timedelta
import pytest

from custom_components.octopus_energy.utils.requests import calculate_next_refresh

@pytest.mark.asyncio
@pytest.mark.parametrize("request_attempts,expected_next_refresh",[
  (1, datetime.strptime("2023-07-14T10:35:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (2, datetime.strptime("2023-07-14T10:36:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (3, datetime.strptime("2023-07-14T10:38:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (4, datetime.strptime("2023-07-14T10:41:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (5, datetime.strptime("2023-07-14T10:45:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (6, datetime.strptime("2023-07-14T10:50:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (7, datetime.strptime("2023-07-14T10:56:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (8, datetime.strptime("2023-07-14T11:03:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (9, datetime.strptime("2023-07-14T11:11:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (10, datetime.strptime("2023-07-14T11:20:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (11, datetime.strptime("2023-07-14T11:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (12, datetime.strptime("2023-07-14T11:41:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (13, datetime.strptime("2023-07-14T11:53:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (14, datetime.strptime("2023-07-14T12:06:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (15, datetime.strptime("2023-07-14T12:20:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (16, datetime.strptime("2023-07-14T12:35:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (17, datetime.strptime("2023-07-14T12:51:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (18, datetime.strptime("2023-07-14T13:08:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (19, datetime.strptime("2023-07-14T13:26:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (20, datetime.strptime("2023-07-14T13:45:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (21, datetime.strptime("2023-07-14T14:05:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (22, datetime.strptime("2023-07-14T14:26:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (23, datetime.strptime("2023-07-14T14:48:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (24, datetime.strptime("2023-07-14T15:11:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (25, datetime.strptime("2023-07-14T15:35:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (26, datetime.strptime("2023-07-14T16:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (27, datetime.strptime("2023-07-14T16:26:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (28, datetime.strptime("2023-07-14T16:53:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (29, datetime.strptime("2023-07-14T17:21:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (30, datetime.strptime("2023-07-14T17:50:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (31, datetime.strptime("2023-07-14T18:20:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (32, datetime.strptime("2023-07-14T18:50:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (33, datetime.strptime("2023-07-14T19:20:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (34, datetime.strptime("2023-07-14T19:50:00+01:00", "%Y-%m-%dT%H:%M:%S%z"))
])
async def test_when_data_provided_then_expected_rate_is_returned(request_attempts, expected_next_refresh):
  # Arrange
  refresh_rate_in_minutes = 5
  request_datetime = datetime.strptime("2023-07-14T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  current = request_datetime + timedelta(minutes=refresh_rate_in_minutes) + timedelta(minutes=request_attempts - 1)
  
  # Act
  next_refresh = calculate_next_refresh(request_datetime, request_attempts, refresh_rate_in_minutes)

  # Assert
  assert next_refresh == expected_next_refresh
  assert current <= next_refresh