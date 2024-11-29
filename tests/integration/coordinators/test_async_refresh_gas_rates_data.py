from datetime import datetime, timedelta
import pytest
import zoneinfo

from homeassistant.util.dt import (set_default_time_zone)

from integration import (create_rate_data, get_test_context)

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.coordinators.gas_rates import GasRatesCoordinatorResult, async_refresh_gas_rates_data
from custom_components.octopus_energy.utils import Tariff

@pytest.mark.asyncio
@pytest.mark.parametrize("previous_data_available",[
  (True),
  (False)
])
async def test_when_next_refresh_is_in_the_past_and_then_requested_data_returned(previous_data_available):
  # Arrange
  context = get_test_context()
  client = OctopusEnergyApiClient(context.api_key)
  set_default_time_zone(zoneinfo.ZoneInfo("Europe/London"))

  account_info = await client.async_get_account(context.account_id)
  assert account_info is not None

  target_mprn = context.gas_mprn
  target_serial_number = context.gas_serial_number
  
  current_utc_timestamp = datetime.strptime(f'2024-11-20T10:12:00Z', "%Y-%m-%dT%H:%M:%S%z")
  current_utc_timestamp_start = current_utc_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

  existing_rates_result = None
  if previous_data_available == True:
    # Make our previous data for the previous period
    existing_rates_result = GasRatesCoordinatorResult(
      current_utc_timestamp - timedelta(days=1),
      1,
      create_rate_data(
        current_utc_timestamp_start - timedelta(days=1),
        current_utc_timestamp_start - timedelta(hours=4),
        [1]
      ),
      None
    )

  actual_fired_events = {}
  def fire_event(name, metadata):
    nonlocal actual_fired_events
    actual_fired_events[name] = metadata
    return None

  # Act
  result = await async_refresh_gas_rates_data(
    current_utc_timestamp,
    client,
    account_info,
    target_mprn,
    target_serial_number,
    existing_rates_result,
    fire_event
  )

  # Assert
  assert result is not None
  assert result.last_evaluated == current_utc_timestamp
  
  assert len(result.rates) == 48 * 3

  expected_valid_from = current_utc_timestamp.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
  for item in result.rates:
    expected_valid_to = expected_valid_from + timedelta(minutes=30)

    assert "start" in item
    assert item["start"] == expected_valid_from
    assert "end" in item
    assert item["end"] == expected_valid_to

    expected_valid_from = expected_valid_to