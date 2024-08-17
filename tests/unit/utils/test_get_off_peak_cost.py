from custom_components.octopus_energy.api_client import rates_to_thirty_minute_increments
import pytest
from datetime import datetime, timedelta
import zoneinfo

from homeassistant.util.dt import (set_default_time_zone)

from custom_components.octopus_energy.utils import get_off_peak_cost
from tests.unit import create_rate_data

@pytest.mark.asyncio
@pytest.mark.parametrize("rates,expected_off_peak_cost",[
  ([1], None),
  ([1, 2], 1),
  ([1, 2, 3], 1),
  ([1, 2, 3, 4], None),
])
async def test_when_correct_number_of_rates_available_then_off_peak_cost_retrieved(rates, expected_off_peak_cost):
  period_from = datetime.strptime("2023-10-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2023-10-15T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2023-10-14T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  rate_data = create_rate_data(period_from, period_to, rates)
  
  # Act
  result = get_off_peak_cost(current, rate_data)

  # Assert
  assert result == expected_off_peak_cost

@pytest.mark.asyncio
async def test_when_rates_spead_over_two_days_then_off_peak_cost_not_retrieved():
  period_from = datetime.strptime("2023-10-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2023-10-14T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  rate_data = create_rate_data(period_from, period_from + timedelta(days=1), [1]) + create_rate_data(period_from + timedelta(days=1), period_from + timedelta(days=2), [2])
  
  # Act
  result = get_off_peak_cost(current, rate_data)

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_rates_available_then_off_peak_cost_returned():
  period_from = datetime.strptime("2023-11-04T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2023-11-06T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2023-11-05T10:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  data = [
    {
			"value_exc_vat": 28.8068,
			"value_inc_vat": 30.24714,
			"valid_from": "2023-11-06T04:30:00Z",
			"valid_to": "2023-11-07T00:30:00Z"
		},
		{
			"value_exc_vat": 8.5714,
			"value_inc_vat": 8.99997,
			"valid_from": "2023-11-06T00:30:00Z",
			"valid_to": "2023-11-06T04:30:00Z"
		},
		{
			"value_exc_vat": 28.8068,
			"value_inc_vat": 30.24714,
			"valid_from": "2023-11-05T04:30:00Z",
			"valid_to": "2023-11-06T00:30:00Z"
		},
		{
			"value_exc_vat": 8.5714,
			"value_inc_vat": 8.99997,
			"valid_from": "2023-11-05T00:30:00Z",
			"valid_to": "2023-11-05T04:30:00Z"
		},
		{
			"value_exc_vat": 28.8068,
			"value_inc_vat": 30.24714,
			"valid_from": "2023-11-04T04:30:00Z",
			"valid_to": "2023-11-05T00:30:00Z"
		},
		{
			"value_exc_vat": 8.5714,
			"value_inc_vat": 8.99997,
			"valid_from": "2023-11-04T00:30:00Z",
			"valid_to": "2023-11-04T04:30:00Z"
		},
		{
			"value_exc_vat": 28.8068,
			"value_inc_vat": 30.24714,
			"valid_from": "2023-11-03T04:30:00Z",
			"valid_to": "2023-11-04T00:30:00Z"
		}
  ]
  rate_data = rates_to_thirty_minute_increments({ "results": data }, period_from, period_to, 'tariff')
  
  # Act
  result = get_off_peak_cost(current, rate_data)

  # Assert
  assert result == 8.99997
  
@pytest.mark.asyncio
async def test_when_rates_available_and_bst_then_off_peak_cost_returned():
  period_from = datetime.strptime("2024-04-09T23:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2024-04-10T23:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2024-04-09T23:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
  set_default_time_zone(zoneinfo.ZoneInfo("Europe/London"))
  data = [
    {
			"value_exc_vat": 7.1428,
			"value_inc_vat": 7.49994,
			"valid_from": "2024-04-10T22:30:00+00:00",
			"valid_to": "2024-04-11T04:30:00+00:00",
		},
		{
			"value_exc_vat": 25.2575,
			"value_inc_vat": 26.520375,
			"valid_from": "2024-04-10T04:30:00+00:00",
			"valid_to": "2024-04-10T22:30:00+00:00",
		},
		{
			"value_exc_vat": 7.1428,
			"value_inc_vat": 7.49994,
			"valid_from": "2024-04-09T22:30:00+00:00",
			"valid_to": "2024-04-10T04:30:00+00:00",
		}
  ]
  rate_data = rates_to_thirty_minute_increments({ "results": data }, period_from, period_to, 'tariff')
  
  # Act
  result = get_off_peak_cost(current, rate_data)

  # Assert
  assert result == 7.49994