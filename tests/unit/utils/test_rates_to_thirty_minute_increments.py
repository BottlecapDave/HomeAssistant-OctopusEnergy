from datetime import timedelta
import pytest

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.octopus_energy.api_client import rates_to_thirty_minute_increments

# Based on E-1R-GO-22-07-05-D
@pytest.mark.asyncio
async def test_go_rates_bst():
  # Act
  period_from = as_utc(parse_datetime("2022-10-09T00:00+01:00"))
  period_to = as_utc(parse_datetime("2022-10-10T00:00+01:00"))
  tariff_code = "test_tariff"
  rates = [
    {
			"value_exc_vat": 40.274,
			"value_inc_vat": 42.2877,
			"valid_from": "2022-10-10T03:30:00Z",
			"valid_to": "2022-10-10T23:30:00Z"
		},
		{
			"value_exc_vat": 7.142,
			"value_inc_vat": 7.4991,
			"valid_from": "2022-10-09T23:30:00Z",
			"valid_to": "2022-10-10T03:30:00Z"
		},
		{
			"value_exc_vat": 40.274,
			"value_inc_vat": 42.2877,
			"valid_from": "2022-10-09T03:30:00Z",
			"valid_to": "2022-10-09T23:30:00Z"
		},
		{
			"value_exc_vat": 7.142,
			"value_inc_vat": 7.4991,
			"valid_from": "2022-10-08T23:30:00Z",
			"valid_to": "2022-10-09T03:30:00Z"
		},
		{
			"value_exc_vat": 40.274,
			"value_inc_vat": 42.2877,
			"valid_from": "2022-10-08T03:30:00Z",
			"valid_to": "2022-10-08T23:30:00Z"
		},
		{
			"value_exc_vat": 7.142,
			"value_inc_vat": 7.4991,
			"valid_from": "2022-10-07T23:30:00Z",
			"valid_to": "2022-10-08T03:30:00Z"
		},
		{
			"value_exc_vat": 40.274,
			"value_inc_vat": 42.2877,
			"valid_from": "2022-10-07T03:30:00Z",
			"valid_to": "2022-10-07T23:30:00Z"
		}
  ]
  
  result = rates_to_thirty_minute_increments(
    {
      "results": rates
    }, 
    period_from,
    period_to,
    tariff_code
  )

  # Assert
  assert result is not None
  assert len(result) == 48

  start_time = as_utc(parse_datetime("2022-10-09T00:00+01:00"))
  for index in range(48):
    end_time = start_time + timedelta(minutes=30)
    assert result[index]["start"] == start_time
    assert result[index]["end"] == end_time

    rates_index = 6
    if index < 1:
      rates_index = 4
    elif index < 9:
      rates_index = 5

    assert result[index]["value_inc_vat"] == rates[rates_index]["value_inc_vat"]

    assert result[index]["tariff_code"] == tariff_code

    start_time = end_time

  assert start_time == as_utc(parse_datetime("2022-10-10T00:00+01:00"))