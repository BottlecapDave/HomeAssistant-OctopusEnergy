import aiohttp
from datetime import (datetime, timedelta)
from homeassistant.util.dt import (utcnow, as_utc, parse_datetime)

class OctopusEnergyApiClient:

  def __init__(self, api_key):
    self._api_key = api_key
    self._base_url = 'https://api.octopus.energy'

  async def async_get_account(self, account_id):
    """Get the user's account"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/accounts/{account_id}'
      async with client.get(url, auth=auth) as response:
        # Disable content type check as sometimes it can report text/html
        data = await response.json(content_type=None)
        if ("properties" in data):
          # We're only supporting one property at the moment and we don't want to expose addresses
          prop = data["properties"][0]
          return {
            "electricity_meter_points": prop["electricity_meter_points"],
            "gas_meter_points": prop["gas_meter_points"]
          }
        
        return None

  async def async_get_rates(self, product_code, tariff_code):
    """Get the current rates"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      now = utcnow()
      period_from = as_utc(parse_datetime(now.strftime("%Y-%m-%dT00:00:00Z")))
      period_to = as_utc(parse_datetime((now + timedelta(days=2)).strftime("%Y-%m-%dT00:00:00Z")))
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        # Disable content type check as sometimes it can report text/html
        data = await response.json(content_type=None)
        results = []
        if ("results" in data):
          # We need to normalise our data into 30 minute increments so that all of our rates across all tariffs are the same and it's 
          # easier to calculate our target rate sensors
          for item in data["results"]:
            value_exc_vat = float(item["value_exc_vat"])
            value_inc_vat = float(item["value_inc_vat"])

            current_date = as_utc(parse_datetime(item["valid_from"]))

            # If we're on a fixed rate, then our current time could be in the past so we should go from
            # our target period from date otherwise we could be adjusting times quite far in the past
            if current_date < period_from:
              current_date = period_from

            # Some rates don't have end dates, so we should treat this as our period to target
            if "valid_to" in item and item["valid_to"] != None:
              target_date = as_utc(parse_datetime(item["valid_to"]))
            else:
              target_date = period_to
            
            while current_date < target_date:
              valid_to = current_date + timedelta(minutes=30)
              results.append({
                "value_exc_vat": value_exc_vat,
                "value_inc_vat": value_inc_vat,
                "valid_from": current_date,
                "valid_to": valid_to
              })

              current_date = valid_to
        
        return results

  def process_consumption(self, item):
    return {
      "consumption": float(item["consumption"]),
      "interval_start": as_utc(parse_datetime(item["interval_start"])),
      "interval_end": as_utc(parse_datetime(item["interval_end"]))
    }

  async def async_electricity_consumption(self, mpan, serial_number, period_from, period_to):
    """Get the current electricity rates"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/electricity-meter-points/{mpan}/meters/{serial_number}/consumption?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        # Disable content type check as sometimes it can report text/html
        data = await response.json(content_type=None)
        if ("results" in data):
          data = data["results"]
          results = []
          for item in data:
            item = self.process_consumption(item)

            # For some reason, the end point returns slightly more data than we requested, so we need to filter out
            # the results
            if as_utc(item["interval_start"]) >= period_from and as_utc(item["interval_end"]) <= period_to:
              results.append(item)
          
          return results
        
        return None

  async def async_gas_consumption(self, mprn, serial_number, period_from, period_to):
    """Get the current gas rates"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/gas-meter-points/{mprn}/meters/{serial_number}/consumption?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        # Disable content type check as sometimes it can report text/html
        data = await response.json(content_type=None)
        if ("results" in data):
          data = data["results"]
          results = []
          for item in data:
            item = self.process_consumption(item)

            # For some reason, the end point returns slightly more data than we requested, so we need to filter out
            # the results
            if as_utc(item["interval_start"]) >= period_from and as_utc(item["interval_end"]) <= period_to:
              results.append(item)
          
          return results
        
        return None