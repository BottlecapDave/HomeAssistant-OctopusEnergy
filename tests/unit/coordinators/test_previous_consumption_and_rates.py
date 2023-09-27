from datetime import datetime, timedelta
from custom_components.octopus_energy.const import EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES, EVENT_GAS_PREVIOUS_CONSUMPTION_RATES
import pytest
import mock

from unit import (create_consumption_data, create_rate_data)

from custom_components.octopus_energy.coordinators.previous_consumption_and_rates import async_fetch_consumption_and_rates
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

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
  assert "rates" in raised_events[expected_event_name]
  assert len(raised_events[expected_event_name]["rates"]) > 2
  assert "valid_from" in raised_events[expected_event_name]["rates"][0]
  assert raised_events[expected_event_name]["rates"][0]["valid_from"] == expected_valid_from
  assert "valid_to" in raised_events[expected_event_name]["rates"][-1]
  assert raised_events[expected_event_name]["rates"][-1]["valid_to"] == expected_valid_to

@pytest.mark.asyncio
async def test_when_now_is_not_at_30_minute_mark_and_previous_data_is_available_then_previous_data_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")

  sensor_identifier = "ABC123"
  sensor_serial_number = "123456"
  is_electricity = False
  tariff_code = "AB-123"
  is_smart_meter = True
  
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  previous_data = {
    "consumption": [],
    "rates": [],
    "standing_charge": None
  }

  for minute in range(0, 59):
    if (minute == 0 or minute == 30):
      continue

    actual_fired_events = {}
    def fire_event(name, metadata):
      nonlocal actual_fired_events
      actual_fired_events[name] = metadata
      return None
    
    minuteStr = f'{minute}'.zfill(2)
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minuteStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

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
@pytest.mark.parametrize("minutes",[
  (0),
  (30),
])
async def test_when_now_is_at_30_minute_mark_and_previous_data_is_in_requested_period_then_previous_data_returned(minutes):
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")

  sensor_identifier = "ABC123"
  sensor_serial_number = "123456"
  is_electricity = False
  tariff_code = "AB-123"
  is_smart_meter = True

  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  previous_data = {
    "consumption": create_consumption_data(period_from, period_to),
    "rates": create_rate_data(period_from, period_to, [1, 2]),
    "standing_charge": 10.1
  }
    
  minutesStr = f'{minutes}'.zfill(2)
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

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
  assert result == previous_data

  assert len(actual_fired_events) == 0

@pytest.mark.asyncio
@pytest.mark.parametrize("minutes,previous_data_available",[
  (0, True),
  (0, False),
  (30, True),
  (30, False),
])
async def test_when_now_is_at_30_minute_mark_and_gas_sensor_then_requested_data_returned(minutes, previous_data_available):
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
    sensor_serial_number = "123456"
    is_electricity = False
    tariff_code = "AB-123"
    is_smart_meter = True

    previous_data = None
    if previous_data_available == True:
      # Make our previous data for the previous period
      previous_data = {
        "consumption": create_consumption_data(
          datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
        ),
        "rates": create_rate_data(
          datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          [1, 2]
        ),
        "standing_charge": 10.1
      }
    
    minutesStr = f'{minutes}'.zfill(2)
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

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

    assert "consumption" in result
    assert len(result["consumption"]) == 48

    # Make sure our data is returned in 30 minute increments
    expected_valid_from = period_from
    for item in result["consumption"]:
      expected_valid_to = expected_valid_from + timedelta(minutes=30)

      assert "interval_start" in item
      assert item["interval_start"] == expected_valid_from
      assert "interval_end" in item
      assert item["interval_end"] == expected_valid_to

      expected_valid_from = expected_valid_to

    assert "rates" in result
    assert result["rates"] == expected_rates

    assert "standing_charge" in result
    assert result["standing_charge"] == expected_standing_charge

  assert len(actual_fired_events) == 1
  assert_raised_events(actual_fired_events,
                       EVENT_GAS_PREVIOUS_CONSUMPTION_RATES,
                       period_from,
                       period_to,
                       "mprn",
                       sensor_identifier)

@pytest.mark.asyncio
@pytest.mark.parametrize("minutes,previous_data_available",[
  (0, True),
  (0, False),
  (30, True),
  (30, False),
])
async def test_when_now_is_at_30_minute_mark_and_electricity_sensor_then_requested_data_returned(minutes, previous_data_available):
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
    sensor_serial_number = "123456"
    is_electricity = True
    tariff_code = "AB-123"
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    previous_data = None
    if previous_data_available == True:
      # Make our previous data for the previous period
      previous_data = {
        "consumption": create_consumption_data(
          datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
        ),
        "rates": create_rate_data(
          datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          [1, 2]
        ),
        "standing_charge": 10.1
      }
    
    minutesStr = f'{minutes}'.zfill(2)
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

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

    assert "consumption" in result
    assert len(result["consumption"]) == 48

    # Make sure our data is returned in 30 minute increments
    expected_valid_from = period_from
    for item in result["consumption"]:
      expected_valid_to = expected_valid_from + timedelta(minutes=30)

      assert "interval_start" in item
      assert item["interval_start"] == expected_valid_from
      assert "interval_end" in item
      assert item["interval_end"] == expected_valid_to

      expected_valid_from = expected_valid_to

    assert "rates" in result
    assert result["rates"] == expected_rates
    
    assert "standing_charge" in result
    assert result["standing_charge"] == expected_standing_charge

    assert len(actual_fired_events) == 1
    assert_raised_events(actual_fired_events,
                         EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES,
                         period_from,
                         period_to,
                         "mpan",
                         sensor_identifier)

@pytest.mark.asyncio
@pytest.mark.parametrize("minutes",[
  (0),
  (30),
])
async def test_when_now_is_at_30_minute_mark_and_gas_sensor_and_returned_data_is_empty_then_previous_data_returned(minutes):
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
    sensor_serial_number = "123456"
    is_electricity = False
    tariff_code = "AB-123"
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    previous_period_from = datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    previous_period_to = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    previous_data = previous_data = {
      "consumption": create_consumption_data(
        previous_period_from,
        previous_period_to
      ),
      "rates": create_rate_data(
        previous_period_from,
        previous_period_to,
        [1, 2]
      ),
      "standing_charge": 10.1
    }
    
    minutesStr = f'{minutes}'.zfill(2)
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

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
@pytest.mark.parametrize("minutes",[
  (0),
  (30),
])
async def test_when_now_is_at_30_minute_mark_and_electricity_sensor_and_returned_data_is_empty_then_previous_data_returned(minutes):
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
    sensor_serial_number = "123456"
    is_electricity = True
    tariff_code = "AB-123"
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    previous_period_from = datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    previous_period_to = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    previous_data = {
      "consumption": create_consumption_data(
        previous_period_from,
        previous_period_to
      ),
      "rates": create_rate_data(
        previous_period_from,
        previous_period_to,
        [1, 2]
      ),
      "standing_charge": 10.1
    }
    
    minutesStr = f'{minutes}'.zfill(2)
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:{minutesStr}:00Z', "%Y-%m-%dT%H:%M:%S%z")

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
    assert result == previous_data

    assert len(actual_fired_events) == 0