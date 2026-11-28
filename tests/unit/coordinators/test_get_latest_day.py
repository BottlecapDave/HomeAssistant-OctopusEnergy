from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import mock
import pytest
from homeassistant.util import dt as dt_util

from unit import create_consumption_data, create_rate_data
from unit.coordinators.test_previous_consumption_and_rates import get_account_info, sensor_identifier, sensor_serial_number
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.coordinators.previous_consumption_and_rates import get_latest_day, async_fetch_consumption_and_rates


@pytest.fixture(autouse=True)
def london_time_zone():
  previous_time_zone = dt_util.DEFAULT_TIME_ZONE
  dt_util.set_default_time_zone(ZoneInfo('Europe/London'))
  yield
  dt_util.set_default_time_zone(previous_time_zone)


def consumption_for_day(day):
  local_start = datetime.fromisoformat(day).replace(tzinfo=ZoneInfo('Europe/London'))
  return create_consumption_data(
    local_start.astimezone(timezone.utc),
    (local_start + timedelta(days=1)).astimezone(timezone.utc)
  )


@pytest.mark.parametrize('day, expected_count', [
  ('2026-03-28', 48),
  ('2026-03-29', 46),
  ('2026-07-01', 48),
  ('2026-10-25', 50),
  ('2026-10-26', 48),
])
def test_complete_local_day_is_returned(day, expected_count):
  consumption = consumption_for_day(day)
  assert len(consumption) == expected_count
  assert get_latest_day(consumption) == consumption


@pytest.mark.parametrize('consumption', [None, []])
def test_empty_data_returns_none(consumption):
  assert get_latest_day(consumption) is None


def test_autumn_day_with_only_48_readings_is_incomplete():
  assert get_latest_day(consumption_for_day('2026-10-25')[:-2]) is None


@pytest.mark.parametrize('missing_index', [0, 10, -1])
def test_missing_half_hour_is_incomplete(missing_index):
  consumption = consumption_for_day('2026-10-25')
  del consumption[missing_index]
  assert get_latest_day(consumption) is None


def test_duplicate_cannot_replace_a_missing_half_hour():
  consumption = consumption_for_day('2026-10-25')
  consumption[10] = consumption[9]
  assert get_latest_day(consumption) is None


def test_overlapping_interval_is_incomplete():
  consumption = consumption_for_day('2026-10-25')
  consumption[10]['end'] += timedelta(minutes=30)
  assert get_latest_day(consumption) is None


def test_48_readings_on_a_spring_day_are_not_complete():
  consumption = consumption_for_day('2026-03-29')
  consumption[5:5] = [consumption[4], consumption[4]]
  assert len(consumption) == 48
  assert get_latest_day(consumption) is None


def test_latest_complete_day_is_used_before_a_partial_day():
  complete = consumption_for_day('2026-10-25')
  partial = consumption_for_day('2026-10-26')[:10]
  assert get_latest_day(complete + partial) == complete


def test_a_later_complete_day_is_selected():
  earlier = consumption_for_day('2026-10-25')
  later = consumption_for_day('2026-10-26')
  assert get_latest_day(earlier + later) == later


def test_zero_consumption_is_a_valid_reading():
  consumption = consumption_for_day('2026-10-25')
  for reading in consumption:
    reading['consumption'] = 0
  assert get_latest_day(consumption) == consumption


@pytest.mark.asyncio
@pytest.mark.parametrize('is_electricity', [True, False])
@pytest.mark.parametrize('day, following_day', [
  ('2026-03-29', '2026-03-30'),
  ('2026-10-25', '2026-10-26'),
])
@pytest.mark.parametrize('partial_count', [0, 10, 46])
async def test_coordinator_retains_a_complete_clock_change_day(is_electricity, day, following_day, partial_count):
  complete = consumption_for_day(day)
  response = complete + consumption_for_day(following_day)[:partial_count]
  period_from = complete[0]['start']
  period_to = complete[-1]['end']
  client = mock.Mock(spec=OctopusEnergyApiClient)
  consumption_method = mock.AsyncMock(side_effect=lambda *args, **kwargs: response[-kwargs['page_size']:])
  if is_electricity:
    client.async_get_electricity_consumption = consumption_method
    client.async_get_electricity_rates = mock.AsyncMock(return_value=create_rate_data(period_from, period_to, [1]))
    client.async_get_electricity_standing_charge = mock.AsyncMock(return_value={'value_inc_vat': 50})
  else:
    client.async_get_gas_consumption = consumption_method
    client.async_get_gas_rates = mock.AsyncMock(return_value=create_rate_data(period_from, period_to, [1]))
    client.async_get_gas_standing_charge = mock.AsyncMock(return_value={'value_inc_vat': 50})

  result = await async_fetch_consumption_and_rates(
    None,
    period_to + timedelta(days=1),
    get_account_info(period_from),
    client,
    sensor_identifier,
    sensor_serial_number,
    is_electricity,
    True,
    lambda *args: None,
  )

  assert result is not None
  assert result.consumption == complete
  consumption_method.assert_awaited_once()
  assert consumption_method.call_args.kwargs['page_size'] <= 100
