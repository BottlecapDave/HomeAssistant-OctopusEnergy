import logging
import os
from datetime import datetime, timedelta

logging.getLogger().setLevel(logging.DEBUG)

class TestContext:
  api_key: str
  account_id: str
  gas_mprn: str
  gas_serial_number: str
  electricity_mpan: str
  electricity_serial_number: str

  def __init__(self, api_key, account_id, gas_mprn, gas_serial_number, electricity_mpan, electricity_serial_number):
    self.api_key = api_key
    self.account_id = account_id
    self.gas_mprn = gas_mprn
    self.gas_serial_number = gas_serial_number
    self.electricity_mpan = electricity_mpan
    self.electricity_serial_number = electricity_serial_number

def get_test_context():
  api_key = os.environ["API_KEY"]
  if (api_key is None):
      raise Exception("API_KEY must be set")

  account_id = os.environ["ACCOUNT_ID"]
  if (account_id is None):
      raise Exception("ACCOUNT_ID must be set")

  gas_mprn = os.environ["GAS_MPRN"]
  if (gas_mprn is None):
      raise Exception("GAS_MPRN must be set")

  gas_serial_number = os.environ["GAS_SN"]
  if (gas_serial_number is None):
      raise Exception("GAS_SN must be set")

  electricity_mpan= os.environ["ELECTRICITY_MPAN"]
  if (electricity_mpan is None):
      raise Exception("ELECTRICITY_MPAN must be set")

  electricity_serial_number = os.environ["ELECTRICITY_SN"]
  if (electricity_serial_number is None):
      raise Exception("ELECTRICITY_SN must be set")
  
  return TestContext(api_key, account_id, gas_mprn, gas_serial_number, electricity_mpan, electricity_serial_number)

def create_consumption_data(period_from: datetime, period_to: datetime, reverse = False):
  consumption = []
  current_valid_from = period_from
  current_valid_to = None
  while current_valid_to is None or current_valid_to < period_to:
    current_valid_to = current_valid_from + timedelta(minutes=30)

    consumption.append({
      "start": current_valid_from,
      "end": current_valid_to,
      "consumption": 1
    })

    current_valid_from = current_valid_to

  if reverse == True:
    def get_interval_start(item):
      return (item["start"].timestamp(), item["start"].fold)

    consumption.sort(key=get_interval_start, reverse=True)

  return consumption

def create_rate_data(period_from, period_to, expected_rates: list):
  rates = []
  current_valid_from = period_from
  current_valid_to = None

  rate_index = 0
  while current_valid_to is None or current_valid_to < period_to:
    current_valid_to = current_valid_from + timedelta(minutes=30)

    rates.append({
      "start": current_valid_from,
      "end": current_valid_to,
      "tariff_code": "1-ER-TARIFF-L",
      "value_inc_vat": expected_rates[rate_index],
      "is_capped": False
    })

    current_valid_from = current_valid_to
    rate_index = rate_index + 1

    if (rate_index > (len(expected_rates) - 1)):
      rate_index = 0

  return rates