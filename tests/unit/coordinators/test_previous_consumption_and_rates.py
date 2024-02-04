from datetime import datetime, timedelta
from custom_components.octopus_energy.const import EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES, EVENT_GAS_PREVIOUS_CONSUMPTION_RATES
import pytest
import mock

from unit import (create_consumption_data, create_rate_data)

from custom_components.octopus_energy.coordinators.previous_consumption_and_rates import PreviousConsumptionCoordinatorResult, async_fetch_consumption_and_rates
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
1,

sensor_serial_number = "123456"

def assert_raised_events(
  raised_events: dict,
  expected_event_name: str,
  expected_valid_from: datetime,
  expected_valid_to: datetime,
  expected_identifier: str,
  expected_identifier_value: str
):
  assert expected_event_name in raised_events
  assert expected_identifier in raised_events[expected_event_name]
  assert raised_events[expected_event_name][expected_identifier] == expected_identifier_value
  assert "serial_number" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["serial_number"] == sensor_serial_number
  assert "rates" in raised_events[expected_event_name]
  assert len(raised_events[expected_event_name]["rates"]) > 2
  assert "start" in raised_events[expected_event_name]["rates"][0]
  assert raised_events[expected_event_name]["rates"][0]["start"] == expected_valid_from
  assert "end" in raised_events[expected_event_name]["rates"][-1]
  assert raised_events[expected_event_name]["rates"][-1]["end"] == expected_valid_to

  rates: list = raised_events[expected_event_name]["rates"]
  rates.sort(key=lambda rate: rate["value_inc_vat"])
  expected_min_rate = rates[0]["value_inc_vat"]
  rates.sort(key=lambda rate: rate["value_inc_vat"], reverse=True)
  expected_max_rate = rates[0]["value_inc_vat"]
  expected_average = sum(map(lambda rate: rate["value_inc_vat"], rates)) / len(rates)
  
  assert "min_rate" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["min_rate"] == expected_min_rate
  assert "max_rate" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["max_rate"] == expected_max_rate
  assert "average_rate" in raised_events[expected_event_name]
  assert raised_events[expected_event_name]["average_rate"] ==round(expected_average, 8)

@pytest.mark.asyncio
async def test_when_when_next_refresh_is_in_the_future_and_previous_data_is_available_then_previous_data_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")

  sensor_identifier = "ABC123"
  is_electricity = False
  tariff_code = "AB-123"
  is_smart_meter = True
  
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  previous_data = PreviousConsumptionCoordinatorResult(
    current_utc_timestamp,
    1,
    [],
    [],
    None
  )

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
  assert result == previous_data

  assert len(actual_fired_events) == 0

@pytest.mark.asyncio
@pytest.mark.parametrize("previous_data_available",[
  (True),
  (False)
])
async def test_when_next_refresh_is_in_the_past_and_gas_sensor_then_requested_data_returned(previous_data_available):
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  async def async_mocked_get_gas_consumption(*args, **kwargs):
    return create_consumption_data(period_from, period_to)
  
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  async def async_mocked_get_gas_rates(*args, **kwargs):
    return expected_rates
  
  expected_standing_charge = 100.2
  async def async_mocked_get_gas_standing_charge(*args, **kwargs):
    return {
      "value_inc_vat": expected_standing_charge
    }
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_consumption=async_mocked_get_gas_consumption, async_get_gas_rates=async_mocked_get_gas_rates, async_get_gas_standing_charge=async_mocked_get_gas_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")

    sensor_identifier = "ABC123"
    is_electricity = False
    tariff_code = "AB-123"
    is_smart_meter = True
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    
    previous_data = None
    if previous_data_available == True:
      # Make our previous data for the previous period
      previous_data = PreviousConsumptionCoordinatorResult(
        current_utc_timestamp - timedelta(days=1),
        1,
        create_consumption_data(
          datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
        ),
        create_rate_data(
          datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          [1, 2]
        ),
        10.1
      )

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

    assert result.rates == expected_rates

    assert result.standing_charge == expected_standing_charge

  assert len(actual_fired_events) == 1
  assert_raised_events(actual_fired_events,
                       EVENT_GAS_PREVIOUS_CONSUMPTION_RATES,
                       period_from,
                       period_to,
                       "mprn",
                       sensor_identifier)

@pytest.mark.asyncio
@pytest.mark.parametrize("previous_data_available",[
  (True),
  (False),
])
async def test_when_next_refresh_is_in_the_past_and_electricity_sensor_then_requested_data_returned(previous_data_available):
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    return create_consumption_data(period_from, period_to)
  
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    return expected_rates
  
  expected_standing_charge = 100.2
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    return {
      "value_inc_vat": expected_standing_charge
    }
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_consumption=async_mocked_get_electricity_consumption, async_get_electricity_rates=async_mocked_get_electricity_rates, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")

    sensor_identifier = "ABC123"
    is_electricity = True
    tariff_code = "AB-123"
    is_smart_meter = True

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
          datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
        ),
        create_rate_data(
          datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          [1, 2]
        ),
        10.1
      )

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

    assert result.rates == expected_rates
    
    assert result.standing_charge == expected_standing_charge

    assert len(actual_fired_events) == 1
    assert_raised_events(actual_fired_events,
                         EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES,
                         period_from,
                         period_to,
                         "mpan",
                         sensor_identifier)

@pytest.mark.asyncio
async def test_when_retrieving_gas_and_next_refresh_is_in_the_past_and_returned_data_is_empty_then_previous_data_returned():
  # Arrange
  async def async_mocked_get_gas_consumption(*args, **kwargs):
    return []
  
  async def async_mocked_get_gas_standing_charge(*args, **kwargs):
    return None
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_consumption=async_mocked_get_gas_consumption, async_get_gas_standing_charge=async_mocked_get_gas_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")

    sensor_identifier = "ABC123"
    is_electricity = False
    tariff_code = "AB-123"
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    previous_period_from = datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    previous_period_to = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    previous_data = PreviousConsumptionCoordinatorResult(
      current_utc_timestamp - timedelta(days=1),
      1,
      create_consumption_data(
        previous_period_from,
        previous_period_to
      ),
      create_rate_data(
        previous_period_from,
        previous_period_to,
        [1, 2]
      ),
      10.1
    )

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
    assert result.last_retrieved == previous_data.last_retrieved
    assert result.consumption == previous_data.consumption
    assert result.rates == previous_data.rates
    assert result.standing_charge == previous_data.standing_charge

    assert len(actual_fired_events) == 0

@pytest.mark.asyncio
async def test_when_retrieving_electricity_and_next_refresh_is_in_the_past_and_returned_data_is_empty_then_previous_data_returned():
  # Arrange
  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    return []
  
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    return None
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_consumption=async_mocked_get_electricity_consumption, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")

    sensor_identifier = "ABC123"
    is_electricity = True
    tariff_code = "AB-123"
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    previous_period_from = datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    previous_period_to = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    previous_data = PreviousConsumptionCoordinatorResult(
      current_utc_timestamp - timedelta(days=1),
      1,
      create_consumption_data(
        previous_period_from,
        previous_period_to
      ),
      create_rate_data(
        previous_period_from,
        previous_period_to,
        [1, 2]
      ),
      10.1
    )

    store = {
      f'{sensor_identifier}_{sensor_serial_number}_previous_consumption': previous_data
    }

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
    assert result.last_retrieved == previous_data.last_retrieved
    assert result.consumption == previous_data.consumption
    assert result.rates == previous_data.rates
    assert result.standing_charge == previous_data.standing_charge

    assert len(actual_fired_events) == 0

@pytest.mark.asyncio
async def test_when_not_enough_consumption_returned_then_previous_data_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    return create_consumption_data(period_from, period_to)[:2]
  
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    return expected_rates
  
  expected_standing_charge = 100.2
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    return {
      "value_inc_vat": expected_standing_charge
    }
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_consumption=async_mocked_get_electricity_consumption, async_get_electricity_rates=async_mocked_get_electricity_rates, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")

    sensor_identifier = "ABC123"
    is_electricity = True
    tariff_code = "AB-123"
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    # Make our previous data for the previous period
    previous_data = PreviousConsumptionCoordinatorResult(
      current_utc_timestamp,
      1,
      create_consumption_data(
        datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
      ),
      create_rate_data(
        datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        [1, 2]
      ),
      10.1
    )

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
    assert result.consumption == previous_data.consumption
    assert result.rates == previous_data.rates
    assert result.standing_charge == previous_data.standing_charge

    assert len(actual_fired_events) == 0

@pytest.mark.asyncio
async def test_when_electricity_and_consumption_data_spans_multiple_days_then_previous_data_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-28T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    return create_consumption_data(period_from, period_to)[:2]
  
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    return expected_rates
  
  expected_standing_charge = 100.2
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    return {
      "value_inc_vat": expected_standing_charge
    }
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_consumption=async_mocked_get_electricity_consumption, async_get_electricity_rates=async_mocked_get_electricity_rates, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")

    sensor_identifier = "ABC123"
    is_electricity = True
    tariff_code = "AB-123"
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    # Make our previous data for the previous period
    previous_data = PreviousConsumptionCoordinatorResult(
      current_utc_timestamp,
      1,
      create_consumption_data(
        datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
      ),
      create_rate_data(
        datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        [1, 2]
      ),
      10.1
    )

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
    assert result.consumption == previous_data.consumption
    assert result.rates == previous_data.rates
    assert result.standing_charge == previous_data.standing_charge

    assert len(actual_fired_events) == 0

@pytest.mark.asyncio
async def test_when_gas_and_consumption_data_spans_multiple_days_then_previous_data_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-28T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  async def async_mocked_get_gas_consumption(*args, **kwargs):
    return create_consumption_data(period_from, period_to)[:2]
  
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  async def async_mocked_get_gas_rates(*args, **kwargs):
    return expected_rates
  
  expected_standing_charge = 100.2
  async def async_mocked_get_gas_standing_charge(*args, **kwargs):
    return {
      "value_inc_vat": expected_standing_charge
    }
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_consumption=async_mocked_get_gas_consumption, async_get_gas_rates=async_mocked_get_gas_rates, async_get_gas_standing_charge=async_mocked_get_gas_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")

    sensor_identifier = "ABC123"
    is_electricity = True
    tariff_code = "AB-123"
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    # Make our previous data for the previous period
    previous_data = PreviousConsumptionCoordinatorResult(
      current_utc_timestamp,
      1,
      create_consumption_data(
        datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
      ),
      create_rate_data(
        datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        [1, 2]
      ),
      10.1
    )

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
    assert result.consumption == previous_data.consumption
    assert result.rates == previous_data.rates
    assert result.standing_charge == previous_data.standing_charge

    assert len(actual_fired_events) == 0