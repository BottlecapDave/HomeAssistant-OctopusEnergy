import logging
import json
import aiohttp
from datetime import (datetime, timedelta, time)

from homeassistant.util.dt import (as_utc, now, as_local, parse_datetime)

from ..utils import (
  get_tariff_parts,
)

from .intelligent_settings import IntelligentSettings
from .intelligent_dispatches import IntelligentDispatchItem, IntelligentDispatches

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
          makeAndType
					serialNumber
          makeAndType
          meterType
          smartExportElectricityMeter {{
						deviceId
            manufacturer
            model
            firmwareVersion
					}}
          smartImportElectricityMeter {{
						deviceId
            manufacturer
            model
            firmwareVersion
					}}
				}}
				agreements {{
					validFrom
					validTo
					tariff {{
						...on StandardTariff {{
							tariffCode
              productCode
						}}
						...on DayNightTariff {{
							tariffCode
              productCode
						}}
						...on ThreeRateTariff {{
							tariffCode
              productCode
						}}
						...on HalfHourlyTariff {{
							tariffCode
              productCode
						}}
            ...on PrepayTariff {{
							tariffCode
              productCode
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
          modelName
          mechanism
          smartGasMeter {{
						deviceId
            manufacturer
            model
            firmwareVersion
					}}
				}}
				agreements {{
					validFrom
					validTo
					tariff {{
						tariffCode
            productCode
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

live_consumption_query = '''query {{
	smartMeterTelemetry(
    deviceId: "{device_id}"
    grouping: HALF_HOURLY 
		start: "{period_from}"
		end: "{period_to}"
	) {{
    readAt
		consumptionDelta
    demand
	}}
}}'''

intelligent_dispatches_query = '''query {{
	plannedDispatches(accountNumber: "{account_id}") {{
		startDt
		endDt
    delta
    meta {{
			source
      location
		}}
	}}
	completedDispatches(accountNumber: "{account_id}") {{
		startDt
		endDt
    delta
    meta {{
			source
      location
		}}
	}}
}}'''

intelligent_device_query = '''query {{
	registeredKrakenflexDevice(accountNumber: "{account_id}") {{
		krakenflexDeviceId
		vehicleMake
		vehicleModel
    vehicleBatterySizeInKwh
		chargePointMake
		chargePointModel
    chargePointPowerInKw
	}}
}}'''

intelligent_settings_query = '''query vehicleChargingPreferences {{
  vehicleChargingPreferences(accountNumber: "{account_id}") {{
    weekdayTargetTime
    weekdayTargetSoc
    weekendTargetTime
    weekendTargetSoc
  }}
  registeredKrakenflexDevice(accountNumber: "{account_id}") {{
    suspended
	}}
}}'''

intelligent_settings_mutation = '''mutation vehicleChargingPreferences {{
  setVehicleChargePreferences(
    input: {{
      accountNumber: "{account_id}"
      weekdayTargetSoc: {weekday_target_percentage}
      weekendTargetSoc: {weekend_target_percentage}
      weekdayTargetTime: "{weekday_target_time}"
      weekendTargetTime: "{weekend_target_time}"
    }}
  ) {{
     krakenflexDevice {{
			 krakenflexDeviceId
		}}
  }}
}}'''

intelligent_turn_on_bump_charge_mutation = '''mutation {{
	triggerBoostCharge(
    input: {{
      accountNumber: "{account_id}"
    }}
  ) {{
		krakenflexDevice {{
			 krakenflexDeviceId
		}}
	}}
}}'''

intelligent_turn_off_bump_charge_mutation = '''mutation {{
	deleteBoostCharge(
    input: {{
      accountNumber: "{account_id}"
    }}
  ) {{
		krakenflexDevice {{
			 krakenflexDeviceId
		}}
	}}
}}'''

intelligent_turn_on_smart_charge_mutation = '''mutation {{
	resumeControl(
    input: {{
      accountNumber: "{account_id}"
    }}
  ) {{
		krakenflexDevice {{
			 krakenflexDeviceId
		}}
	}}
}}'''

intelligent_turn_off_smart_charge_mutation = '''mutation {{
	suspendControl(
    input: {{
      accountNumber: "{account_id}"
    }}
  ) {{
		krakenflexDevice {{
			 krakenflexDeviceId
		}}
	}}
}}'''

def get_valid_from(rate):
  return rate["valid_from"]
    
def rates_to_thirty_minute_increments(data, period_from: datetime, period_to: datetime, tariff_code: str, price_cap: float = None):
  """Process the collection of rates to ensure they're in 30 minute periods"""
  starting_period_from = period_from
  results = []
  if ("results" in data):
    items = data["results"]
    items.sort(key=get_valid_from)

    # We need to normalise our data into 30 minute increments so that all of our rates across all tariffs are the same and it's 
    # easier to calculate our target rate sensors
    for item in items:
      value_inc_vat = float(item["value_inc_vat"])

      is_capped = False
      if (price_cap is not None and value_inc_vat > price_cap):
        value_inc_vat = price_cap
        is_capped = True

      if "valid_from" in item and item["valid_from"] is not None:
        valid_from = as_utc(parse_datetime(item["valid_from"]))

        # If we're on a fixed rate, then our current time could be in the past so we should go from
        # our target period from date otherwise we could be adjusting times quite far in the past
        if (valid_from < starting_period_from):
          valid_from = starting_period_from
      else:
        valid_from = starting_period_from

      # Some rates don't have end dates, so we should treat this as our period to target
      if "valid_to" in item and item["valid_to"] is not None:
        target_date = as_utc(parse_datetime(item["valid_to"]))

        # Cap our target date to our end period
        if (target_date > period_to):
          target_date = period_to
      else:
        target_date = period_to
      
      while valid_from < target_date:
        valid_to = valid_from + timedelta(minutes=30)
        results.append({
          "value_inc_vat": value_inc_vat,
          "valid_from": valid_from,
          "valid_to": valid_to,
          "tariff_code": tariff_code,
          "is_capped": is_capped
        })

        valid_from = valid_to
        starting_period_from = valid_to
    
  return results

class ServerError(Exception): ...

class RequestError(Exception): ...

class OctopusEnergyApiClient:

  def __init__(self, api_key, electricity_price_cap = None, gas_price_cap = None, timeout_in_seconds = 15):
    if (api_key is None):
      raise Exception('API KEY is not set')

    self._api_key = api_key
    self._base_url = 'https://api.octopus.energy'

    self._graphql_token = None
    self._graphql_expiration = None

    self._product_tracker_cache = dict()

    self._electricity_price_cap = electricity_price_cap
    self._gas_price_cap = gas_price_cap

    self.timeout = aiohttp.ClientTimeout(total=timeout_in_seconds)

  async def async_refresh_token(self):
    """Get the user's refresh token"""
    if (self._graphql_expiration is not None and (self._graphql_expiration - timedelta(minutes=5)) > now()):
      return

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": api_token_query.format(api_key=self._api_key) }
      async with client.post(url, json=payload) as token_response:
        token_response_body = await self.__async_read_response__(token_response, url)
        if (token_response_body is not None and 
            "data" in token_response_body and
            "obtainKrakenToken" in token_response_body["data"] and 
            token_response_body["data"]["obtainKrakenToken"] is not None and
            "token" in token_response_body["data"]["obtainKrakenToken"]):
          
          self._graphql_token = token_response_body["data"]["obtainKrakenToken"]["token"]
          self._graphql_expiration = now() + timedelta(hours=1)
        else:
          _LOGGER.error("Failed to retrieve auth token")

  async def async_get_account(self, account_id):
    """Get the user's account"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": account_query.format(account_id=account_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as account_response:
        account_response_body = await self.__async_read_response__(account_response, url)

        _LOGGER.debug(f'account: {account_response_body}')

        if (account_response_body is not None and 
            "data" in account_response_body and 
            "account" in account_response_body["data"] and 
            account_response_body["data"]["account"] is not None):
          return {
            "id": account_id,
            "electricity_meter_points": list(map(lambda mp: {
                "mpan": mp["meterPoint"]["mpan"],
                "meters": list(map(lambda m: {
                    "serial_number": m["serialNumber"],
                    "is_export": m["smartExportElectricityMeter"] is not None,
                    "is_smart_meter": f'{m["meterType"]}'.startswith("S1") or f'{m["meterType"]}'.startswith("S2"),
                    "device_id": m["smartImportElectricityMeter"]["deviceId"] if m["smartImportElectricityMeter"] is not None else None,
                    "manufacturer": m["smartImportElectricityMeter"]["manufacturer"] 
                      if m["smartImportElectricityMeter"] is not None 
                      else m["smartExportElectricityMeter"]["manufacturer"] 
                      if m["smartExportElectricityMeter"] is not None
                      else m["makeAndType"],
                    "model": m["smartImportElectricityMeter"]["model"] 
                      if m["smartImportElectricityMeter"] is not None 
                      else m["smartExportElectricityMeter"]["model"] 
                      if m["smartExportElectricityMeter"] is not None
                      else None,
                    "firmware": m["smartImportElectricityMeter"]["firmwareVersion"] 
                      if m["smartImportElectricityMeter"] is not None 
                      else m["smartExportElectricityMeter"]["firmwareVersion"] 
                      if m["smartExportElectricityMeter"] is not None
                      else None
                  },
                  mp["meterPoint"]["meters"]
                  if "meterPoint" in mp and "meters" in mp["meterPoint"] and mp["meterPoint"]["meters"] is not None
                  else []
                )),
                "agreements": list(map(lambda a: {
                  "valid_from": a["validFrom"],
                  "valid_to": a["validTo"],
                  "tariff_code": a["tariff"]["tariffCode"] if "tariff" in a and "tariffCode" in a["tariff"] else None,
                  "product_code": a["tariff"]["productCode"] if "tariff" in a and "productCode" in a["tariff"] else None,
                }, 
                mp["meterPoint"]["agreements"]
                if "meterPoint" in mp and "agreements" in mp["meterPoint"] and mp["meterPoint"]["agreements"] is not None
                else []
              ))
            }, 
            account_response_body["data"]["account"]["electricityAgreements"]
            if "electricityAgreements" in account_response_body["data"]["account"] and account_response_body["data"]["account"]["electricityAgreements"] is not None
            else []
          )),
            "gas_meter_points": list(map(lambda mp: {
              "mprn": mp["meterPoint"]["mprn"],
              "meters": list(map(lambda m: {
                  "serial_number": m["serialNumber"],
                  "consumption_units": m["consumptionUnits"],
                  "is_smart_meter": m["mechanism"] == "S1" or m["mechanism"] == "S2",
                  "device_id": m["smartGasMeter"]["deviceId"] if m["smartGasMeter"] is not None else None,
                  "manufacturer": m["smartGasMeter"]["manufacturer"] 
                    if m["smartGasMeter"] is not None 
                    else m["modelName"],
                  "model": m["smartGasMeter"]["model"] 
                    if m["smartGasMeter"] is not None 
                    else None,
                  "firmware": m["smartGasMeter"]["firmwareVersion"] 
                    if m["smartGasMeter"] is not None 
                    else None
                },
                mp["meterPoint"]["meters"]
                if "meterPoint" in mp and "meters" in mp["meterPoint"] and mp["meterPoint"]["meters"] is not None
                else []
              )),
              "agreements": list(map(lambda a: {
                  "valid_from": a["validFrom"],
                  "valid_to": a["validTo"],
                  "tariff_code": a["tariff"]["tariffCode"] if "tariff" in a and "tariffCode" in a["tariff"] else None,
                  "product_code": a["tariff"]["productCode"] if "tariff" in a and "productCode" in a["tariff"] else None,
                },
                mp["meterPoint"]["agreements"]
                if "meterPoint" in mp and "agreements" in mp["meterPoint"] and mp["meterPoint"]["agreements"] is not None
                else []
              ))
            }, 
            account_response_body["data"]["account"]["gasAgreements"] 
            if "gasAgreements" in account_response_body["data"]["account"] and account_response_body["data"]["account"]["gasAgreements"] is not None
            else []
          )),
        }
        else:
          _LOGGER.error("Failed to retrieve account")
    
    return None

  async def async_get_saving_sessions(self, account_id):
    """Get the user's seasons savings"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": saving_session_query.format(account_id=account_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as account_response:
        response_body = await self.__async_read_response__(account_response, url)

        if (response_body is not None and "data" in response_body):
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

  async def async_get_smart_meter_consumption(self, device_id: str, period_from: datetime, period_to: datetime):
    """Get the user's smart meter consumption"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'

      payload = { "query": live_consumption_query.format(device_id=device_id, period_from=period_from.strftime("%Y-%m-%dT%H:%M:%S%z"), period_to=period_to.strftime("%Y-%m-%dT%H:%M:%S%z")) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as live_consumption_response:
        response_body = await self.__async_read_response__(live_consumption_response, url)

        if (response_body is not None and "data" in response_body and "smartMeterTelemetry" in response_body["data"] and response_body["data"]["smartMeterTelemetry"] is not None and len(response_body["data"]["smartMeterTelemetry"]) > 0):
          return list(map(lambda mp: {
            "consumption": float(mp["consumptionDelta"]) / 1000,
            "demand": float(mp["demand"]) if "demand" in mp and mp["demand"] is not None else None,
            "interval_start": parse_datetime(mp["readAt"]),
            "interval_end": parse_datetime(mp["readAt"]) + timedelta(minutes=30)
          }, response_body["data"]["smartMeterTelemetry"]))
        else:
          _LOGGER.debug(f"Failed to retrieve smart meter consumption data - device_id: {device_id}; period_from: {period_from}; period_to: {period_to}")
    
    return None

  async def async_get_electricity_standard_rates(self, product_code, tariff_code, period_from, period_to): 
    """Get the current standard rates"""
    results = []
    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if data is None:
          return None
        else:
          results = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code, self._electricity_price_cap)

    return results

  async def async_get_electricity_day_night_rates(self, product_code, tariff_code, is_smart_meter, period_from, period_to):
    """Get the current day and night rates"""
    results = []
    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/day-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if data is None:
          return None
        else:
          # Normalise the rates to be in 30 minute increments and remove any rates that fall outside of our day period 
          day_rates = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code, self._electricity_price_cap)
          for rate in day_rates:
            if (self.__is_night_rate(rate, is_smart_meter)) == False:
              results.append(rate)

      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/night-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if data is None:
          return None

        # Normalise the rates to be in 30 minute increments and remove any rates that fall outside of our night period 
        night_rates = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code, self._electricity_price_cap)
        for rate in night_rates:
          if (self.__is_night_rate(rate, is_smart_meter)) == True:
            results.append(rate)

    # Because we retrieve our day and night periods separately over a 2 day period, we need to sort our rates 
    results.sort(key=get_valid_from)

    return results

  async def async_get_electricity_rates(self, tariff_code: str, is_smart_meter: bool, period_from: datetime, period_to: datetime):
    """Get the current rates"""

    tariff_parts = get_tariff_parts(tariff_code)
    if tariff_parts is None:
      return None
    
    product_code = tariff_parts.product_code

    if (tariff_parts.rate.startswith("1")):
      return await self.async_get_electricity_standard_rates(product_code, tariff_code, period_from, period_to)
    else:
      return await self.async_get_electricity_day_night_rates(product_code, tariff_code, is_smart_meter, period_from, period_to)

  async def async_get_electricity_consumption(self, mpan, serial_number, period_from, period_to):
    """Get the current electricity consumption"""
    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/electricity-meter-points/{mpan}/meters/{serial_number}/consumption?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        
        data = await self.__async_read_response__(response, url)
        if (data is not None and "results" in data):
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
    if tariff_parts is None:
      return None
    
    product_code = tariff_parts.product_code

    results = []
    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/gas-tariffs/{tariff_code}/standard-unit-rates?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if data is None:
          return None
        else:
          results = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code, self._gas_price_cap)

    return results

  async def async_get_gas_consumption(self, mprn, serial_number, period_from, period_to):
    """Get the current gas rates"""
    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/gas-meter-points/{mprn}/meters/{serial_number}/consumption?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if (data is not None and "results" in data):
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

  async def async_get_product(self, product_code):
    """Get all products"""
    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}'
      async with client.get(url, auth=auth) as response:
        return await self.__async_read_response__(response, url)

  async def async_get_electricity_standing_charge(self, tariff_code, period_from, period_to):
    """Get the electricity standing charges"""
    tariff_parts = get_tariff_parts(tariff_code)
    if tariff_parts is None:
      return None
    
    product_code = tariff_parts.product_code
    
    result = None
    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standing-charges?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if (data is not None and "results" in data and len(data["results"]) > 0):
          result = {
            "valid_from": parse_datetime(data["results"][0]["valid_from"]) if "valid_from" in data["results"][0] and data["results"][0]["valid_from"] is not None else None,
            "valid_to": parse_datetime(data["results"][0]["valid_to"]) if "valid_to" in data["results"][0] and data["results"][0]["valid_to"] is not None else None,
            "value_inc_vat": float(data["results"][0]["value_inc_vat"])
          }

    return result

  async def async_get_gas_standing_charge(self, tariff_code, period_from, period_to):
    """Get the gas standing charges"""
    tariff_parts = get_tariff_parts(tariff_code)
    if tariff_parts is None:
      return None
    
    product_code = tariff_parts.product_code

    result = None
    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/gas-tariffs/{tariff_code}/standing-charges?period_from={period_from.strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if (data is not None and "results" in data and len(data["results"]) > 0):
          result = {
            "valid_from": parse_datetime(data["results"][0]["valid_from"]) if "valid_from" in data["results"][0] and data["results"][0]["valid_from"] is not None else None,
            "valid_to": parse_datetime(data["results"][0]["valid_to"]) if "valid_to" in data["results"][0] and data["results"][0]["valid_to"] is not None else None,
            "value_inc_vat": float(data["results"][0]["value_inc_vat"])
          }

    return result
  
  async def async_get_intelligent_dispatches(self, account_id: str):
    """Get the user's intelligent dispatches"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": intelligent_dispatches_query.format(account_id=account_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_get_intelligent_dispatches: {response_body}')

        if (response_body is not None and "data" in response_body):
          return IntelligentDispatches(
            list(map(lambda ev: IntelligentDispatchItem(
                as_utc(parse_datetime(ev["startDt"])),
                as_utc(parse_datetime(ev["endDt"])),
                float(ev["delta"]) if "delta" in ev and ev["delta"] is not None else None,
                ev["meta"]["source"] if "meta" in ev and "source" in ev["meta"] else None,
                ev["meta"]["location"] if "meta" in ev and "location" in ev["meta"] else None,
              ), response_body["data"]["plannedDispatches"]
              if "plannedDispatches" in response_body["data"] and response_body["data"]["plannedDispatches"] is not None
              else [])
            ),
            list(map(lambda ev: IntelligentDispatchItem(
                as_utc(parse_datetime(ev["startDt"])),
                as_utc(parse_datetime(ev["endDt"])),
                float(ev["delta"]) if "delta" in ev and ev["delta"] is not None else None,
                ev["meta"]["source"] if "meta" in ev and "source" in ev["meta"] else None,
                ev["meta"]["location"] if "meta" in ev and "location" in ev["meta"] else None,
              ), response_body["data"]["completedDispatches"]
              if "completedDispatches" in response_body["data"] and response_body["data"]["completedDispatches"] is not None
              else [])
            )
          )
        else:
          _LOGGER.error("Failed to retrieve intelligent dispatches")
    
    return None
  
  async def async_get_intelligent_settings(self, account_id: str):
    """Get the user's intelligent settings"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_settings_query.format(account_id=account_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_get_intelligent_settings: {response_body}')

        _LOGGER.debug(f'Intelligent Settings: {response_body}')
        if (response_body is not None and "data" in response_body):

          return IntelligentSettings(
            response_body["data"]["registeredKrakenflexDevice"]["suspended"] == False
            if "registeredKrakenflexDevice" in response_body["data"] and "suspended" in response_body["data"]["registeredKrakenflexDevice"]
            else None,
            int(response_body["data"]["vehicleChargingPreferences"]["weekdayTargetSoc"])
            if "vehicleChargingPreferences" in response_body["data"] and "weekdayTargetSoc" in response_body["data"]["vehicleChargingPreferences"]
            else None,
            int(response_body["data"]["vehicleChargingPreferences"]["weekendTargetSoc"])
            if "vehicleChargingPreferences" in response_body["data"] and "weekendTargetSoc" in response_body["data"]["vehicleChargingPreferences"]
            else None,
            self.__ready_time_to_time__(response_body["data"]["vehicleChargingPreferences"]["weekdayTargetTime"])
            if "vehicleChargingPreferences" in response_body["data"] and "weekdayTargetTime" in response_body["data"]["vehicleChargingPreferences"]
            else None,
            self.__ready_time_to_time__(response_body["data"]["vehicleChargingPreferences"]["weekendTargetTime"])
            if "vehicleChargingPreferences" in response_body["data"] and "weekendTargetTime" in response_body["data"]["vehicleChargingPreferences"]
            else None
          )
        else:
          _LOGGER.error("Failed to retrieve intelligent settings")
    
    return None
  
  def __ready_time_to_time__(self, time_str: str) -> time:
    if time_str is not None:
      parts = time_str.split(':')
      if len(parts) != 2:
        raise Exception(f"Unexpected number of parts in '{time_str}'")
      
      return time(int(parts[0]), int(parts[1]))

    return None
  
  async def async_update_intelligent_car_target_percentage(
      self, 
      account_id: str,
      target_percentage: int
    ):
    """Update a user's intelligent car target percentage"""
    await self.async_refresh_token()

    settings = await self.async_get_intelligent_settings(account_id)

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_settings_mutation.format(
        account_id=account_id,
        weekday_target_percentage=target_percentage,
        weekend_target_percentage=target_percentage,
        weekday_target_time=settings.ready_time_weekday.strftime("%H:%M"),
        weekend_target_time=settings.ready_time_weekend.strftime("%H:%M")
      ) }

      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_update_intelligent_car_target_percentage: {response_body}')

  async def async_update_intelligent_car_target_time(
      self, account_id: str,
      target_time: time,
    ):
    """Update a user's intelligent car target time"""
    await self.async_refresh_token()
    
    settings = await self.async_get_intelligent_settings(account_id)

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_settings_mutation.format(
        account_id=account_id,
        weekday_target_percentage=settings.charge_limit_weekday,
        weekend_target_percentage=settings.charge_limit_weekend,
        weekday_target_time=target_time.strftime("%H:%M"),
        weekend_target_time=target_time.strftime("%H:%M")
      ) }

      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_update_intelligent_car_target_time: {response_body}')

  async def async_turn_on_intelligent_bump_charge(
      self, account_id: str,
    ):
    """Turn on an intelligent bump charge"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_turn_on_bump_charge_mutation.format(
        account_id=account_id,
      ) }

      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_turn_on_intelligent_bump_charge: {response_body}')

  async def async_turn_off_intelligent_bump_charge(
      self, account_id: str,
    ):
    """Turn off an intelligent bump charge"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_turn_off_bump_charge_mutation.format(
        account_id=account_id,
      ) }

      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_turn_off_intelligent_bump_charge: {response_body}')

  async def async_turn_on_intelligent_smart_charge(
      self, account_id: str,
    ):
    """Turn on an intelligent bump charge"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_turn_on_smart_charge_mutation.format(
        account_id=account_id,
      ) }

      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_turn_on_intelligent_smart_charge: {response_body}')

  async def async_turn_off_intelligent_smart_charge(
      self, account_id: str,
    ):
    """Turn off an intelligent bump charge"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_turn_off_smart_charge_mutation.format(
        account_id=account_id,
      ) }

      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_turn_off_intelligent_smart_charge: {response_body}')
  
  async def async_get_intelligent_device(self, account_id: str):
    """Get the user's intelligent dispatches"""
    await self.async_refresh_token()

    async with aiohttp.ClientSession(timeout=self.timeout) as client:
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_device_query.format(account_id=account_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_get_intelligent_device: {response_body}')

        if (response_body is not None and "data" in response_body and
            "registeredKrakenflexDevice" in response_body["data"]):
          device = response_body["data"]["registeredKrakenflexDevice"]
          return {
            "krakenflexDeviceId": device["krakenflexDeviceId"],
            "vehicleMake": device["vehicleMake"],
            "vehicleModel": device["vehicleModel"],
            "vehicleBatterySizeInKwh": float(device["vehicleBatterySizeInKwh"]) if "vehicleBatterySizeInKwh" in device and device["vehicleBatterySizeInKwh"] is not None else None,
            "chargePointMake": device["chargePointMake"],
            "chargePointModel": device["chargePointModel"],
            "chargePointPowerInKw": float(device["chargePointPowerInKw"]) if "chargePointPowerInKw" in device and device["chargePointPowerInKw"] is not None else None,
            
          }
        else:
          _LOGGER.error("Failed to retrieve intelligent device")
    
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

  async def __async_read_response__(self, response, url):
    """Reads the response, logging any json errors"""

    text = await response.text()

    if response.status >= 400:
      if response.status >= 500:
        msg = f'DO NOT REPORT - Octopus Energy server error ({url}): {response.status}; {text}'
        _LOGGER.debug(msg)
        raise ServerError(msg)
      elif response.status not in [401, 403, 404]:
        msg = f'Failed to send request ({url}): {response.status}; {text}'
        _LOGGER.debug(msg)
        raise RequestError(msg)
      return None

    data_as_json = None
    try:
      data_as_json = json.loads(text)
    except:
      raise Exception(f'Failed to extract response json: {url}; {text}')
    
    if ("graphql" in url and "errors" in data_as_json):
      msg = f'Errors in request ({url}): {data_as_json["errors"]}'
      _LOGGER.debug(msg)
      raise RequestError(msg)
    
    return data_as_json
