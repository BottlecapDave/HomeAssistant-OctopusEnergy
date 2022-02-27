import os
from datetime import timedelta

def create_consumption_data(period_from, period_to, reverse = False):
  consumption = []
  current_valid_from = period_from
  current_valid_to = None
  while current_valid_to == None or current_valid_to < period_to:
    current_valid_to = current_valid_from + timedelta(minutes=30)

    consumption.append({
      "interval_start": current_valid_from,
      "interval_end": current_valid_to,
      "consumption": 1
    })

    current_valid_from = current_valid_to

  if reverse == True:
    def get_interval_start(item):
      return item["interval_start"]

    consumption.sort(key=get_interval_start, reverse=True)

  return consumption

def create_rate_data(period_from, period_to, expected_rates: list):
  rates = []
  current_valid_from = period_from
  current_valid_to = None

  rate_index = 0
  while current_valid_to == None or current_valid_to < period_to:
    current_valid_to = current_valid_from + timedelta(minutes=30)

    rates.append({
      "valid_from": current_valid_from,
      "valid_to": current_valid_to,
      "value_inc_vat": expected_rates[rate_index]
    })

    current_valid_from = current_valid_to
    rate_index = rate_index + 1

    if (rate_index > (len(expected_rates) - 1)):
      rate_index = 0

  return rates
