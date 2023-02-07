import logging
import json
import aiohttp
from datetime import (timedelta)
from homeassistant.util.dt import (as_utc, now, as_local, parse_datetime)

from .utils import (
  get_tariff_parts,
  get_valid_from,
  rates_to_thirty_minute_increments
)

_LOGGER = logging.getLogger(__name__)

api_token_query = '''mutation {{
	obtainKrakenToken(input: {{ APIKey: "{api_key}" }}) {{
		token
	}}
}}'''

account_query = '''query {{
  account(accountNumber: "{account_id}") {{
    electricityAgreements(active: true) {{
			meterPoint {{
				mpan
				meters(includeInactive: false) {{
					serialNumber
          smartExportElectricityMeter {{
						deviceId
					}}
          smartImportElectricityMeter {{
						deviceId
					}}
				}}
				agreements {{
					validFrom
					validTo
					tariff {{
						...on StandardTariff {{
							tariffCode
						}}
						...on DayNightTariff {{
							tariffCode
						}}
						...on ThreeRateTariff {{
							tariffCode
						}}
						...on HalfHourlyTariff {{
							tariffCode
						}}
            ...on PrepayTariff {{
							tariffCode
						}}
					}}
				}}
			}}
    }}
    gasAgreements(active: true) {{
			meterPoint {{
				mprn
				meters(includeInactive: false) {{
					serialNumber
          consumptionUnits
				}}
				agreements {{
					validFrom
					validTo
					tariff {{
						tariffCode
					}}
				}}
			}}
    }}
  }}
}}'''

saving_session_query = '''query {{
	savingSessions {{
		account(accountNumber: "{account_id}") {{
			hasJoinedCampaign
			joinedEvents {{
				eventId
				startAt
				endAt
			}}
		}}
	}}
  octoPoints {{
		account(accountNumber: "{account_id}") {{
			currentPointsInWallet
    }}
  }}
}}'''

class OctopusEnergyApiClient:

  def __init__(self, api_key):
    if (api_key == None):
      raise Exception('API KEY is not set')

    self._api_key = api_key
    self._base_url = 'https://api.octopus.energy'

    self._graphql_token = None
    self._graphql_expiration = None

    self._product_tracker_cache = dict()

  async def async_refresh_token(self):
    """Get the user's refresh token"""
    if (self._graphql_expiration != None and (self._graphql_expiration - timedelta(minutes=5)) > now()):
      return

    async with aiohttp.ClientSession() as client:
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": api_token_query.format(api_key=self._api_key) }
      async with client.post(url, json=payload) as token_response:
        token_response_body = await self.__async_read_response(token_response, url)
        if (token_response_body != None and "data" in token_response_body):
          self._graphql_token = token_response_body["data"]["obtainKrakenToken"]["token"]
          self._graphql_expiration = now() + timedelta(hours=1)
        else:
          _LOGGER.error("Failed to retrieve auth token")
          raise Exception('Failed to refresh token')

  async def async_get_account(self, account_id):
    """Get the user's account"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession() as client:
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": account_query.format(account_id=account_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as account_response:
        account_response_body = await self.__async_read_response(account_response, url)

        _LOGGER.debug(account_response_body)

        if (account_response_body != None and "data" in account_response_body):
          return {
            "electricity_meter_points": list(map(lambda mp: {
              "mpan": mp["meterPoint"]["mpan"],
              "meters": list(map(lambda m: {
                "serial_number": m["serialNumber"],
                "is_export": m["smartExportElectricityMeter"] != None,
                "is_smart_meter": m["smartImportElectricityMeter"] != None or m["smartExportElectricityMeter"] != None,
              }, mp["meterPoint"]["meters"])),
              "agreements": list(map(lambda a: {
                "valid_from": a["validFrom"],
                "valid_to": a["validTo"],
                "tariff_code": a["tariff"]["tariffCode"] if "tariff" in a and "tariffCode" in a["tariff"] else None,
              }, mp["meterPoint"]["agreements"]))
            }, account_response_body["data"]["account"]["electricityAgreements"])),
            "gas_meter_points": list(map(lambda mp: {
              "mprn": mp["meterPoint"]["mprn"],
              "meters": list(map(lambda m: {
                "serial_number": m["serialNumber"],
                "consumption_units": m["consumptionUnits"],
              }, mp["meterPoint"]["meters"])),
              "agreements": list(map(lambda a: {
                "valid_from": a["validFrom"],
                "valid_to": a["validTo"],
                "tariff_code": a["tariff"]["tariffCode"] if "tariff" in a and "tariffCode" in a["tariff"] else None,
              }, mp["meterPoint"]["agreements"]))
            }, account_response_body["data"]["account"]["gasAgreements"])),
          }
        else:
          _LOGGER.error("Failed to retrieve account")
    
    return None

  async def async_get_saving_sessions(self, account_id):
    """Get the user's seasons savings"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession() as client:
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": saving_session_query.format(account_id=account_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as account_response:
        response_body = await self.__async_read_response(account_response, url)

        if (response_body != None and "data" in response_body):
          return {
            "points": int(response_body["data"]["octoPoints"]["account"]["currentPointsInWallet"]),
            "events": list(map(lambda ev: {
              "start": as_utc(parse_datetime(ev["startAt"])),
              "end": as_utc(parse_datetime(ev["endAt"]))
            }, response_body["data"]["savingSessions"]["account"]["joinedEvents"]))
          }
        else:
          _LOGGER.error("Failed to retrieve account")
    
    return None

  async def async_get_electricity_standard_rates(self, product_code, tariff_code, period_from, period_to): 
    """Get the current standard rates"""
    results = []
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          if data == None:
            return None
          results = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code)
        except:
          _LOGGER.error(f'Failed to extract standard rates: {url}')
          raise

    return results

  async def async_get_electricity_day_night_rates(self, product_code, tariff_code, is_smart_meter, period_from, period_to):
    """Get the current day and night rates"""
    results = []
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/day-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          if data == None:
            return None

          # Normalise the rates to be in 30 minute increments and remove any rates that fall outside of our day period 
          day_rates = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code)
          for rate in day_rates:
            if (self.__is_night_rate(rate, is_smart_meter)) == False:
              results.append(rate)
        except:
          _LOGGER.error(f'Failed to extract day rates: {url}')
          raise

      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/night-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          if data == None:
            return None

          # Normalise the rates to be in 30 minute increments and remove any rates that fall outside of our night period 
          night_rates = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code)
          for rate in night_rates:
            if (self.__is_night_rate(rate, is_smart_meter)) == True:
              results.append(rate)
        except:
          _LOGGER.error(f'Failed to extract night rates: {url}')
          raise

    # Because we retrieve our day and night periods separately over a 2 day period, we need to sort our rates 
    results.sort(key=get_valid_from)
    _LOGGER.debug(results)

    return results

  async def async_get_electricity_rates(self, tariff_code, is_smart_meter, period_from, period_to):
    """Get the current rates"""

    tariff_parts = get_tariff_parts(tariff_code)
    product_code = tariff_parts["product_code"]

    if (await self.__async_is_tracker_tariff(tariff_code)):
      return await self.__async_get_tracker_rates__(tariff_code, period_from, period_to)
    elif (tariff_parts["rate"].startswith("1")):
      return await self.async_get_electricity_standard_rates(product_code, tariff_code, period_from, period_to)
    else:
      return await self.async_get_electricity_day_night_rates(product_code, tariff_code, is_smart_meter, period_from, period_to)

  async def async_get_electricity_consumption(self, mpan, serial_number, period_from, period_to):
    """Get the current electricity consumption"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/electricity-meter-points/{mpan}/meters/{serial_number}/consumption?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        
        data = await self.__async_read_response(response, url)
        if (data != None and "results" in data):
          data = data["results"]
          results = []
          for item in data:
            item = self.__process_consumption(item)

            # For some reason, the end point returns slightly more data than we requested, so we need to filter out
            # the results
            if as_utc(item["interval_start"]) >= period_from and as_utc(item["interval_end"]) <= period_to:
              results.append(item)
          
          results.sort(key=self.__get_interval_end)
          return results
        
        return None

  async def async_get_gas_rates(self, tariff_code, period_from, period_to):
    """Get the gas rates"""
    tariff_parts = get_tariff_parts(tariff_code)
    product_code = tariff_parts["product_code"]

    if (await self.__async_is_tracker_tariff(tariff_code)):
      return await self.__async_get_tracker_rates__(tariff_code, period_from, period_to)
    
    results = []
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/gas-tariffs/{tariff_code}/standard-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          if data == None:
            return None

          results = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code)
        except:
          _LOGGER.error(f'Failed to extract standard gas rates: {url}')
          raise

    return results

  async def async_get_gas_consumption(self, mprn, serial_number, period_from, period_to):
    """Get the current gas rates"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/gas-meter-points/{mprn}/meters/{serial_number}/consumption?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response(response, url)
        if (data != None and "results" in data):
          data = data["results"]
          results = []
          for item in data:
            item = self.__process_consumption(item)

            # For some reason, the end point returns slightly more data than we requested, so we need to filter out
            # the results
            if as_utc(item["interval_start"]) >= period_from and as_utc(item["interval_end"]) <= period_to:
              results.append(item)
          
          results.sort(key=self.__get_interval_end)
          return results
        
        return None

  async def async_get_products(self, is_variable):
    """Get all products"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products?is_variable={is_variable}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response(response, url)
        if (data != None and "results" in data):
          return data["results"]

    return []

  async def async_get_electricity_standing_charge(self, tariff_code, period_from, period_to):
    """Get the electricity standing charges"""
    tariff_parts = get_tariff_parts(tariff_code)
    product_code = tariff_parts["product_code"]

    if await self.__async_is_tracker_tariff(tariff_code):
      return await self.__async_get_tracker_standing_charge__(tariff_code, period_from, period_to)
    
    result = None
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standing-charges?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          if (data != None and "results" in data and len(data["results"]) > 0):
            result = {
              "value_exc_vat": float(data["results"][0]["value_exc_vat"]),
              "value_inc_vat": float(data["results"][0]["value_inc_vat"])
            }
        except:
          _LOGGER.error(f'Failed to extract electricity standing charges: {url}')
          raise

    return result

  async def async_get_gas_standing_charge(self, tariff_code, period_from, period_to):
    """Get the gas standing charges"""
    tariff_parts = get_tariff_parts(tariff_code)
    product_code = tariff_parts["product_code"]

    if await self.__async_is_tracker_tariff(tariff_code):
      return await self.__async_get_tracker_standing_charge__(tariff_code, period_from, period_to)

    result = None
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/gas-tariffs/{tariff_code}/standing-charges?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          if (data != None and "results" in data and len(data["results"]) > 0):
            result = {
              "value_exc_vat": float(data["results"][0]["value_exc_vat"]),
              "value_inc_vat": float(data["results"][0]["value_inc_vat"])
            }
        except:
          _LOGGER.error(f'Failed to extract gas standing charges: {url}')
          raise

    return result

  async def __async_is_tracker_tariff(self, tariff_code):
    tariff_parts = get_tariff_parts(tariff_code)
    product_code = tariff_parts["product_code"]

    if product_code in self._product_tracker_cache:
      return self._product_tracker_cache[product_code]

    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'https://api.octopus.energy/v1/products/{product_code}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response(response, url)
        if data == None:
          return False
        
        is_tracker = "is_tracker" in data and data["is_tracker"]
        self._product_tracker_cache[product_code] = is_tracker
        return is_tracker

  async def __async_get_tracker_rates__(self, tariff_code, period_from, period_to):
    """Get the tracker rates"""

    results = []
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'https://octopus.energy/api/v1/tracker/{tariff_code}/daily/past/1/0'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          if data == None:
            return None

          items = []
          for period in data["periods"]:
            valid_from = parse_datetime(f'{period["date"]}T00:00:00Z')
            valid_to = parse_datetime(f'{period["date"]}T00:00:00Z') + timedelta(days=1)
            vat = float(period["breakdown"]["standing_charge"]["VAT"])

            if ((valid_from >= period_from and valid_from <= period_to) or (valid_to >= period_from and valid_to <= period_to)):
              vat = float(period["breakdown"]["unit_charge"]["VAT"])
              items.append(
                {
                  "valid_from": valid_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
                  "valid_to": valid_to.strftime("%Y-%m-%dT%H:%M:%SZ"),
                  "value_exc_vat": float(period["unit_rate"]) - vat,
                  "value_inc_vat": float(period["unit_rate"]),
                }
              )

          results = rates_to_thirty_minute_increments({ "results": items }, period_from, period_to, tariff_code)
        except:
          _LOGGER.error(f'Failed to extract tracker gas rates: {url}')
          raise

    return results

  async def __async_get_tracker_standing_charge__(self, tariff_code, period_from, period_to):
    """Get the tracker standing charge"""

    results = []
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'https://octopus.energy/api/v1/tracker/{tariff_code}/daily/past/1/0'
      async with client.get(url, auth=auth) as response:
        try:
          data = await self.__async_read_response(response, url)
          if data == None:
            return None

          for period in data["periods"]:
            valid_from = parse_datetime(f'{period["date"]}T00:00:00Z')
            valid_to = parse_datetime(f'{period["date"]}T00:00:00Z') + timedelta(days=1)
            if ((valid_from >= period_from and valid_from <= period_to) or (valid_to >= period_from and valid_to <= period_to)):
              vat = float(period["breakdown"]["standing_charge"]["VAT"])
              return {
                "value_exc_vat": float(period["standing_charge"]) - vat,
                "value_inc_vat": float(period["standing_charge"])
              }
        except:
          _LOGGER.error(f'Failed to extract tracker gas rates: {url}')
          raise

    return None

  def __get_interval_end(self, item):
    return item["interval_end"]

  def __is_night_rate(self, rate, is_smart_meter):
    # Normally the economy seven night rate is between 12am and 7am UK time
    # https://octopus.energy/help-and-faqs/articles/what-is-an-economy-7-meter-and-tariff/
    # However, if a smart meter is being used then the times are between 12:30am and 7:30am UTC time
    # https://octopus.energy/help-and-faqs/articles/what-happens-to-my-economy-seven-e7-tariff-when-i-have-a-smart-meter-installed/
    if is_smart_meter:
        is_night_rate = self.__is_between_times(rate, "00:30:00", "07:30:00", True)
    else:
        is_night_rate = self.__is_between_times(rate, "00:00:00", "07:00:00", False)
    return is_night_rate

  def __is_between_times(self, rate, target_from_time, target_to_time, use_utc):
    """Determines if a current rate is between two times"""
    rate_local_valid_from = as_local(rate["valid_from"])
    rate_local_valid_to = as_local(rate["valid_to"])

    if use_utc:
        rate_utc_valid_from = as_utc(rate["valid_from"])
        # We need to convert our times into local time to account for BST to ensure that our rate is valid between the target times.
        from_date_time = as_local(parse_datetime(rate_utc_valid_from.strftime(f"%Y-%m-%dT{target_from_time}Z")))
        to_date_time = as_local(parse_datetime(rate_utc_valid_from.strftime(f"%Y-%m-%dT{target_to_time}Z")))
    else:
        local_now = now()
        # We need to convert our times into local time to account for BST to ensure that our rate is valid between the target times.
        from_date_time = as_local(parse_datetime(rate_local_valid_from.strftime(f"%Y-%m-%dT{target_from_time}{local_now.strftime('%z')}")))
        to_date_time = as_local(parse_datetime(rate_local_valid_from.strftime(f"%Y-%m-%dT{target_to_time}{local_now.strftime('%z')}")))

    _LOGGER.debug('is_valid: %s; from_date_time: %s; to_date_time: %s; rate_local_valid_from: %s; rate_local_valid_to: %s', rate_local_valid_from >= from_date_time and rate_local_valid_from < to_date_time, from_date_time, to_date_time, rate_local_valid_from, rate_local_valid_to)

    return rate_local_valid_from >= from_date_time and rate_local_valid_from < to_date_time

  def __process_consumption(self, item):
    return {
      "consumption": float(item["consumption"]),
      "interval_start": as_utc(parse_datetime(item["interval_start"])),
      "interval_end": as_utc(parse_datetime(item["interval_end"]))
    }

  async def __async_read_response(self, response, url):
    """Reads the response, logging any json errors"""

    text = await response.text()

    if response.status >= 400:
      _LOGGER.error(f'Request failed ({url}): {response.status}; {text}')
      return None

    try:
      return json.loads(text)
    except:
      raise Exception(f'Failed to extract response json: {url}; {text}')
