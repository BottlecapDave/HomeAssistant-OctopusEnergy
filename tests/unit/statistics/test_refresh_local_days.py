from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import mock
import pytest
from homeassistant.util import dt as dt_util

from unit import create_consumption_data
from custom_components.octopus_energy.const import DATA_ACCOUNT, DOMAIN
from custom_components.octopus_energy.statistics import refresh


@pytest.fixture(autouse=True)
def london_time_zone():
  previous_time_zone = dt_util.DEFAULT_TIME_ZONE
  dt_util.set_default_time_zone(ZoneInfo('Europe/London'))
  yield
  dt_util.set_default_time_zone(previous_time_zone)


@pytest.mark.asyncio
@pytest.mark.parametrize('is_electricity', [True, False])
@pytest.mark.parametrize('start_date, expected_bounds', [
  ('2026-03-29', ['2026-03-29T00:00:00+00:00', '2026-03-29T23:00:00+00:00']),
  ('2026-07-01', ['2026-06-30T23:00:00+00:00', '2026-07-01T23:00:00+00:00']),
  ('2026-10-25', ['2026-10-24T23:00:00+00:00', '2026-10-26T00:00:00+00:00']),
  ('2026-10-26', ['2026-10-26T00:00:00+00:00', '2026-10-27T00:00:00+00:00']),
  ('2026-10-24', ['2026-10-23T23:00:00+00:00', '2026-10-24T23:00:00+00:00', '2026-10-26T00:00:00+00:00', '2026-10-27T00:00:00+00:00']),
])
async def test_refresh_requests_complete_local_calendar_days(is_electricity, start_date, expected_bounds):
  bounds = [datetime.fromisoformat(value) for value in expected_bounds]
  expected_periods = list(zip(bounds, bounds[1:]))
  current = bounds[-1].astimezone(ZoneInfo('Europe/London'))
  client = mock.Mock()
  fuel = 'electricity' if is_electricity else 'gas'
  consumption_method = mock.AsyncMock(side_effect=lambda point, serial, start, end: create_consumption_data(start, end))
  rates_method = mock.AsyncMock(return_value=[])
  setattr(client, f'async_get_{fuel}_consumption', consumption_method)
  setattr(client, f'async_get_{fuel}_rates', rates_method)
  consumption_import = mock.AsyncMock(return_value=object())
  cost_import = mock.AsyncMock(return_value=object())
  hass = mock.Mock()
  hass.data = {DOMAIN: {'account': {DATA_ACCOUNT: SimpleNamespace(account={})}}}
  tariff = SimpleNamespace(product='TEST', code='TEST')

  with (
    mock.patch.object(refresh, 'now', return_value=current),
    mock.patch.object(refresh, f'get_{fuel}_meter_tariff', return_value=tariff),
    mock.patch.object(refresh, f'calculate_{fuel}_consumption_and_cost', side_effect=lambda consumption, *args: {'charges': consumption}),
    mock.patch.object(refresh, 'async_import_external_statistics_from_consumption', consumption_import),
    mock.patch.object(refresh, 'async_import_external_statistics_from_cost', cost_import),
    mock.patch.object(refresh.persistent_notification, 'async_create'),
  ):
    if is_electricity:
      await refresh.async_refresh_previous_electricity_consumption_data(
        hass, client, 'account', start_date, 'point', 'serial', True, False
      )
    else:
      await refresh.async_refresh_previous_gas_consumption_data(
        hass, client, 'account', start_date, 'point', 'serial', 'm³', 39.2
      )

  requested_periods = [(call.args[-2], call.args[-1]) for call in consumption_method.call_args_list]
  assert requested_periods == expected_periods
  assert [(call.args[-2], call.args[-1]) for call in rates_method.call_args_list] == expected_periods
  assert consumption_import.await_count == len(expected_periods) * (1 if is_electricity else 2)
  assert cost_import.await_count == len(expected_periods)
  for index, (start, end) in enumerate(expected_periods):
    charges = cost_import.call_args_list[index].args[4]
    assert charges[0]['start'] == start
    assert charges[-1]['end'] == end
    assert len(charges) == int((end - start).total_seconds() / 1800)
