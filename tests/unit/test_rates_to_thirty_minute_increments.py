from datetime import timedelta
import pytest

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.octopus_energy.utils import rates_to_thirty_minute_increments

@pytest.mark.asyncio
async def test_go_rates():
  # Act
  period_from = as_utc(parse_datetime("2022-10-09T00:00Z"))
  period_to = as_utc(parse_datetime("2022-10-10T00:00Z"))
  tariff_code = "test_tariff"
  rates = [
    {
      "value_exc_vat": 38.217,
      "value_inc_vat": 40.12785,
      "valid_from": "2022-10-08T04:30:00Z",
      "valid_to": "2022-10-09T00:30:00Z"
    },
    {
      "value_exc_vat": 7.142,
      "value_inc_vat": 7.4991,
      "valid_from": "2022-10-09T00:30:00Z",
      "valid_to": "2022-10-09T04:30:00Z"
    },
    {
      "value_exc_vat": 38.217,
      "value_inc_vat": 40.12785,
      "valid_from": "2022-10-09T04:30:00Z",
      "valid_to": "2022-10-10T00:30:00Z"
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
  assert result != None
  assert len(result) == 48

  start_time = as_utc(parse_datetime("2022-10-09T00:00Z"))
  for index in range(48):
    end_time = start_time + timedelta(minutes=30)
    assert result[index]["valid_from"] == start_time
    assert result[index]["valid_to"] == end_time

    rates_index = 2
    if index < 1:
      rates_index = 0
    elif index < 9:
      rates_index = 1

    assert result[index]["value_inc_vat"] == rates[rates_index]["value_inc_vat"]
    assert result[index]["value_exc_vat"] == rates[rates_index]["value_exc_vat"]

    assert result[index]["tariff_code"] == tariff_code

    start_time = end_time

  assert start_time == as_utc(parse_datetime("2022-10-10T00:00Z"))