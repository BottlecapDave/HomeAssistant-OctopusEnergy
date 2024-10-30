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
    10.1
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
    10.1
  )
  identifier = "identifier"
  serial_number = "serial_number"

  load_called = False
  async def async_load_historic_consumptions(identifer, serial_number, is_weekday):
    nonlocal load_called
    load_called = True
    return []
  
  save_called = False
  async def async_save_historic_consumptions(identifer, serial_number, is_weekday, consumption):
    nonlocal save_called
    save_called = True
    return None
  
  get_electricity_consumption_called = False
  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    nonlocal get_electricity_consumption_called
    get_electricity_consumption_called = True
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

    assert save_called == False
    assert load_called == False
    assert get_electricity_consumption_called == False

@pytest.mark.asyncio
@pytest.mark.parametrize("include_historic_weekday_data,include_historic_weekend_data",[
  (True, False),
  (False, True),
])
async def test_when_data_last_updated_is_not_equal_to_previous_data_then_new_data_returned(include_historic_weekday_data: bool, include_historic_weekend_data: bool):
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
    10.1
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
    historic_weekday_consumption=create_consumption_data(datetime.strptime("2024-08-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-08-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")) if include_historic_weekday_data else None,
    historic_weekend_consumption=create_consumption_data(datetime.strptime("2024-08-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-08-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")) if include_historic_weekend_data else None
  )
  identifier = "identifier"
  serial_number = "serial_number"

  load_weekday_called = False
  load_weekend_called = False
  async def async_load_historic_consumptions(identifer, serial_number, is_weekday):
    nonlocal load_weekday_called, load_weekend_called
    if is_weekday:
      load_weekday_called = True
    else:
      load_weekend_called = True
    return create_consumption_data(datetime.strptime("2024-08-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-08-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"))
  
  saved_weekday_consumptions: list = []
  saved_weekend_consumptions: list = []
  save_weekday_called = False
  save_weekend_called = False
  async def async_save_historic_consumptions(identifer, serial_number, is_weekday, consumptions):
    nonlocal saved_weekday_consumptions, saved_weekend_consumptions, save_weekday_called, save_weekend_called
    if is_weekday:
      saved_weekday_consumptions = consumptions
      save_weekday_called = True
    else:
      saved_weekend_consumptions = consumptions
      save_weekend_called = True
    return None
  
  requested_consumptions = []
  get_electricity_consumption_called = False
  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    nonlocal requested_consumptions, get_electricity_consumption_called
    get_electricity_consumption_called = True
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
    assert save_weekday_called == True
    assert save_weekend_called == True
    assert load_weekday_called == (include_historic_weekday_data == False)
    assert load_weekend_called == (include_historic_weekend_data == False)
    assert get_electricity_consumption_called == True

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
    expected_missing_weekday_times.sort(key=lambda x: (x["start"].timestamp(), x["start"].fold))

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
    expected_missing_weekend_times.sort(key=lambda x: (x["start"].timestamp(), x["start"].fold))

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
    
@pytest.mark.asyncio
@pytest.mark.parametrize("include_historic_weekday_data,include_historic_weekend_data",[
  (True, False),
  (False, True),
])
async def test_when_no_data_is_missing_then_consumption_data_is_not_saved(include_historic_weekday_data: bool, include_historic_weekend_data: bool):
  # Arrange
  current = datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  existing_weekday_consumption_data = (
    create_consumption_data(datetime.strptime("2024-08-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-08-31T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")) +
    create_consumption_data(datetime.strptime("2024-09-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-09-07T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")) +
    create_consumption_data(datetime.strptime("2024-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-09-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")) +
    create_consumption_data(datetime.strptime("2024-09-16T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"))
  )

  existing_weekend_consumption_data = (
    create_consumption_data(datetime.strptime("2024-08-24T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-08-26T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")) +
    create_consumption_data(datetime.strptime("2024-08-31T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-09-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")) +
    create_consumption_data(datetime.strptime("2024-09-07T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")) +
    create_consumption_data(datetime.strptime("2024-09-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-09-16T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"))
  )

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
    historic_weekday_consumption=existing_weekday_consumption_data if include_historic_weekday_data else None,
    historic_weekend_consumption=existing_weekend_consumption_data if include_historic_weekend_data else None
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
    historic_weekday_consumption=existing_weekday_consumption_data if include_historic_weekday_data else None,
    historic_weekend_consumption=existing_weekend_consumption_data if include_historic_weekend_data else None
  )
  identifier = "identifier"
  serial_number = "serial_number"

  load_weekday_called = False
  load_weekend_called = False
  async def async_load_historic_consumptions(identifer, serial_number, is_weekday):
    nonlocal load_weekday_called, load_weekend_called
    if is_weekday:
      load_weekday_called = True
    else:
      load_weekend_called = True
    return create_consumption_data(datetime.strptime("2024-08-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2024-08-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"))
  
  save_weekday_called = False
  save_weekend_called = False
  async def async_save_historic_consumptions(identifer, serial_number, is_weekday, consumptions):
    nonlocal save_weekday_called, save_weekend_called
    if is_weekday:
      save_weekday_called = True
    else:
      save_weekend_called = True
    return None
  
  requested_consumptions = []
  get_electricity_consumption_called = False
  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    nonlocal requested_consumptions, get_electricity_consumption_called
    get_electricity_consumption_called = True
    requested_client, identifer, serial_number, period_from, period_to = args
    requested_consumptions.append({ "start": period_from, "end": period_to })
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
    assert save_weekday_called == (include_historic_weekday_data == False)
    assert save_weekend_called == (include_historic_weekend_data == False)
    assert load_weekday_called == (include_historic_weekday_data == False)
    assert load_weekend_called == (include_historic_weekend_data == False)
    assert get_electricity_consumption_called == True

    assert requested_consumptions is not None
    assert len(requested_consumptions) == (13 if include_historic_weekday_data == False else 0) + (7 if include_historic_weekend_data == False else 0)

    assert result.historic_weekday_consumption is not None
    assert len(result.historic_weekday_consumption) == 48 * 15

    expected_weekday_times = [
      { "start": datetime.strptime("2024-08-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-08-29T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-08-29T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-08-30T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-08-30T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-08-31T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-03T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-03T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-04T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-04T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-05T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-05T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-06T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-06T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-07T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-11T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-12T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-12T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-13T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-13T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-16T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-17T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    ]

    for i in range(len(expected_weekday_times)):
      current_start = expected_weekday_times[i]["start"]
      for j in range(48):
        assert result.historic_weekday_consumption[(i * 48) + j]["start"] == current_start
        assert result.historic_weekday_consumption[(i * 48) + j]["end"] == current_start + timedelta(minutes=30)
        current_start = current_start + timedelta(minutes=30)

    assert result.historic_weekend_consumption is not None
    assert len(result.historic_weekend_consumption) == 48 * 8

    expected_weekend_times = [
      { "start": datetime.strptime("2024-08-24T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-08-25T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-08-25T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-08-26T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-08-31T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-07T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-08T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-08T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-15T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
      { "start": datetime.strptime("2024-09-15T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), "end": datetime.strptime("2024-09-16T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z") },
    ]

    for i in range(len(expected_weekend_times)):
      current_start = expected_weekend_times[i]["start"]
      for j in range(48):
        assert result.historic_weekend_consumption[(i * 48) + j]["start"] == current_start
        assert result.historic_weekend_consumption[(i * 48) + j]["end"] == current_start + timedelta(minutes=30)
        current_start = current_start + timedelta(minutes=30)