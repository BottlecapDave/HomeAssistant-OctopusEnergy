from datetime import datetime, timedelta
from unittest import mock
import pytest

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.coordinators.previous_consumption_and_rates import PreviousConsumptionCoordinatorResult, async_enhance_with_historic_consumption
from tests.integration import create_consumption_data, create_rate_data

@pytest.mark.asyncio
async def test_when_data_last_updated_is_equal_to_previous_data_then_existing_data_returned():
  # Arrange
  current = datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  data = PreviousConsumptionCoordinatorResult(
    current - timedelta(days=1),
    1,
    create_consumption_data(
      datetime.strptime("2024-09-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    ),
    create_rate_data(
      datetime.strptime("2024-09-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      [1, 2]
    ),
    10.1,
    datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  previous_data = PreviousConsumptionCoordinatorResult(
    current - timedelta(days=1),
    1,
    create_consumption_data(
      datetime.strptime("2024-09-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    ),
    create_rate_data(
      datetime.strptime("2024-09-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      [1, 2]
    ),
    10.1,
    datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  identifier = "identifier"
  serial_number = "serial_number"

  async def async_load_historic_consumptions(identifer, serial_number, is_weekday):
    return []
  
  async def async_save_historic_consumptions(identifer, serial_number, is_weekday, consumption):
    return None
  
  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    requested_client, identifer, serial_number, period_from, period_to = args
    return create_consumption_data(period_from, period_to)

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_consumption=async_mocked_get_electricity_consumption):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_enhance_with_historic_consumption(
      current,
      client,
      data,
      previous_data,
      identifier,
      serial_number,
      async_load_historic_consumptions,
      async_save_historic_consumptions
    )

    # Assert
    assert result is not None
    assert result == data

@pytest.mark.asyncio
async def test_when_data_last_updated_is_not_equal_to_previous_data_then_new_data_returned():
  # Arrange
  current = datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  data = PreviousConsumptionCoordinatorResult(
    current - timedelta(days=1),
    1,
    create_consumption_data(
      datetime.strptime("2024-09-15T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    ),
    create_rate_data(
      datetime.strptime("2024-09-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      [1, 2]
    ),
    10.1,
    datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  previous_data = PreviousConsumptionCoordinatorResult(
    current - timedelta(days=2),
    1,
    create_consumption_data(
      datetime.strptime("2024-09-15T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    ),
    create_rate_data(
      datetime.strptime("2024-09-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
      [1, 2]
    ),
    10.1,
    datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )
  identifier = "identifier"
  serial_number = "serial_number"

  async def async_load_historic_consumptions(identifer, serial_number, is_weekday):
    return create_consumption_data(datetime.strptime("2024-08-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-08-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"))
  
  saved_weekday_consumptions: list = []
  saved_weekend_consumptions: list = []
  async def async_save_historic_consumptions(identifer, serial_number, is_weekday, consumptions):
    nonlocal saved_weekday_consumptions, saved_weekend_consumptions
    if is_weekday:
      saved_weekday_consumptions = consumptions
    else:
      saved_weekend_consumptions = consumptions
    return None
  
  requested_consumptions = []
  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    nonlocal requested_consumptions
    requested_client, identifer, serial_number, period_from, period_to = args
    requested_consumptions.append({ "start": period_from, "end": period_to })
    return create_consumption_data(period_from, period_to)
  
  expected_missing_weekday_times = [
    { "start": datetime.strptime("2024-09-13T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-12T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-13T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-12T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-06T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-07T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-05T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-06T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-04T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-05T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-03T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-04T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-03T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-08-30T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-08-31T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-08-29T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-08-30T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-08-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-08-29T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
  ]
  
  expected_missing_weekend_times = [
    { "start": datetime.strptime("2024-09-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-15T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-08T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-07T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-08T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-09-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-08-31T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-08-25T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-08-26T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    { "start": datetime.strptime("2024-08-24T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-08-25T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
  ]

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_consumption=async_mocked_get_electricity_consumption):
    client = OctopusEnergyApiClient("NOT_REAL")
    
    result = await async_enhance_with_historic_consumption(
      current,
      client,
      data,
      previous_data,
      identifier,
      serial_number,
      async_load_historic_consumptions,
      async_save_historic_consumptions
    )

    # Assert
    assert requested_consumptions is not None
    
    # Check for missing weekdays
    for i in range(len(expected_missing_weekday_times)):
      assert requested_consumptions[i]["start"] == expected_missing_weekday_times[i]["start"]
      assert requested_consumptions[i]["end"] == expected_missing_weekday_times[i]["end"]

    # Check for weekend days
    for i in range(len(expected_missing_weekend_times)):
      assert requested_consumptions[i + len(expected_missing_weekday_times)]["start"] == expected_missing_weekend_times[i]["start"]
      assert requested_consumptions[i + len(expected_missing_weekday_times)]["end"] == expected_missing_weekend_times[i]["end"]

    assert result is not None
    assert result.historic_weekday_consumption is not None
    assert len(result.historic_weekday_consumption) == 48 * 15
    expected_missing_weekday_times.sort(key=lambda x: x["start"])

    expected_weekday_times = expected_missing_weekday_times + [
      { "start": datetime.strptime("2024-09-16T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") }
    ]

    for i in range(len(expected_weekday_times)):
      current_start = expected_weekday_times[i]["start"]
      for j in range(48):
        assert result.historic_weekday_consumption[(i * 48) + j]["start"] == current_start
        assert result.historic_weekday_consumption[(i * 48) + j]["end"] == current_start + timedelta(minutes=30)
        current_start = current_start + timedelta(minutes=30)

    assert result.historic_weekend_consumption is not None
    assert len(result.historic_weekend_consumption) == 48 * 8
    expected_missing_weekend_times.sort(key=lambda x: x["start"])

    expected_weekend_times = expected_missing_weekend_times + [
      { "start": datetime.strptime("2024-09-15T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-16T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") }
    ]

    for i in range(len(expected_weekend_times)):
      current_start = expected_weekend_times[i]["start"]
      for j in range(48):
        assert result.historic_weekend_consumption[(i * 48) + j]["start"] == current_start
        assert result.historic_weekend_consumption[(i * 48) + j]["end"] == current_start + timedelta(minutes=30)
        current_start = current_start + timedelta(minutes=30)

    assert saved_weekday_consumptions == result.historic_weekday_consumption
    assert saved_weekend_consumptions == result.historic_weekend_consumption
    