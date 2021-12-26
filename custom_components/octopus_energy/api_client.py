import logging
import json
import aiohttp
from datetime import (timedelta)
from homeassistant.util.dt import (utcnow, as_utc, now, as_local, parse_datetime)

from .utils import (
  get_tariff_parts
)

_LOGGER = logging.getLogger(__name__)

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
        data = await self.__async_read_response(response, url)
        if ("properties" in data):
          # We're only supporting one property at the moment and we don't want to expose addresses
          properties = data["properties"]
          prop = next(current_prop for current_prop in properties if current_prop["moved_out_at"] == None)
          if (prop == None):
            raise Exception("Failed to find occupied property")

          return {
            "electricity_meter_points": prop["electricity_meter_points"],
            "gas_meter_points": prop["gas_meter_points"]
          }
        
        return None

  async def async_get_standard_rates(self, product_code, tariff_code, period_from, period_to):
    """Get the current standard rates"""
    results = []
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          results = self.__process_rates(data, period_from, period_to, tariff_code)
        except:
          _LOGGER.error(f'Failed to extract standard rates: {url}')
          raise

    return results

  async def async_get_day_night_rates(self, product_code, tariff_code, period_from, period_to):
    """Get the current day and night rates"""
    results = []
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/day-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)

          # Normalise the rates to be in 30 minute increments and remove any rates that fall outside of our day period 
          # (7am to 12am UK time https://octopus.energy/help-and-faqs/categories/tariffs/eco-seven/)
          day_rates = self.__process_rates(data, period_from, period_to, tariff_code)
          for rate in day_rates:
            if (self.__is_between_local_times(rate, "07:00:00", "23:59:59")) == True:
              results.append(rate)
        except:
          _LOGGER.error(f'Failed to extract day rates: {url}')
          raise

      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/night-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)

          # Normalise the rates to be in 30 minute increments and remove any rates that fall outside of our night period 
          # (12am to 7am UK time https://octopus.energy/help-and-faqs/categories/tariffs/eco-seven/)
          night_rates = self.__process_rates(data, period_from, period_to, tariff_code)
          for rate in night_rates:
            if (self.__is_between_local_times(rate, "00:00:00", "07:00:00")) == True:
              results.append(rate)
        except:
          _LOGGER.error(f'Failed to extract night rates: {url}')
          raise

    # Because we retrieve our day and night periods separately over a 2 day period, we need to sort our rates 
    results.sort(key=self.__get_valid_from)
    _LOGGER.error(results)

    return results

  async def async_get_rates(self, tariff_code, period_from, period_to):
    """Get the current rates"""

    tariff_parts = get_tariff_parts(tariff_code)
    product_code = tariff_parts["product_code"]

    if (tariff_parts["rate"].startswith("1")):
      return await self.async_get_standard_rates(product_code, tariff_code, period_from, period_to)
    else:
      return await self.async_get_day_night_rates(product_code, tariff_code, period_from, period_to)

  async def async_electricity_consumption(self, mpan, serial_number, period_from, period_to):
    """Get the current electricity consumption"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/electricity-meter-points/{mpan}/meters/{serial_number}/consumption?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        
        data = await self.__async_read_response(response, url)

        if ("results" in data):
          data = data["results"]
          results = []
          for item in data:
            item = self.__process_consumption(item)

            # For some reason, the end point returns slightly more data than we requested, so we need to filter out
            # the results
            if as_utc(item["interval_start"]) >= period_from and as_utc(item["interval_end"]) <= period_to:
              results.append(item)
          
          return results
        
        return None

  async def async_gas_rates(self, tariff_code, period_from, period_to):
    """Get the gas rates"""
    tariff_parts = get_tariff_parts(tariff_code)
    product_code = tariff_parts["product_code"]

    results = []
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/gas-tariffs/{tariff_code}/standard-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          results = self.__process_rates(data, period_from, period_to, tariff_code)
        except:
          _LOGGER.error(f'Failed to extract standard gas rates: {url}')
          raise

    return results

  async def async_gas_consumption(self, mprn, serial_number, period_from, period_to):
    """Get the current gas rates"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/gas-meter-points/{mprn}/meters/{serial_number}/consumption?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response(response, url)
        if ("results" in data):
          data = data["results"]
          results = []
          for item in data:
            item = self.__process_consumption(item)

            # For some reason, the end point returns slightly more data than we requested, so we need to filter out
            # the results
            if as_utc(item["interval_start"]) >= period_from and as_utc(item["interval_end"]) <= period_to:
              results.append(item)
          
          return results
        
        return None

  async def async_get_products(self, is_variable):
    """Get all products"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products?is_variable={is_variable}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response(response, url)
        if ("results" in data):
          return data["results"]

    return []

  async def async_get_electricity_standing_charges(self, tariff_code, period_from, period_to):
    """Get the electricity standing charges"""
    tariff_parts = get_tariff_parts(tariff_code)
    product_code = tariff_parts["product_code"]
    
    result = None
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standing-charges?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          if ("results" in data and len(data["results"]) > 0):
            result = {
              "value_exc_vat": float(data["results"][0]["value_exc_vat"]),
              "value_inc_vat": float(data["results"][0]["value_inc_vat"])
            }
        except:
          _LOGGER.error(f'Failed to extract electricity standing charges: {url}')
          raise

    return result

  async def async_get_gas_standing_charges(self, tariff_code, period_from, period_to):
    """Get the gas standing charges"""
    tariff_parts = get_tariff_parts(tariff_code)
    product_code = tariff_parts["product_code"]

    result = None
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/gas-tariffs/{tariff_code}/standing-charges?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          if ("results" in data and len(data["results"]) > 0):
            result = {
              "value_exc_vat": float(data["results"][0]["value_exc_vat"]),
              "value_inc_vat": float(data["results"][0]["value_inc_vat"])
            }
        except:
          _LOGGER.error(f'Failed to extract gas standing charges: {url}')
          raise

    return result

  def __get_valid_from(self, rate):
    return rate["valid_from"]

  def __is_between_local_times(self, rate, target_from_time, target_to_time):
    """Determines if a current rate is between two times"""
    local_now = now()

    rate_local_valid_from = as_local(rate["valid_from"])
    rate_local_valid_to = as_local(rate["valid_to"])

    # We need to convert our times into local time to account for BST to ensure that our rate is valid between the target times.
    from_date_time = as_local(parse_datetime(rate_local_valid_from.strftime(f"%Y-%m-%dT{target_from_time}{local_now.strftime('%z')}")))
    to_date_time = as_local(parse_datetime(rate_local_valid_from.strftime(f"%Y-%m-%dT{target_to_time}{local_now.strftime('%z')}")))

    _LOGGER.error('is_valid: %s; from_date_time: %s; to_date_time: %s; rate_local_valid_from: %s; rate_local_valid_to: %s', rate_local_valid_from >= from_date_time and rate_local_valid_from < to_date_time, from_date_time, to_date_time, rate_local_valid_from, rate_local_valid_to)

    return rate_local_valid_from >= from_date_time and rate_local_valid_from < to_date_time

  def __process_consumption(self, item):
    return {
      "consumption": float(item["consumption"]),
      "interval_start": as_utc(parse_datetime(item["interval_start"])),
      "interval_end": as_utc(parse_datetime(item["interval_end"]))
    }

  def __process_rates(self, data, period_from, period_to, tariff_code):
    """Process the collection of rates to ensure they're in 30 minute periods"""
    starting_period_from = period_from
    results = []
    if ("results" in data):
      # We need to normalise our data into 30 minute increments so that all of our rates across all tariffs are the same and it's 
      # easier to calculate our target rate sensors
      for item in data["results"]:
        value_exc_vat = float(item["value_exc_vat"])
        value_inc_vat = float(item["value_inc_vat"])

        if "valid_from" in item and item["valid_from"] != None:
          valid_from = as_utc(parse_datetime(item["valid_from"]))

          # If we're on a fixed rate, then our current time could be in the past so we should go from
          # our target period from date otherwise we could be adjusting times quite far in the past
          if (valid_from < starting_period_from):
            valid_from = starting_period_from
        else:
          valid_from = starting_period_from

        # Some rates don't have end dates, so we should treat this as our period to target
        if "valid_to" in item and item["valid_to"] != None:
          target_date = as_utc(parse_datetime(item["valid_to"]))
        else:
          target_date = period_to
        
        while valid_from < target_date:
          valid_to = valid_from + timedelta(minutes=30)
          results.append({
            "value_exc_vat": value_exc_vat,
            "value_inc_vat": value_inc_vat,
            "valid_from": valid_from,
            "valid_to": valid_to,
            "tariff_code": tariff_code
          })

          valid_from = valid_to
          starting_period_from = valid_to
      
    return results

  async def __async_read_response(self, response, url):
    """Reads the response, logging any json errors"""
    text = await response.text()
    try:
      return json.loads(text)
    except:
      raise Exception(f'Failed to extract response json: {url}; {text}')
