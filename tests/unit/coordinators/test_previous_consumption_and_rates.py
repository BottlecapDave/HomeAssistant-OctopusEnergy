from datetime import datetime, timedelta
from custom_components.octopus_energy.coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult
from custom_components.octopus_energy.storage.intelligent_dispatches_history import IntelligentDispatchesHistory
import pytest
import mock

from unit import (create_consumption_data, create_rate_data)

from custom_components.octopus_energy.coordinators.previous_consumption_and_rates import PreviousConsumptionCoordinatorResult, async_fetch_consumption_and_rates
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.intelligent_device import IntelligentDevice

from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatches, SimpleIntelligentDispatchItem
from custom_components.octopus_energy.const import EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES, EVENT_GAS_PREVIOUS_CONSUMPTION_RATES

sensor_identifier = "ABC123"
sensor_serial_number = "123456"

default_electricity_tariff_code = "E-1R-SUPER-GREEN-24M-21-07-30-A"
default_gas_tariff_code = "G-1R-SUPER-GREEN-24M-21-07-30-A"
default_electricity_product_code = "SUPER-GREEN-24M-21-07-30"
default_gas_product_code = "SUPER-GREEN-24M-21-07-30"

def get_account_info(current: datetime,
                     electricity_product_code = default_electricity_product_code,
                     electricity_tariff_code = default_electricity_tariff_code,
                     gas_product_code = default_gas_product_code,
                     gas_tariff_code = default_gas_tariff_code):
  return {
    "electricity_meter_points": [
      {
        "mpan": sensor_identifier,
        "meters": [
          {
            "serial_number": sensor_serial_number
          }
        ],
        "agreements": [
          {
            "start": (current + timedelta(days=7)).isoformat(),
            "end": (current + timedelta(days=14)).isoformat(),
            "tariff_code": "E-1R-FUTURE-TARIFF-A",
            "product_code": "FUTURE-TARIFF"
          },
          {
            "start": (current - timedelta(days=7)).isoformat(),
            "end": (current + timedelta(days=7)).isoformat(),
            "tariff_code": electricity_tariff_code,
            "product_code": electricity_product_code
          },
          {
            "start": (current - timedelta(days=14)).isoformat(),
            "end": (current - timedelta(days=7)).isoformat(),
            "tariff_code": "E-1R-AGILE-TARIFF-A",
            "product_code": "AGILE-TARIFF"
          }
        ]
      }
    ],
    "gas_meter_points": [
      {
        "mprn": sensor_identifier,
        "meters": [
          {
            "serial_number": sensor_serial_number
          }
        ],
        "agreements": [
          {
            "start": (current + timedelta(days=7)).isoformat(),
            "end": (current + timedelta(days=14)).isoformat(),
            "tariff_code": "G-1R-FUTURE-TARIFF-A",
            "product_code": "FUTURE-TARIFF"
          },
          {
            "start": (current - timedelta(days=7)).isoformat(),
            "end": (current + timedelta(days=7)).isoformat(),
            "tariff_code": gas_tariff_code,
            "product_code": gas_product_code
          },
          {
            "start": (current - timedelta(days=14)).isoformat(),
            "end": (current - timedelta(days=7)).isoformat(),
            "tariff_code": "G-1R-AGILE-TARIFF-A",
            "product_code": "AGILE-TARIFF"
          }
        ]
      }
    ]
  }

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
@pytest.mark.parametrize("is_electricity",[
  (True),
  (False)
])
async def test_when_when_account_is_none_then_previous_data_returned(is_electricity: bool):
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")

  is_smart_meter = True

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  account_info = None

  previous_data = PreviousConsumptionCoordinatorResult(
    current_utc_timestamp,
    1,
    [],
    [],
    None,
    datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )

  # Act
  result = await async_fetch_consumption_and_rates(
    previous_data,
    current_utc_timestamp,
    account_info,
    client,
    sensor_identifier,
    sensor_serial_number,
    is_electricity,
    is_smart_meter,
    fire_event
  )

  # Assert
  assert result == previous_data

  assert len(actual_fired_events) == 0

@pytest.mark.asyncio
async def test_when_when_next_refresh_is_in_the_future_and_previous_data_is_available_then_previous_data_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")

  is_electricity = False
  is_smart_meter = True
  
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None
  
  current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

  account_info = get_account_info(period_from)

  previous_data = PreviousConsumptionCoordinatorResult(
    current_utc_timestamp,
    1,
    [],
    [],
    None,
    datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  )

  # Act
  result = await async_fetch_consumption_and_rates(
    previous_data,
    current_utc_timestamp,
    account_info,
    client,
    sensor_identifier,
    sensor_serial_number,
    is_electricity,
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
  
  requested_rate_tariff_code = None
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  async def async_mocked_get_gas_rates(*args, **kwargs):
    nonlocal requested_rate_tariff_code

    requested_client, requested_rate_product_code, requested_rate_tariff_code, period_from, period_to = args
    return expected_rates
  
  expected_standing_charge = 100.2
  requested_standing_charge_tariff_code = None
  async def async_mocked_get_gas_standing_charge(*args, **kwargs):
    nonlocal requested_standing_charge_tariff_code

    requested_client, requested_standing_charge_product_code, requested_standing_charge_tariff_code, period_from, period_to = args
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

    is_electricity = False
    is_smart_meter = True
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from)
    
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
        10.1,
        datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
      )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp

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
  
  assert requested_rate_tariff_code == default_gas_tariff_code
  assert requested_standing_charge_tariff_code == default_gas_tariff_code

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
  
  requested_rate_tariff_code = None
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal requested_rate_tariff_code

    requested_client, requested_product_code, requested_rate_tariff_code, is_smart_meter, period_from, period_to = args
    return expected_rates
  
  expected_standing_charge = 100.2
  requested_standing_charge_tariff_code = None
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal requested_standing_charge_tariff_code

    requested_client, requested_standing_charge_product_code, requested_standing_charge_tariff_code, period_from, period_to = args
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

    is_electricity = True
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from)

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
        10.1,
        datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
      )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp

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
    
    assert requested_rate_tariff_code == default_electricity_tariff_code
    assert requested_standing_charge_tariff_code == default_electricity_tariff_code

@pytest.mark.asyncio
async def test_when_retrieving_gas_and_next_refresh_is_in_the_past_and_returned_data_is_empty_then_previous_data_returned():
  # Arrange
  async def async_mocked_get_gas_rates(*args, **kwargs):
    return []

  async def async_mocked_get_gas_consumption(*args, **kwargs):
    return []
  
  async def async_mocked_get_gas_standing_charge(*args, **kwargs):
    return None
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_gas_rates=async_mocked_get_gas_rates, async_get_gas_consumption=async_mocked_get_gas_consumption, async_get_gas_standing_charge=async_mocked_get_gas_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")

    is_electricity = False
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    previous_period_from = datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    previous_period_to = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from)

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp
    assert result.consumption == previous_data.consumption
    assert result.rates == previous_data.rates
    assert result.standing_charge == previous_data.standing_charge

    assert len(actual_fired_events) == 0

@pytest.mark.asyncio
async def test_when_retrieving_electricity_and_next_refresh_is_in_the_past_and_returned_data_is_empty_then_previous_data_returned():
  # Arrange
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    return []

  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    return []
  
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    return None
  
  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates, async_get_electricity_consumption=async_mocked_get_electricity_consumption, async_get_electricity_standing_charge=async_mocked_get_electricity_standing_charge):
    client = OctopusEnergyApiClient("NOT_REAL")

    is_electricity = True
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

    previous_period_from = datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    previous_period_to = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from)

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    store = {
      f'{sensor_identifier}_{sensor_serial_number}_previous_consumption': previous_data
    }

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp
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

    is_electricity = True
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from)

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp
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

    is_electricity = True
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from)

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp
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

    is_electricity = True
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from)

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp
    assert result.consumption == previous_data.consumption
    assert result.rates == previous_data.rates
    assert result.standing_charge == previous_data.standing_charge

    assert len(actual_fired_events) == 0

@pytest.mark.asyncio
async def test_when_started_intelligent_dispatches_available_then_adjusted_requested_data_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    return create_consumption_data(period_from, period_to)
  
  expected_rates = (
    create_rate_data(period_from, datetime.strptime("2022-02-28T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), [1]) +
    create_rate_data(datetime.strptime("2022-02-28T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), period_to, [2])
  )
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

    is_electricity = True
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from, electricity_product_code="INTELLI-BB-VAR-23-03-01", electricity_tariff_code="E-1R-INTELLI-BB-VAR-23-03-01-C")

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    intelligent_dispatches = IntelligentDispatches(
      "SMART_CONTROL_IN_PROGRESS",
      [],
      [],
      [
        SimpleIntelligentDispatchItem(
          datetime.strptime("2022-02-28T07:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
          datetime.strptime("2022-02-28T08:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
        )
      ]
    )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event,
      { "1": IntelligentDispatchesCoordinatorResult(current_utc_timestamp, 1, intelligent_dispatches, IntelligentDispatchesHistory([]), 0, current_utc_timestamp) }
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp

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

    assert len(result.rates) == len(expected_rates)
    for index, rate in enumerate(result.rates):
      if rate["start"] >= intelligent_dispatches.started[0].start and rate["end"] <= intelligent_dispatches.started[0].end:
        assert result.rates[index]["start"] == expected_rates[index]["start"]
        assert result.rates[index]["end"] == expected_rates[index]["end"]
        assert result.rates[index]["value_inc_vat"] == 1
        assert result.rates[index]["is_intelligent_adjusted"] == True
      else:
        assert result.rates[index] == expected_rates[index]
    
    assert result.standing_charge == expected_standing_charge

    assert len(actual_fired_events) == 1
    assert_raised_events(actual_fired_events,
                         EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES,
                         period_from,
                         period_to,
                         "mpan",
                         sensor_identifier)
    
@pytest.mark.asyncio
async def test_when_intelligent_tariff_and_intelligent_device_and_no_dispatches_available_then_previous_result_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    return create_consumption_data(period_from, period_to)
  
  expected_rates = (
    create_rate_data(period_from, datetime.strptime("2022-02-28T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), [1]) +
    create_rate_data(datetime.strptime("2022-02-28T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), period_to, [2])
  )
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

    is_electricity = True
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from, electricity_product_code="INTELLI-BB-VAR-23-03-01", electricity_tariff_code="E-1R-INTELLI-BB-VAR-23-03-01-C")

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    intelligent_dispatches = None

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event,
      intelligent_dispatches
    )

    # Assert
    assert result == previous_data
    assert len(actual_fired_events) == 0

@pytest.mark.asyncio
async def test_when_intelligent_tariff_and_no_dispatches_available_then_rates_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    return create_consumption_data(period_from, period_to)
  
  expected_rates = (
    create_rate_data(period_from, datetime.strptime("2022-02-28T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), [1]) +
    create_rate_data(datetime.strptime("2022-02-28T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), period_to, [2])
  )
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

    is_electricity = True
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from, electricity_product_code="INTELLI-BB-VAR-23-03-01", electricity_tariff_code="E-1R-INTELLI-BB-VAR-23-03-01-C")

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    intelligent_dispatches = { "1": IntelligentDispatchesCoordinatorResult(current_utc_timestamp, 1, IntelligentDispatches(None, [], [], []), IntelligentDispatchesHistory([]), 0, current_utc_timestamp) }

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event,
      intelligent_dispatches
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp

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

    assert len(result.rates) == len(expected_rates)
    for index, rate in enumerate(result.rates):
      assert result.rates[index] == expected_rates[index]
    
    assert result.standing_charge == expected_standing_charge

    assert len(actual_fired_events) == 1
    assert_raised_events(actual_fired_events,
                         EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES,
                         period_from,
                         period_to,
                         "mpan",
                         sensor_identifier)

@pytest.mark.asyncio
async def test_when_electricity_tariff_not_found_then_previous_result_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  consumption_called = False
  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    nonlocal consumption_called
    consumption_called = True
    return create_consumption_data(period_from, period_to)
  
  rates_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal rates_called
    rates_called = True
    return []
  
  standing_charge_called = False
  expected_standing_charge = 100.2
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal standing_charge_called
    standing_charge_called = True
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

    is_electricity = True
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-04-01T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(current_utc_timestamp)

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result == previous_data
    assert len(actual_fired_events) == 0

    assert consumption_called == True
    assert rates_called == False
    assert standing_charge_called == False

@pytest.mark.asyncio
async def test_when_gas_tariff_not_found_then_previous_result_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  consumption_called = False
  async def async_mocked_get_gas_consumption(*args, **kwargs):
    nonlocal consumption_called
    consumption_called = True
    return create_consumption_data(period_from, period_to)
  
  rates_called = False
  async def async_mocked_get_gas_rates(*args, **kwargs):
    nonlocal rates_called
    rates_called = True
    return []
  
  standing_charge_called = False
  expected_standing_charge = 100.2
  async def async_mocked_get_gas_standing_charge(*args, **kwargs):
    nonlocal standing_charge_called
    standing_charge_called = True
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

    is_electricity = False
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-04-01T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(current_utc_timestamp)

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result == previous_data
    assert len(actual_fired_events) == 0

    assert consumption_called == True
    assert rates_called == False
    assert standing_charge_called == False

@pytest.mark.asyncio
async def test_when_electricity_exception_raised_then_previous_result_returned_and_exception_captured():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  consumption_called = False
  raised_exception = RequestException("foo", [])
  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    nonlocal consumption_called
    consumption_called = True
    raise raised_exception
  
  rates_called = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal rates_called
    rates_called = True
    return []
  
  standing_charge_called = False
  expected_standing_charge = 100.2
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal standing_charge_called
    standing_charge_called = True
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

    is_electricity = True
    is_smart_meter = True
    
    current_utc_timestamp = datetime.strptime(f'2022-04-01T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(current_utc_timestamp)

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
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.historic_weekday_consumption == previous_data.historic_weekday_consumption
    assert result.historic_weekend_consumption == previous_data.historic_weekend_consumption
    assert result.consumption == previous_data.consumption
    assert result.rates == previous_data.rates
    assert result.standing_charge == previous_data.standing_charge
    assert result.last_evaluated == previous_data.last_evaluated
    assert result.request_attempts == previous_data.request_attempts + 1
    assert result.next_refresh == previous_data.next_refresh + timedelta(minutes=1)
    assert result.last_error == raised_exception

    assert len(actual_fired_events) == 0

    assert consumption_called == True
    assert rates_called == False
    assert standing_charge_called == False

@pytest.mark.asyncio
async def test_when_electricity_previous_rates_are_same_as_consumption_then_rates_not_re_retrieved():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  expected_consumption = create_consumption_data(period_from, period_to)
  async def async_mocked_get_electricity_consumption(*args, **kwargs):
    nonlocal expected_consumption
    return expected_consumption
  
  get_rates_called = False
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal get_rates_called
    get_rates_called = True

    requested_client, requested_product_code, requested_rate_tariff_code, is_smart_meter, period_from, period_to = args
    return expected_rates
  
  expected_standing_charge = 100.2
  get_standing_charge_called = False
  async def async_mocked_get_electricity_standing_charge(*args, **kwargs):
    nonlocal get_standing_charge_called
    get_standing_charge_called = True

    requested_client, requested_standing_charge_product_code, requested_standing_charge_tariff_code, period_from, period_to = args
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

    is_electricity = True
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from)

    previous_data = PreviousConsumptionCoordinatorResult(
      current_utc_timestamp - timedelta(days=1),
      1,
      create_consumption_data(
        datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
      ),
      create_rate_data(
        period_from,
        period_to,
        [1, 2]
      ),
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp

    assert result.consumption == expected_consumption

    assert result.rates == previous_data.rates
    
    assert result.standing_charge == previous_data.standing_charge

    assert len(actual_fired_events) == 1
    assert_raised_events(actual_fired_events,
                         EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES,
                         period_from,
                         period_to,
                         "mpan",
                         sensor_identifier)
    
    assert get_rates_called == False
    assert get_standing_charge_called == False

@pytest.mark.asyncio
async def test_when_gas_previous_rates_are_same_as_consumption_then_rates_not_re_retrieved():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  expected_consumption = create_consumption_data(period_from, period_to)
  async def async_mocked_get_gas_consumption(*args, **kwargs):
    nonlocal expected_consumption
    return expected_consumption
  
  get_rates_called = False
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  async def async_mocked_get_gas_rates(*args, **kwargs):
    nonlocal get_rates_called
    get_rates_called = True

    requested_client, requested_product_code, requested_rate_tariff_code, is_smart_meter, period_from, period_to = args
    return expected_rates
  
  expected_standing_charge = 100.2
  get_standing_charge_called = False
  async def async_mocked_get_gas_standing_charge(*args, **kwargs):
    nonlocal get_standing_charge_called
    get_standing_charge_called = True

    requested_client, requested_standing_charge_product_code, requested_standing_charge_tariff_code, period_from, period_to = args
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

    is_electricity = False
    is_smart_meter = True

    period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    current_utc_timestamp = datetime.strptime(f'2022-02-12T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")

    account_info = get_account_info(period_from)

    previous_data = PreviousConsumptionCoordinatorResult(
      current_utc_timestamp - timedelta(days=1),
      1,
      create_consumption_data(
        datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
        datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
      ),
      create_rate_data(
        period_from,
        period_to,
        [1, 2]
      ),
      10.1,
      datetime.strptime("2022-02-10T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    )

    # Act
    result = await async_fetch_consumption_and_rates(
      previous_data,
      current_utc_timestamp,
      account_info,
      client,
      sensor_identifier,
      sensor_serial_number,
      is_electricity,
      is_smart_meter,
      fire_event
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp

    assert result.consumption == expected_consumption

    assert result.rates == previous_data.rates
    
    assert result.standing_charge == previous_data.standing_charge

    assert len(actual_fired_events) == 1
    assert_raised_events(actual_fired_events,
                         EVENT_GAS_PREVIOUS_CONSUMPTION_RATES,
                         period_from,
                         period_to,
                         "mprn",
                         sensor_identifier)
    
    assert get_rates_called == False
    assert get_standing_charge_called == False