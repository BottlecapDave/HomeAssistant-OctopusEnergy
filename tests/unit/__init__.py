from datetime import datetime, timedelta
import logging

from custom_components.octopus_energy.api_client import rates_to_thirty_minute_increments

logging.getLogger().setLevel(logging.DEBUG)

def create_consumption_data(period_from: datetime, period_to: datetime, reverse = False, from_key = "start", to_key = "end"):
  consumption = []
  current_valid_from = period_from
  current_valid_to = None
  while current_valid_to is None or current_valid_to < period_to:
    current_valid_to = current_valid_from + timedelta(minutes=30)

    consumption.append({
      from_key: current_valid_from,
      to_key: current_valid_to,
      "consumption": 1
    })

    current_valid_from = current_valid_to

  if reverse == True:
    def get_interval_start(item):
      return (item[from_key].timestamp(), item[from_key].fold)

    consumption.sort(key=get_interval_start, reverse=True)

  return consumption

def create_rate_data(period_from: datetime, period_to: datetime, expected_rates: list, tariff_code = None):
  rates = []
  current_valid_from = period_from
  current_valid_to = None

  rate_index = 0
  while current_valid_to is None or current_valid_to < period_to:
    current_valid_to = current_valid_from + timedelta(minutes=30)

    rates.append({
      "start": current_valid_from,
      "end": current_valid_to,
      "value_inc_vat": expected_rates[rate_index],
      "tariff_code": tariff_code if tariff_code is not None else "E-1R-Test-L",
      "is_capped": False
    })

    current_valid_from = current_valid_to
    rate_index = rate_index + 1

    if (rate_index > (len(expected_rates) - 1)):
      rate_index = 0

  return rates

agile_rates = rates_to_thirty_minute_increments(
  {
    "results": [
      {
        "value_exc_vat": 15.33,
        "value_inc_vat": 16.0965,
        "valid_from": "2022-10-22T22:30:00Z",
        "valid_to": "2022-10-22T23:00:00Z"
      },
      {
        "value_exc_vat": 14.28,
        "value_inc_vat": 14.994,
        "valid_from": "2022-10-22T22:00:00Z",
        "valid_to": "2022-10-22T22:30:00Z"
      },
      {
        "value_exc_vat": 22.03,
        "value_inc_vat": 23.1315,
        "valid_from": "2022-10-22T21:30:00Z",
        "valid_to": "2022-10-22T22:00:00Z"
      },
      {
        "value_exc_vat": 24.42,
        "value_inc_vat": 25.641,
        "valid_from": "2022-10-22T21:00:00Z",
        "valid_to": "2022-10-22T21:30:00Z"
      },
      {
        "value_exc_vat": 23.1,
        "value_inc_vat": 24.255,
        "valid_from": "2022-10-22T20:30:00Z",
        "valid_to": "2022-10-22T21:00:00Z"
      },
      {
        "value_exc_vat": 27.89,
        "value_inc_vat": 29.2845,
        "valid_from": "2022-10-22T20:00:00Z",
        "valid_to": "2022-10-22T20:30:00Z"
      },
      {
        "value_exc_vat": 24.36,
        "value_inc_vat": 25.578,
        "valid_from": "2022-10-22T19:30:00Z",
        "valid_to": "2022-10-22T20:00:00Z"
      },
      {
        "value_exc_vat": 31.58,
        "value_inc_vat": 33.159,
        "valid_from": "2022-10-22T19:00:00Z",
        "valid_to": "2022-10-22T19:30:00Z"
      },
      {
        "value_exc_vat": 29.23,
        "value_inc_vat": 30.6915,
        "valid_from": "2022-10-22T18:30:00Z",
        "valid_to": "2022-10-22T19:00:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-22T18:00:00Z",
        "valid_to": "2022-10-22T18:30:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-22T17:30:00Z",
        "valid_to": "2022-10-22T18:00:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-22T17:00:00Z",
        "valid_to": "2022-10-22T17:30:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-22T16:30:00Z",
        "valid_to": "2022-10-22T17:00:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-22T16:00:00Z",
        "valid_to": "2022-10-22T16:30:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-22T15:30:00Z",
        "valid_to": "2022-10-22T16:00:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-22T15:00:00Z",
        "valid_to": "2022-10-22T15:30:00Z"
      },
      {
        "value_exc_vat": 21.0,
        "value_inc_vat": 22.05,
        "valid_from": "2022-10-22T14:30:00Z",
        "valid_to": "2022-10-22T15:00:00Z"
      },
      {
        "value_exc_vat": 20.37,
        "value_inc_vat": 21.3885,
        "valid_from": "2022-10-22T14:00:00Z",
        "valid_to": "2022-10-22T14:30:00Z"
      },
      {
        "value_exc_vat": 18.02,
        "value_inc_vat": 18.921,
        "valid_from": "2022-10-22T13:30:00Z",
        "valid_to": "2022-10-22T14:00:00Z"
      },
      {
        "value_exc_vat": 18.27,
        "value_inc_vat": 19.1835,
        "valid_from": "2022-10-22T13:00:00Z",
        "valid_to": "2022-10-22T13:30:00Z"
      },
      {
        "value_exc_vat": 17.22,
        "value_inc_vat": 18.081,
        "valid_from": "2022-10-22T12:30:00Z",
        "valid_to": "2022-10-22T13:00:00Z"
      },
      {
        "value_exc_vat": 17.64,
        "value_inc_vat": 18.522,
        "valid_from": "2022-10-22T12:00:00Z",
        "valid_to": "2022-10-22T12:30:00Z"
      },
      {
        "value_exc_vat": 19.03,
        "value_inc_vat": 19.9815,
        "valid_from": "2022-10-22T11:30:00Z",
        "valid_to": "2022-10-22T12:00:00Z"
      },
      {
        "value_exc_vat": 20.33,
        "value_inc_vat": 21.3465,
        "valid_from": "2022-10-22T11:00:00Z",
        "valid_to": "2022-10-22T11:30:00Z"
      },
      {
        "value_exc_vat": 19.74,
        "value_inc_vat": 20.727,
        "valid_from": "2022-10-22T10:30:00Z",
        "valid_to": "2022-10-22T11:00:00Z"
      },
      {
        "value_exc_vat": 19.74,
        "value_inc_vat": 20.727,
        "valid_from": "2022-10-22T10:00:00Z",
        "valid_to": "2022-10-22T10:30:00Z"
      },
      {
        "value_exc_vat": 20.16,
        "value_inc_vat": 21.168,
        "valid_from": "2022-10-22T09:30:00Z",
        "valid_to": "2022-10-22T10:00:00Z"
      },
      {
        "value_exc_vat": 21.21,
        "value_inc_vat": 22.2705,
        "valid_from": "2022-10-22T09:00:00Z",
        "valid_to": "2022-10-22T09:30:00Z"
      },
      {
        "value_exc_vat": 21.59,
        "value_inc_vat": 22.6695,
        "valid_from": "2022-10-22T08:30:00Z",
        "valid_to": "2022-10-22T09:00:00Z"
      },
      {
        "value_exc_vat": 23.4,
        "value_inc_vat": 24.57,
        "valid_from": "2022-10-22T08:00:00Z",
        "valid_to": "2022-10-22T08:30:00Z"
      },
      {
        "value_exc_vat": 28.56,
        "value_inc_vat": 29.988,
        "valid_from": "2022-10-22T07:30:00Z",
        "valid_to": "2022-10-22T08:00:00Z"
      },
      {
        "value_exc_vat": 23.18,
        "value_inc_vat": 24.339,
        "valid_from": "2022-10-22T07:00:00Z",
        "valid_to": "2022-10-22T07:30:00Z"
      },
      {
        "value_exc_vat": 20.75,
        "value_inc_vat": 21.7875,
        "valid_from": "2022-10-22T06:30:00Z",
        "valid_to": "2022-10-22T07:00:00Z"
      },
      {
        "value_exc_vat": 16.32,
        "value_inc_vat": 17.136,
        "valid_from": "2022-10-22T06:00:00Z",
        "valid_to": "2022-10-22T06:30:00Z"
      },
      {
        "value_exc_vat": 16.32,
        "value_inc_vat": 17.136,
        "valid_from": "2022-10-22T05:30:00Z",
        "valid_to": "2022-10-22T06:00:00Z"
      },
      {
        "value_exc_vat": 18.9,
        "value_inc_vat": 19.845,
        "valid_from": "2022-10-22T05:00:00Z",
        "valid_to": "2022-10-22T05:30:00Z"
      },
      {
        "value_exc_vat": 17.05,
        "value_inc_vat": 17.9025,
        "valid_from": "2022-10-22T04:30:00Z",
        "valid_to": "2022-10-22T05:00:00Z"
      },
      {
        "value_exc_vat": 18.9,
        "value_inc_vat": 19.845,
        "valid_from": "2022-10-22T04:00:00Z",
        "valid_to": "2022-10-22T04:30:00Z"
      },
      {
        "value_exc_vat": 17.62,
        "value_inc_vat": 18.501,
        "valid_from": "2022-10-22T03:30:00Z",
        "valid_to": "2022-10-22T04:00:00Z"
      },
      {
        "value_exc_vat": 17.81,
        "value_inc_vat": 18.7005,
        "valid_from": "2022-10-22T03:00:00Z",
        "valid_to": "2022-10-22T03:30:00Z"
      },
      {
        "value_exc_vat": 17.47,
        "value_inc_vat": 18.3435,
        "valid_from": "2022-10-22T02:30:00Z",
        "valid_to": "2022-10-22T03:00:00Z"
      },
      {
        "value_exc_vat": 17.47,
        "value_inc_vat": 18.3435,
        "valid_from": "2022-10-22T02:00:00Z",
        "valid_to": "2022-10-22T02:30:00Z"
      },
      {
        "value_exc_vat": 18.42,
        "value_inc_vat": 19.341,
        "valid_from": "2022-10-22T01:30:00Z",
        "valid_to": "2022-10-22T02:00:00Z"
      },
      {
        "value_exc_vat": 18.69,
        "value_inc_vat": 19.6245,
        "valid_from": "2022-10-22T01:00:00Z",
        "valid_to": "2022-10-22T01:30:00Z"
      },
      {
        "value_exc_vat": 20.22,
        "value_inc_vat": 21.231,
        "valid_from": "2022-10-22T00:30:00Z",
        "valid_to": "2022-10-22T01:00:00Z"
      },
      {
        "value_exc_vat": 14.123,
        "value_inc_vat": 14.123,
        "valid_from": "2022-10-22T00:00:00Z",
        "valid_to": "2022-10-22T00:30:00Z"
      },
      {
        "value_exc_vat": 14.123,
        "value_inc_vat": 14.123,
        "valid_from": "2022-10-21T23:30:00Z",
        "valid_to": "2022-10-22T00:00:00Z"
      },
      {
        "value_exc_vat": 20.58,
        "value_inc_vat": 21.609,
        "valid_from": "2022-10-21T23:00:00Z",
        "valid_to": "2022-10-21T23:30:00Z"
      },
      {
        "value_exc_vat": 18.9,
        "value_inc_vat": 19.845,
        "valid_from": "2022-10-21T22:30:00Z",
        "valid_to": "2022-10-21T23:00:00Z"
      },
      {
        "value_exc_vat": 18.75,
        "value_inc_vat": 19.6875,
        "valid_from": "2022-10-21T22:00:00Z",
        "valid_to": "2022-10-21T22:30:00Z"
      },
      {
        "value_exc_vat": 19.74,
        "value_inc_vat": 20.727,
        "valid_from": "2022-10-21T21:30:00Z",
        "valid_to": "2022-10-21T22:00:00Z"
      },
      {
        "value_exc_vat": 22.05,
        "value_inc_vat": 23.1525,
        "valid_from": "2022-10-21T21:00:00Z",
        "valid_to": "2022-10-21T21:30:00Z"
      },
      {
        "value_exc_vat": 19.74,
        "value_inc_vat": 20.727,
        "valid_from": "2022-10-21T20:30:00Z",
        "valid_to": "2022-10-21T21:00:00Z"
      },
      {
        "value_exc_vat": 22.39,
        "value_inc_vat": 23.5095,
        "valid_from": "2022-10-21T20:00:00Z",
        "valid_to": "2022-10-21T20:30:00Z"
      },
      {
        "value_exc_vat": 20.62,
        "value_inc_vat": 21.651,
        "valid_from": "2022-10-21T19:30:00Z",
        "valid_to": "2022-10-21T20:00:00Z"
      },
      {
        "value_exc_vat": 24.78,
        "value_inc_vat": 26.019,
        "valid_from": "2022-10-21T19:00:00Z",
        "valid_to": "2022-10-21T19:30:00Z"
      },
      {
        "value_exc_vat": 20.87,
        "value_inc_vat": 21.9135,
        "valid_from": "2022-10-21T18:30:00Z",
        "valid_to": "2022-10-21T19:00:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T18:00:00Z",
        "valid_to": "2022-10-21T18:30:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T17:30:00Z",
        "valid_to": "2022-10-21T18:00:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T17:00:00Z",
        "valid_to": "2022-10-21T17:30:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T16:30:00Z",
        "valid_to": "2022-10-21T17:00:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T16:00:00Z",
        "valid_to": "2022-10-21T16:30:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T15:30:00Z",
        "valid_to": "2022-10-21T16:00:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T15:00:00Z",
        "valid_to": "2022-10-21T15:30:00Z"
      },
      {
        "value_exc_vat": 21.0,
        "value_inc_vat": 22.05,
        "valid_from": "2022-10-21T14:30:00Z",
        "valid_to": "2022-10-21T15:00:00Z"
      },
      {
        "value_exc_vat": 19.74,
        "value_inc_vat": 20.727,
        "valid_from": "2022-10-21T14:00:00Z",
        "valid_to": "2022-10-21T14:30:00Z"
      },
      {
        "value_exc_vat": 20.2,
        "value_inc_vat": 21.21,
        "valid_from": "2022-10-21T13:30:00Z",
        "valid_to": "2022-10-21T14:00:00Z"
      },
      {
        "value_exc_vat": 20.2,
        "value_inc_vat": 21.21,
        "valid_from": "2022-10-21T13:00:00Z",
        "valid_to": "2022-10-21T13:30:00Z"
      },
      {
        "value_exc_vat": 20.35,
        "value_inc_vat": 21.3675,
        "valid_from": "2022-10-21T12:30:00Z",
        "valid_to": "2022-10-21T13:00:00Z"
      },
      {
        "value_exc_vat": 26.04,
        "value_inc_vat": 27.342,
        "valid_from": "2022-10-21T12:00:00Z",
        "valid_to": "2022-10-21T12:30:00Z"
      },
      {
        "value_exc_vat": 20.96,
        "value_inc_vat": 22.008,
        "valid_from": "2022-10-21T11:30:00Z",
        "valid_to": "2022-10-21T12:00:00Z"
      },
      {
        "value_exc_vat": 29.4,
        "value_inc_vat": 30.87,
        "valid_from": "2022-10-21T11:00:00Z",
        "valid_to": "2022-10-21T11:30:00Z"
      },
      {
        "value_exc_vat": 27.09,
        "value_inc_vat": 28.4445,
        "valid_from": "2022-10-21T10:30:00Z",
        "valid_to": "2022-10-21T11:00:00Z"
      },
      {
        "value_exc_vat": 25.2,
        "value_inc_vat": 26.46,
        "valid_from": "2022-10-21T10:00:00Z",
        "valid_to": "2022-10-21T10:30:00Z"
      },
      {
        "value_exc_vat": 25.62,
        "value_inc_vat": 26.901,
        "valid_from": "2022-10-21T09:30:00Z",
        "valid_to": "2022-10-21T10:00:00Z"
      },
      {
        "value_exc_vat": 31.5,
        "value_inc_vat": 33.075,
        "valid_from": "2022-10-21T09:00:00Z",
        "valid_to": "2022-10-21T09:30:00Z"
      },
      {
        "value_exc_vat": 30.58,
        "value_inc_vat": 32.109,
        "valid_from": "2022-10-21T08:30:00Z",
        "valid_to": "2022-10-21T09:00:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T08:00:00Z",
        "valid_to": "2022-10-21T08:30:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T07:30:00Z",
        "valid_to": "2022-10-21T08:00:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T07:00:00Z",
        "valid_to": "2022-10-21T07:30:00Z"
      },
      {
        "value_exc_vat": 31.882,
        "value_inc_vat": 33.4761,
        "valid_from": "2022-10-21T06:30:00Z",
        "valid_to": "2022-10-21T07:00:00Z"
      },
      {
        "value_exc_vat": 26.06,
        "value_inc_vat": 27.363,
        "valid_from": "2022-10-21T06:00:00Z",
        "valid_to": "2022-10-21T06:30:00Z"
      },
      {
        "value_exc_vat": 20.85,
        "value_inc_vat": 21.8925,
        "valid_from": "2022-10-21T05:30:00Z",
        "valid_to": "2022-10-21T06:00:00Z"
      },
      {
        "value_exc_vat": 21.38,
        "value_inc_vat": 22.449,
        "valid_from": "2022-10-21T05:00:00Z",
        "valid_to": "2022-10-21T05:30:00Z"
      },
      {
        "value_exc_vat": 25.56,
        "value_inc_vat": 26.838,
        "valid_from": "2022-10-21T04:30:00Z",
        "valid_to": "2022-10-21T05:00:00Z"
      },
      {
        "value_exc_vat": 20.2,
        "value_inc_vat": 21.21,
        "valid_from": "2022-10-21T04:00:00Z",
        "valid_to": "2022-10-21T04:30:00Z"
      },
      {
        "value_exc_vat": 20.2,
        "value_inc_vat": 21.21,
        "valid_from": "2022-10-21T03:30:00Z",
        "valid_to": "2022-10-21T04:00:00Z"
      },
      {
        "value_exc_vat": 20.62,
        "value_inc_vat": 21.651,
        "valid_from": "2022-10-21T03:00:00Z",
        "valid_to": "2022-10-21T03:30:00Z"
      },
      {
        "value_exc_vat": 20.41,
        "value_inc_vat": 21.4305,
        "valid_from": "2022-10-21T02:30:00Z",
        "valid_to": "2022-10-21T03:00:00Z"
      },
      {
        "value_exc_vat": 20.62,
        "value_inc_vat": 21.651,
        "valid_from": "2022-10-21T02:00:00Z",
        "valid_to": "2022-10-21T02:30:00Z"
      },
      {
        "value_exc_vat": 19.74,
        "value_inc_vat": 20.727,
        "valid_from": "2022-10-21T01:30:00Z",
        "valid_to": "2022-10-21T02:00:00Z"
      },
      {
        "value_exc_vat": 20.62,
        "value_inc_vat": 21.651,
        "valid_from": "2022-10-21T01:00:00Z",
        "valid_to": "2022-10-21T01:30:00Z"
      },
      {
        "value_exc_vat": 20.62,
        "value_inc_vat": 21.651,
        "valid_from": "2022-10-21T00:30:00Z",
        "valid_to": "2022-10-21T01:00:00Z"
      },
      {
        "value_exc_vat": 20.2,
        "value_inc_vat": 21.21,
        "valid_from": "2022-10-21T00:00:00Z",
        "valid_to": "2022-10-21T00:30:00Z"
      },
      {
        "value_exc_vat": 20.62,
        "value_inc_vat": 21.651,
        "valid_from": "2022-10-20T23:30:00Z",
        "valid_to": "2022-10-21T00:00:00Z"
      },
      {
        "value_exc_vat": 23.52,
        "value_inc_vat": 24.696,
        "valid_from": "2022-10-20T23:00:00Z",
        "valid_to": "2022-10-20T23:30:00Z"
      }
    ]
  },
  datetime.strptime("2022-10-21T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
  datetime.strptime("2022-10-23T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z"),
  "E-1R-AGILE-18-02-21-G"
)