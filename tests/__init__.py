import os
from datetime import timedelta

def get_test_context():
  api_key = os.environ["API_KEY"]
  if (api_key == None):
      raise Exception("API_KEY must be set")

  gas_mprn = os.environ["GAS_MPRN"]
  if (gas_mprn == None):
      raise Exception("GAS_MPRN must be set")

  gas_serial_number = os.environ["GAS_SN"]
  if (gas_serial_number == None):
      raise Exception("GAS_SN must be set")

  return {
    "api_key": api_key,
    "gas_mprn": gas_mprn,
    "gas_serial_number": gas_serial_number
  }

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
