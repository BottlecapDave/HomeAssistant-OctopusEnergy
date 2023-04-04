import os
from datetime import timedelta
import aiohttp
import json
from homeassistant.util.dt import (parse_datetime)

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

  return {
    "api_key": api_key,
    "account_id": account_id,
    "gas_mprn": gas_mprn,
    "gas_serial_number": gas_serial_number,
    "electricity_mpan": electricity_mpan,
    "electricity_serial_number": electricity_serial_number
  }

def create_consumption_data(period_from, period_to, reverse = False):
  consumption = []
  current_valid_from = period_from
  current_valid_to = None
  while current_valid_to is None or current_valid_to < period_to:
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

async def async_get_tracker_tariff(api_key, tariff_code, target_date):
  async with aiohttp.ClientSession() as client:
    auth = aiohttp.BasicAuth(api_key, '')
    url = f'https://octopus.energy/api/v1/tracker/{tariff_code}/daily/past/1/0'
    async with client.get(url, auth=auth) as response:
      text = await response.text()
      data = json.loads(text)
      for period in data["periods"]:
        valid_from = parse_datetime(f'{period["date"]}T00:00:00Z')
        valid_to = parse_datetime(f'{period["date"]}T00:00:00Z') + timedelta(days=1)
        if (valid_from <= target_date and valid_to >= target_date):
          return period