import aiohttp
from datetime import datetime
from homeassistant.util.dt import as_utc

class OctopusEnergyApiClient:

  def __init__(self, api_key, tariff):
    self._api_key = api_key
    self._tariff = tariff
    self._base_url = 'https://api.octopus.energy'

  async def async_get_rates(self, product_code, tariff_code):
    """Get the current rates"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      async with client.get(f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates', auth=auth) as response:
        data = await response.json()
        data = data["results"]
        
        for item in data:
          item["value_exc_vat"] = float(item["value_exc_vat"])
          item["value_inc_vat"] = float(item["value_inc_vat"])
          item["valid_from"] = as_utc(datetime.strptime(item["valid_from"], "%Y-%m-%dT%H:%M:%SZ"))
          item["valid_to"] = as_utc(datetime.strptime(item["valid_to"], "%Y-%m-%dT%H:%M:%SZ"))

          # TODO: Update prices for "go" tariff
        
        return data

  async def async_latest_electricity_consumption(self, mpan, serial_number):
    """Get the current rates"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      async with client.get(f'{self._base_url}/v1/electricity-meter-points/{mpan}/meters/{serial_number}/consumption?page_size=1', auth=auth) as response:
        data = await response.json()
        data = data["results"]
        
        for item in data:
          item["consumption"] = float(item["consumption"])
          item["interval_start"] = as_utc(datetime.strptime(item["interval_start"], "%Y-%m-%dT%H:%M:%SZ"))
          item["interval_end"] = as_utc(datetime.strptime(item["interval_end"], "%Y-%m-%dT%H:%M:%SZ"))
        
        if (len(data) > 0):
          return data[0]
        
        return None

  async def async_latest_gas_consumption(self, mprn, serial_number):
    """Get the current rates"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      async with client.get(f'{self._base_url}/v1/gas-meter-points/{mprn}/meters/{serial_number}/consumption?page_size=1', auth=auth) as response:
        data = await response.json()
        data = data["results"]
        
        for item in data:
          item["consumption"] = float(item["consumption"])
          item["interval_start"] = as_utc(datetime.strptime(item["interval_start"], "%Y-%m-%dT%H:%M:%SZ"))
          item["interval_end"] = as_utc(datetime.strptime(item["interval_end"], "%Y-%m-%dT%H:%M:%SZ"))
        
        if (len(data) > 0):
          return data[0]
        
        return None