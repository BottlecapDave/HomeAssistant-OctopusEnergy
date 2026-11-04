from datetime import datetime
import pytest

from custom_components.octopus_energy.utils.datetime import round_up_to_nearest_half_hour

@pytest.mark.parametrize("dt,expected",[
  # Already exactly on a half hour boundary - unchanged
  (datetime.strptime("2023-07-14T10:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-14T10:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2023-07-14T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-14T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  # Not exactly on the hour once seconds/microseconds are considered - rounds up to the half hour
  (datetime.strptime("2023-07-14T10:00:00.500000+01:00", "%Y-%m-%dT%H:%M:%S.%f%z"), datetime.strptime("2023-07-14T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2023-07-14T10:00:30+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-14T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  # Within the first half of the hour - rounds up to the half hour
  (datetime.strptime("2023-07-14T10:01:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-14T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2023-07-14T10:15:30+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-14T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2023-07-14T10:29:59+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-14T10:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  # Within the second half of the hour - rounds up to the next hour
  (datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-14T11:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2023-07-14T10:30:00.500000+01:00", "%Y-%m-%dT%H:%M:%S.%f%z"), datetime.strptime("2023-07-14T11:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2023-07-14T10:31:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-14T11:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2023-07-14T10:45:15+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-14T11:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2023-07-14T10:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-14T11:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  # Crosses a day boundary
  (datetime.strptime("2023-07-14T23:45:00+01:00", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-07-15T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
])
def test_when_datetime_provided_then_rounded_up_to_nearest_half_hour(dt, expected):
  # Act
  result = round_up_to_nearest_half_hour(dt)

  # Assert
  assert result == expected
