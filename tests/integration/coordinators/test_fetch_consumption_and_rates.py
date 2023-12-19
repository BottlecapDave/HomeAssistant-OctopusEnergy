from datetime import datetime, timedelta
import pytest

from integration import (create_consumption_data, create_rate_data, get_test_context)

from custom_components.octopus_energy.coordinators.previous_consumption_and_rates import PreviousConsumptionCoordinatorResult, async_fetch_consumption_and_rates
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
@pytest.mark.parametrize("previous_data_available",[
  (True),
  (False)
])
async def test_when_next_refresh_is_in_the_past_and_electricity_sensor_then_requested_data_returned(previous_data_available):
  # Arrange
  context = get_test_context()
  client = OctopusEnergyApiClient(context["api_key"])

  sensor_identifier = context["electricity_mpan"]
  sensor_serial_number = context["electricity_serial_number"]
  is_electricity = True
  is_smart_meter = True
  tariff_code = "E-1R-SUPER-GREEN-24M-21-07-30-A"

  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  previous_data = None
  if previous_data_available == True:
    # Make our previous data for the previous period
    previous_data = PreviousConsumptionCoordinatorResult(
      current_utc_timestamp - timedelta(days=1),
      1,
      create_consumption_data(
        datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
      ),
      create_rate_data(
        datetime.strptime("2022-02-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        [1, 2]
      ),
      10.1,
    )

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  # Act
  result = await async_fetch_consumption_and_rates(
    previous_data,
    current_utc_timestamp,
    client,
    period_from,
    period_to,
    sensor_identifier,
    sensor_serial_number,
    is_electricity,
    tariff_code,
    is_smart_meter,
    fire_event
  )

  # Assert
  assert result is not None
  assert result.last_retrieved == current_utc_timestamp
  
  assert len(result.consumption) == 48

  # Make sure our data is returned in 30 minute increments
  expected_valid_from = period_from
  for item in result.consumption:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "start" in item
    assert item["start"] == expected_valid_from
    assert "end" in item
    assert item["end"] == expected_valid_to

    expected_valid_from = expected_valid_to

  assert len(result.rates) == 48

  assert result.standing_charge is not None

