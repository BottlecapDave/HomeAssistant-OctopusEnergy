import logging
import json
import aiohttp
from asyncio import TimeoutError
from datetime import (datetime, timedelta, time, timezone)
from threading import RLock

from homeassistant.util.dt import (as_utc, now, as_local, parse_datetime, parse_date)

from ..const import INTEGRATION_VERSION

from ..utils import (
  is_day_night_tariff,
)

from .intelligent_device import IntelligentDevice
from .octoplus import RedeemOctoplusPointsResponse
from .intelligent_settings import IntelligentSettings
from .intelligent_dispatches import IntelligentDispatchItem, IntelligentDispatches
from .saving_sessions import JoinSavingSessionResponse, SavingSession, SavingSessionsResponse
from .wheel_of_fortune import WheelOfFortuneSpinsResponse
from .greenness_forecast import GreennessForecast
from .free_electricity_sessions import FreeElectricitySession, FreeElectricitySessionsResponse
from .heat_pump import HeatPumpResponse

_LOGGER = logging.getLogger(__name__)

api_token_query = '''mutation {{
	obtainKrakenToken(input: {{ APIKey: "{api_key}" }}) {{
		token
	}}
}}'''

account_query = '''query {{
  octoplusAccountInfo(accountNumber: "{account_id}") {{
    isOctoplusEnrolled
  }}
  octoHeatPumpControllerEuids(accountNumber: "{account_id}")
  account(accountNumber: "{account_id}") {{
    electricityAgreements(active: true) {{
			meterPoint {{
				mpan
				meters(includeInactive: false) {{
          activeFrom
          activeTo
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
				agreements(includeInactive: true) {{
					validFrom
					validTo
          tariff {{
            ... on TariffType {{
              productCode
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
          activeFrom
          activeTo
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
				agreements(includeInactive: true) {{
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

live_consumption_query = '''query {{
	smartMeterTelemetry(
    deviceId: "{device_id}"
    grouping: HALF_HOURLY 
		start: "{period_from}"
		end: "{period_to}"
	) {{
    readAt
    consumption
		consumptionDelta
    demand
	}}
}}'''

intelligent_dispatches_query = '''query {{
  devices(accountNumber: "{account_id}", deviceId: "{device_id}") {{
		id
    status {{
      currentState
    }}
  }}
	plannedDispatches(accountNumber: "{account_id}") {{
		start
		end
    delta
    meta {{
			source
      location
		}}
	}}
	completedDispatches(accountNumber: "{account_id}") {{
		start
		end
    delta
    meta {{
			source
      location
		}}
	}}
}}'''

intelligent_device_query = '''query {{
  electricVehicles {{
		make
		models {{
			model
			batterySize
		}}
	}}
	chargePointVariants {{
		make
		models {{
			model
			powerInKw
		}}
	}}
  devices(accountNumber: "{account_id}") {{
		id
		provider
		deviceType
    status {{
      current
    }}
		__typename
		... on SmartFlexVehicle {{
			make
			model
		}}
		... on SmartFlexChargePoint {{
			make
			model
		}}
	}}
}}'''

intelligent_settings_query = '''query {{
  devices(accountNumber: "{account_id}", deviceId: "{device_id}") {{
		id
    status {{
      isSuspended
    }}
		... on SmartFlexVehicle {{
			chargingPreferences {{
				weekdayTargetTime
				weekdayTargetSoc
				weekendTargetTime
				weekendTargetSoc
				minimumSoc
				maximumSoc
			}}
		}}
		... on SmartFlexChargePoint {{
			chargingPreferences {{
				weekdayTargetTime
				weekdayTargetSoc
				weekendTargetTime
				weekendTargetSoc
				minimumSoc
				maximumSoc
			}}
		}}
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

octoplus_points_query = '''query octoplus_points {
	loyaltyPointLedgers {
		balanceCarriedForward
  }
}'''

octoplus_saving_session_join_mutation = '''mutation {{
	joinSavingSessionsEvent(input: {{
		accountNumber: "{account_id}"
		eventCode: "{event_code}"
	}}) {{
		possibleErrors {{
			message
		}}
	}}
}}
'''

octoplus_saving_session_query = '''query {{
	savingSessions {{
    events(getDevEvents: false) {{
			id
      code
			rewardPerKwhInOctoPoints
			startAt
			endAt
      devEvent
		}}
		account(accountNumber: "{account_id}") {{
			hasJoinedCampaign
			joinedEvents {{
				eventId
				startAt
				endAt
        rewardGivenInOctoPoints
			}}
		}}
	}}
}}'''

wheel_of_fortune_query = '''query {{
  wheelOfFortuneSpins(accountNumber: "{account_id}") {{
    electricity {{
      remainingSpinsThisMonth
    }}
    gas {{
      remainingSpinsThisMonth
    }}
  }}
}}'''

wheel_of_fortune_mutation = '''mutation {{
  spinWheelOfFortune(input: {{ accountNumber: "{account_id}", supplyType: {supply_type}, termsAccepted: true }}) {{
    spinResult {{
      prizeAmount
    }}
  }}
}}'''

greenness_forecast_query = '''query {
  greennessForecast {
    validFrom
    validTo
    greennessScore
    greennessIndex
    highlightFlag
  }
}'''

redeem_octoplus_points_account_credit_mutation = '''mutation {{
  redeemLoyaltyPointsForAccountCredit(input: {{
    accountNumber: "{account_id}",
    points: {points}
  }}) {{
    pointsRedeemed
  }}
}}
'''

heat_pump_set_zone_mode_without_setpoint_mutation = '''
mutation {{
  octoHeatPumpSetZoneMode(accountNumber: "{account_id}", euid: "{euid}", operationParameters: {{
    zone: {zone_id},
    mode: {zone_mode}
  }}) {{
    transactionId
  }}
}}
'''

heat_pump_set_zone_mode_with_setpoint_mutation = '''
mutation {{
  octoHeatPumpSetZoneMode(accountNumber: "{account_id}", euid: "{euid}", operationParameters: {{
    zone: {zone_id},
    mode: {zone_mode},
    setpointInCelsius: "{target_temperature}"
  }}) {{
    transactionId
  }}
}}
'''

heat_pump_boost_zone_mutation = '''
mutation {{
  octoHeatPumpSetZoneMode(accountNumber: "{account_id}", euid: "{euid}", operationParameters: {{
    zone: {zone_id},
    mode: BOOST,
    setpointInCelsius: "{target_temperature}",
    endAt: "{end_at}"
  }}) {{
    transactionId
  }}
}}
'''

heat_pump_update_flow_temp_config_mutation = '''
mutation {{
  octoHeatPumpUpdateFlowTemperatureConfiguration(
    euid: "{euid}"
    flowTemperatureInput: {{
      useWeatherCompensation: {weather_comp_enabled}, 
      flowTemperature: {{
        value: "{fixed_flow_temperature}", 
        unit: DEGREES_CELSIUS
      }}, 
      weatherCompensationValues: {{
        minimum: {{
          value: "{weather_comp_min_temperature}", 
          unit: DEGREES_CELSIUS
        }}, 
        maximum: {{
          value: "{weather_comp_max_temperature}", 
          unit: DEGREES_CELSIUS
        }}
      }}
    }}
  ) {{
    transactionId
  }}
}}
'''

heat_pump_status_and_config_query = '''
query {{
  octoHeatPumpControllerStatus(accountNumber: "{account_id}", euid: "{euid}") {{
    sensors {{
      code
      connectivity {{
        online
        retrievedAt
      }}
      telemetry {{
        temperatureInCelsius
        humidityPercentage
        retrievedAt
      }}
    }}
    zones {{
      zone 
      telemetry {{
        setpointInCelsius
        mode
        relaySwitchedOn
        heatDemand
        retrievedAt
      }}
    }}
  }}
  octoHeatPumpControllerConfiguration(accountNumber: "{account_id}", euid: "{euid}") {{
    controller {{
      state
      heatPumpTimezone
      connected
    }}
    heatPump {{
      serialNumber
      model
      hardwareVersion
      faultCodes
      maxWaterSetpoint
      minWaterSetpoint
      heatingFlowTemperature {{
        currentTemperature {{
          value
          unit
        }}
        allowableRange {{
          minimum {{
            value
            unit
          }}
          maximum {{
            value
            unit
          }}
        }}
      }}
      weatherCompensation {{
        enabled
        allowableRange {{
            minimum {{
            value
            unit
          }}
          maximum {{
            value
            unit
          }}
        }}
        currentRange {{
          minimum {{
            value
            unit
          }}
          maximum {{
            value
            unit
          }}
        }}
      }}
    }}
    zones {{
      configuration {{
        code
        zoneType
        enabled
        displayName
        primarySensor
        currentOperation {{
          mode
          setpointInCelsius
          action
          end
        }}
        callForHeat
        heatDemand
        emergency
        sensors {{
          ... on ADCSensorConfiguration {{
            code
            displayName
            type
            enabled
          }}
          ... on ZigbeeSensorConfiguration {{
            code
            displayName
            type
            firmwareVersion
            boostEnabled
          }}
        }}
      }}
    }}
  }}
  octoHeatPumpLivePerformance(euid: "{euid}") {{
    coefficientOfPerformance
    outdoorTemperature {{
      value
      unit
    }}
    heatOutput {{
      value
      unit
    }}
    powerInput {{
      value
      unit
    }}
    readAt
  }}
  octoHeatPumpLifetimePerformance(euid: "{euid}") {{
    seasonalCoefficientOfPerformance
    heatOutput {{
      value
      unit
    }}
    energyInput {{
      value
      unit
    }}
    readAt
  }}
}}
'''


user_agent_value = "bottlecapdave-ha-octopus-energy"

def get_valid_from(rate):
  return rate["valid_from"]

def get_start(rate):
  return (rate["start"].timestamp(), rate["start"].fold)
    
def rates_to_thirty_minute_increments(data, period_from: datetime, period_to: datetime, tariff_code: str, price_cap: float = None, favour_direct_debit_rates = True):
  """Process the collection of rates to ensure they're in 30 minute periods"""
  starting_period_from = period_from
  results = []
  if ("results" in data):
    items = data["results"]
    items.sort(key=get_valid_from)

    # We need to normalise our data into 30 minute increments so that all of our rates across all tariffs are the same and it's 
    # easier to calculate our target rate sensors
    for item in items:

      if ("payment_method" in item and
          item["payment_method"] is not None and
          (
            (item["payment_method"].lower() == "direct_debit" and favour_direct_debit_rates != True) or
            (item["payment_method"].lower() != "direct_debit" and favour_direct_debit_rates != False)
          )):
        continue

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
          "start": valid_from,
          "end": valid_to,
          "tariff_code": tariff_code,
          "is_capped": is_capped
        })

        valid_from = valid_to
        starting_period_from = valid_to
    
  return results

class ApiException(Exception): ...

class ServerException(ApiException): ...

class TimeoutException(ApiException): ...

class RequestException(ApiException):
  errors: list[str]

  def __init__(self, message: str, errors: list[str]):
    super().__init__(message)
    self.errors = errors

class AuthenticationException(RequestException): ...

class OctopusEnergyApiClient:
  _refresh_token_lock = RLock()
  _session_lock = RLock()

  def __init__(self, api_key, electricity_price_cap = None, gas_price_cap = None, timeout_in_seconds = 20, favour_direct_debit_rates = True):
    if (api_key is None):
      raise Exception('API KEY is not set')

    self._api_key = api_key
    self._base_url = 'https://api.octopus.energy'

    self._graphql_token = None
    self._graphql_expiration = None

    self._product_tracker_cache = dict()

    self._electricity_price_cap = electricity_price_cap
    self._gas_price_cap = gas_price_cap
    self._favour_direct_debit_rates = favour_direct_debit_rates

    self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout_in_seconds, sock_read=timeout_in_seconds)
    self._default_headers = { "user-agent": f'{user_agent_value}/{INTEGRATION_VERSION}' }

    self._session = None

  async def async_close(self):
    with self._session_lock:
      if self._session is not None:
        await self._session.close()

  def _create_client_session(self):
    if self._session is not None:
      return self._session
    
    with self._session_lock:
      if self._session is not None:
        return self._session

      self._session = aiohttp.ClientSession(headers=self._default_headers, skip_auto_headers=['User-Agent'])
      return self._session

  async def async_refresh_token(self):
    """Get the user's refresh token"""
    if (self._graphql_expiration is not None and (self._graphql_expiration - timedelta(minutes=5)) > now()):
      return

    with self._refresh_token_lock:
      # Check that our token wasn't refreshed while waiting for the lock
      if (self._graphql_expiration is not None and (self._graphql_expiration - timedelta(minutes=5)) > now()):
        return

      try:
        client = self._create_client_session()
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
      except TimeoutError:
        _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
        raise TimeoutException()
      
  def map_electricity_meters(self, meter_point):
    meters = list(
      map(lambda m: {
        "active_from": parse_date(m["activeFrom"]) if m["activeFrom"] is not None else None,
        "active_to": parse_date(m["activeTo"]) if m["activeTo"] is not None else None,
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
        meter_point["meterPoint"]["meters"]
        if "meterPoint" in meter_point and "meters" in meter_point["meterPoint"] and meter_point["meterPoint"]["meters"] is not None
        else []
      )
    )

    meters.sort(key=lambda meter: meter["active_from"], reverse=True)

    return {
      "mpan": meter_point["meterPoint"]["mpan"],
      "meters": meters,
      "agreements": list(map(lambda a: {
        "start": a["validFrom"],
        "end": a["validTo"],
        "tariff_code": a["tariff"]["tariffCode"] if "tariff" in a and "tariffCode" in a["tariff"] else None,
        "product_code": a["tariff"]["productCode"] if "tariff" in a and "productCode" in a["tariff"] else None,
      }, 
      meter_point["meterPoint"]["agreements"]
      if "meterPoint" in meter_point and "agreements" in meter_point["meterPoint"] and meter_point["meterPoint"]["agreements"] is not None
      else []
    ))
  }

  def map_gas_meters(self, meter_point):
    meters = list(
      map(lambda m: {
        "active_from": parse_date(m["activeFrom"]) if m["activeFrom"] is not None else None,
        "active_to": parse_date(m["activeTo"]) if m["activeTo"] is not None else None,
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
      meter_point["meterPoint"]["meters"]
      if "meterPoint" in meter_point and "meters" in meter_point["meterPoint"] and meter_point["meterPoint"]["meters"] is not None
      else []
      )
    )

    meters.sort(key=lambda meter: meter["active_from"], reverse=True)

    return {
      "mprn": meter_point["meterPoint"]["mprn"],
      "meters": meters,
      "agreements": list(map(lambda a: {
          "start": a["validFrom"],
          "end": a["validTo"],
          "tariff_code": a["tariff"]["tariffCode"] if "tariff" in a and "tariffCode" in a["tariff"] else None,
          "product_code": a["tariff"]["productCode"] if "tariff" in a and "productCode" in a["tariff"] else None,
        },
        meter_point["meterPoint"]["agreements"]
        if "meterPoint" in meter_point and "agreements" in meter_point["meterPoint"] and meter_point["meterPoint"]["agreements"] is not None
        else []
      ))
    }
    
  async def async_get_account(self, account_id):
    """Get the user's account"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
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
            "octoplus_enrolled": account_response_body["data"]["octoplusAccountInfo"]["isOctoplusEnrolled"] == True 
            if "octoplusAccountInfo" in account_response_body["data"] and "isOctoplusEnrolled" in account_response_body["data"]["octoplusAccountInfo"]
            else False,
            "heat_pump_ids": account_response_body["data"]["octoHeatPumpControllerEuids"] if "data" in account_response_body and "octoHeatPumpControllerEuids" in account_response_body["data"] else [],
            "electricity_meter_points": list(map(self.map_electricity_meters, 
              account_response_body["data"]["account"]["electricityAgreements"]
              if "electricityAgreements" in account_response_body["data"]["account"] and account_response_body["data"]["account"]["electricityAgreements"] is not None
              else []
            )),
            "gas_meter_points": list(map(self.map_gas_meters,
              account_response_body["data"]["account"]["gasAgreements"] 
              if "gasAgreements" in account_response_body["data"]["account"] and account_response_body["data"]["account"]["gasAgreements"] is not None
              else []
            )),
          }
        else:
          _LOGGER.error("Failed to retrieve account")
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
    return None
  
  async def async_get_heat_pump_configuration_and_status(self, account_id: str, euid: str):
    """Get a heat pump configuration and status"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": heat_pump_status_and_config_query.format(account_id=account_id, euid=euid) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as heat_pump_response:
        response = await self.__async_read_response__(heat_pump_response, url)

        if (response is not None 
            and "data" in response 
            and "octoHeatPumpControllerConfiguration" in response["data"] 
            and "octoHeatPumpControllerStatus" in response["data"]
            and "octoHeatPumpLivePerformance" in response["data"]
            and "octoHeatPumpLifetimePerformance" in response["data"]):
          return HeatPumpResponse.parse_obj(response["data"])
        
      return None
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
  async def async_set_heat_pump_flow_temp_config(self, euid: str, weather_comp_enabled: bool, weather_comp_min_temperature: float, weather_comp_max_temperature: float, fixed_flow_temperature: float):
    """Sets the flow temperature for a given heat pump zone"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      query = heat_pump_update_flow_temp_config_mutation.format(euid=euid, weather_comp_enabled=str(weather_comp_enabled).lower(), weather_comp_min_temperature=weather_comp_min_temperature, weather_comp_max_temperature=weather_comp_max_temperature, fixed_flow_temperature=fixed_flow_temperature) 
      payload = { "query": query }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as heat_pump_response:
        await self.__async_read_response__(heat_pump_response, url)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_set_heat_pump_zone_mode(self, account_id: str, euid: str, zone_id: str, zone_mode: str, target_temperature: float | None):
    """Sets the mode for a given heat pump zone"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      query = (heat_pump_set_zone_mode_with_setpoint_mutation.format(account_id=account_id, euid=euid, zone_id=zone_id, zone_mode=zone_mode, target_temperature=target_temperature) 
               if target_temperature is not None 
               else heat_pump_set_zone_mode_without_setpoint_mutation.format(account_id=account_id, euid=euid, zone_id=zone_id, zone_mode=zone_mode))
      payload = { "query": query }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as heat_pump_response:
        await self.__async_read_response__(heat_pump_response, url)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
  async def async_boost_heat_pump_zone(self, account_id: str, euid: str, zone_id: str, end_datetime: datetime, target_temperature: float):
    """Boost a given heat pump zone"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      query = heat_pump_boost_zone_mutation.format(account_id=account_id, euid=euid, zone_id=zone_id, end_at=end_datetime.isoformat(sep="T"), target_temperature=target_temperature) 
      payload = { "query": query }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as heat_pump_response:
        await self.__async_read_response__(heat_pump_response, url)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
  
  async def async_get_greenness_forecast(self) -> list[GreennessForecast]:
    """Get the latest greenness forecast"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": greenness_forecast_query }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as greenness_forecast_response:

        response_body = await self.__async_read_response__(greenness_forecast_response, url)
        if (response_body is not None and "data" in response_body and "greennessForecast" in response_body["data"]):
          forecast = list(map(lambda item: GreennessForecast(as_utc(parse_datetime(item["validFrom"])),
                                                             as_utc(parse_datetime(item["validTo"])),
                                                             int(item["greennessScore"]),
                                                             item["greennessIndex"],
                                                             item["highlightFlag"]),
                          response_body["data"]["greennessForecast"]))
          forecast.sort(key=lambda item: (item.start.timestamp(), item.start.fold))
          return forecast
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_saving_sessions(self, account_id: str) -> SavingSessionsResponse:
    """Get the user's seasons savings"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": octoplus_saving_session_query.format(account_id=account_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as account_response:
        response_body = await self.__async_read_response__(account_response, url)

        if (response_body is not None and "data" in response_body):
          return SavingSessionsResponse(list(map(lambda ev: SavingSession(ev["id"],
                                                                          ev["code"],
                                                                          as_utc(parse_datetime(ev["startAt"])),
                                                                          as_utc(parse_datetime(ev["endAt"])),
                                                                          ev["rewardPerKwhInOctoPoints"]),
                                        response_body["data"]["savingSessions"]["events"])), 
                                        list(map(lambda ev: SavingSession(ev["eventId"],
                                                                          None,
                                                                          as_utc(parse_datetime(ev["startAt"])),
                                                                          as_utc(parse_datetime(ev["endAt"])),
                                                                          ev["rewardGivenInOctoPoints"]),
                                        response_body["data"]["savingSessions"]["account"]["joinedEvents"])))
        else:
          _LOGGER.error("Failed to retrieve saving sessions")
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

    return None

  async def async_get_free_electricity_sessions(self, account_id: str) -> FreeElectricitySessionsResponse:
    """Get the user's free electricity sessions"""

    try:
      client = self._create_client_session()
      url = f'https://oe-api.davidskendall.co.uk/free_electricity.json'
      payload = { }
      headers = { }
      async with client.get(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)

        if (response_body is not None and "data" in response_body):
          sessions = []
          for item in response_body["data"]:
            if "is_test" in item and item["is_test"] == True:
              continue

            sessions.append(FreeElectricitySession(
              item["code"],
              as_utc(parse_datetime(item["start"])),
              as_utc(parse_datetime(item["end"]))))

          return FreeElectricitySessionsResponse(sessions)
        else:
          _LOGGER.error("Failed to retrieve free electricity sessions")
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

    return None

  async def async_get_octoplus_points(self):
    """Get the user's octoplus points"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": octoplus_points_query }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as account_response:
        response_body = await self.__async_read_response__(account_response, url)

        if (response_body is not None and "data" in response_body and "loyaltyPointLedgers" in response_body["data"] and len(response_body["data"]["loyaltyPointLedgers"]) > 0):
          return int(response_body["data"]["loyaltyPointLedgers"][0]["balanceCarriedForward"])
        else:
          _LOGGER.error("Failed to retrieve octopoints")
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

    return None
  
  async def async_join_octoplus_saving_session(self, account_id: str, event_code: str) -> JoinSavingSessionResponse:
    """Join a saving session"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": octoplus_saving_session_join_mutation.format(account_id=account_id, event_code=event_code) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as join_response:

        try:
          await self.__async_read_response__(join_response, url)
          return JoinSavingSessionResponse(True, [])
        except RequestException as e:
          return JoinSavingSessionResponse(False, e.errors)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
  async def async_redeem_octoplus_points_into_account_credit(self, account_id: str, points_to_redeem: int) -> RedeemOctoplusPointsResponse:
    """Redeem octoplus points"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": redeem_octoplus_points_account_credit_mutation.format(account_id=account_id, points=points_to_redeem) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as redemption_response:
        try:
          await self.__async_read_response__(redemption_response, url)
          return RedeemOctoplusPointsResponse(True, [])
        except RequestException as e:
          return RedeemOctoplusPointsResponse(False, e.errors)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_smart_meter_consumption(self, device_id: str, period_from: datetime, period_to: datetime):
    """Get the user's smart meter consumption"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'

      payload = { "query": live_consumption_query.format(device_id=device_id, period_from=period_from.strftime("%Y-%m-%dT%H:%M:%S%z"), period_to=period_to.strftime("%Y-%m-%dT%H:%M:%S%z")) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as live_consumption_response:
        response_body = await self.__async_read_response__(live_consumption_response, url)

        if (response_body is not None and "data" in response_body and "smartMeterTelemetry" in response_body["data"] and response_body["data"]["smartMeterTelemetry"] is not None and len(response_body["data"]["smartMeterTelemetry"]) > 0):
          return list(map(lambda mp: {
            "total_consumption": float(mp["consumption"]) / 1000 if "consumption" in mp and mp["consumption"] is not None else None,
            "consumption": float(mp["consumptionDelta"]) / 1000 if "consumptionDelta" in mp and mp["consumptionDelta"] is not None else 0,
            "demand": float(mp["demand"]) if "demand" in mp and mp["demand"] is not None else None,
            "start": parse_datetime(mp["readAt"]),
            "end": parse_datetime(mp["readAt"]) + timedelta(minutes=30)
          }, response_body["data"]["smartMeterTelemetry"]))
        else:
          _LOGGER.debug(f"Failed to retrieve smart meter consumption data - device_id: {device_id}; period_from: {period_from}; period_to: {period_to}")
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

    return None

  async def async_get_electricity_standard_rates(self, product_code: str, tariff_code: str, period_from: datetime, period_to: datetime): 
    """Get the current standard rates"""
    results = []

    try:
      client = self._create_client_session()
      auth = aiohttp.BasicAuth(self._api_key, '')
      page = 1
      has_more_rates = True
      while has_more_rates:
        url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates?period_from={period_from.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}&page={page}'
        async with client.get(url, auth=auth) as response:
          data = await self.__async_read_response__(response, url)
          if data is None:
            return None
          else:
            results = results + rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code, self._electricity_price_cap, self._favour_direct_debit_rates)
            has_more_rates = "next" in data and data["next"] is not None
            if has_more_rates:
              page = page + 1
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
    results.sort(key=get_start)
    return results

  async def async_get_electricity_day_night_rates(self, product_code: str, tariff_code: str, is_smart_meter: bool, period_from: datetime, period_to: datetime):
    """Get the current day and night rates"""
    results = []

    try:
      client = self._create_client_session()
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/day-unit-rates?period_from={period_from.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if data is None:
          return None
        else:
          # Normalise the rates to be in 30 minute increments and remove any rates that fall outside of our day period 
          day_rates = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code, self._electricity_price_cap, self._favour_direct_debit_rates)
          for rate in day_rates:
            if self.__is_night_rate(rate, is_smart_meter) == False:
              results.append(rate)

      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/night-unit-rates?period_from={period_from.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if data is None:
          return None

        # Normalise the rates to be in 30 minute increments and remove any rates that fall outside of our night period 
        night_rates = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code, self._electricity_price_cap, self._favour_direct_debit_rates)
        for rate in night_rates:
          if self.__is_night_rate(rate, is_smart_meter) == True:
            results.append(rate)
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

    # Because we retrieve our day and night periods separately over a 2 day period, we need to sort our rates 
    results.sort(key=get_start)

    return results

  async def async_get_electricity_rates(self, product_code: str, tariff_code: str, is_smart_meter: bool, period_from: datetime, period_to: datetime):
    """Get the current rates"""

    if is_day_night_tariff(tariff_code):
      return await self.async_get_electricity_day_night_rates(product_code, tariff_code, is_smart_meter, period_from, period_to)
    else:
      return await self.async_get_electricity_standard_rates(product_code, tariff_code, period_from, period_to)
      
  async def async_get_electricity_consumption(self, mpan: str, serial_number: str, period_from: datetime | None = None, period_to: datetime | None = None, page_size: int | None = None):
    """Get the current electricity consumption"""

    try:
      client = self._create_client_session()
      auth = aiohttp.BasicAuth(self._api_key, '')

      query_params = []
      if period_from is not None:
        query_params.append(f'period_from={period_from.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}')
      
      if period_to is not None:
        query_params.append(f'period_to={period_to.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}')

      if page_size is not None:
        query_params.append(f'page_size={page_size}')

      query_string = '&'.join(query_params)
      
      url = f"{self._base_url}/v1/electricity-meter-points/{mpan}/meters/{serial_number}/consumption{f'?{query_string}' if len(query_string) > 0 else ''}"
      async with client.get(url, auth=auth) as response:
        
        data = await self.__async_read_response__(response, url)
        if (data is not None and "results" in data):
          data = data["results"]
          results = []
          for item in data:
            item = self.__process_consumption(item)

            # For some reason, the end point returns slightly more data than we requested, so we need to filter out
            # the results
            if (period_from is None or as_utc(item["start"]) >= period_from) and (period_to is None or as_utc(item["end"]) <= period_to):
              results.append(item)
          
          results.sort(key=self.__get_interval_end)
          return results
        
        return None
        
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_gas_rates(self, product_code: str, tariff_code: str, period_from: datetime, period_to: datetime):
    """Get the gas rates"""
    results = []

    try:
      client = self._create_client_session()
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/gas-tariffs/{tariff_code}/standard-unit-rates?period_from={period_from.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if data is None:
          return None
        else:
          results = rates_to_thirty_minute_increments(data, period_from, period_to, tariff_code, self._gas_price_cap, self._favour_direct_debit_rates)

      return results
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_gas_consumption(self, mprn: str, serial_number: str, period_from: datetime | None = None, period_to: datetime | None = None, page_size: int | None = None):
    """Get the current gas rates"""
    
    try:
      client = self._create_client_session()
      auth = aiohttp.BasicAuth(self._api_key, '')

      query_params = []
      if period_from is not None:
        query_params.append(f'period_from={period_from.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}')
      
      if period_to is not None:
        query_params.append(f'period_to={period_to.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}')

      if page_size is not None:
        query_params.append(f'page_size={page_size}')

      query_string = '&'.join(query_params)

      url = f"{self._base_url}/v1/gas-meter-points/{mprn}/meters/{serial_number}/consumption{f'?{query_string}' if len(query_string) > 0 else ''}"
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if (data is not None and "results" in data):
          data = data["results"]
          results = []
          for item in data:
            item = self.__process_consumption(item)
            results.append(item)

          results.sort(key=self.__get_interval_end)
          return results
        
        return None
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_product(self, product_code):
    """Get all products"""

    try:
      client = self._create_client_session()
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}'
      async with client.get(url, auth=auth) as response:
        return await self.__async_read_response__(response, url)
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_electricity_standing_charge(self, product_code: str, tariff_code: str, period_from: datetime, period_to: datetime):
    """Get the electricity standing charges"""
    result = None

    try:
      client = self._create_client_session()
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standing-charges?period_from={period_from.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if (data is not None and "results" in data and len(data["results"]) > 0):
          result = {
            "start": parse_datetime(data["results"][0]["valid_from"]) if "valid_from" in data["results"][0] and data["results"][0]["valid_from"] is not None else None,
            "end": parse_datetime(data["results"][0]["valid_to"]) if "valid_to" in data["results"][0] and data["results"][0]["valid_to"] is not None else None,
            "value_inc_vat": float(data["results"][0]["value_inc_vat"]),
            "tariff_code": tariff_code,
          }

      return result
    except TimeoutError:
        _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
        raise TimeoutException()

  async def async_get_gas_standing_charge(self, product_code: str, tariff_code: str, period_from: datetime, period_to: datetime):
    """Get the gas standing charges"""
    result = None

    try:
      client = self._create_client_session()
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/v1/products/{product_code}/gas-tariffs/{tariff_code}/standing-charges?period_from={period_from.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}'
      async with client.get(url, auth=auth) as response:
        data = await self.__async_read_response__(response, url)
        if (data is not None and "results" in data and len(data["results"]) > 0):
          result = {
            "start": parse_datetime(data["results"][0]["valid_from"]) if "valid_from" in data["results"][0] and data["results"][0]["valid_from"] is not None else None,
            "end": parse_datetime(data["results"][0]["valid_to"]) if "valid_to" in data["results"][0] and data["results"][0]["valid_to"] is not None else None,
            "value_inc_vat": float(data["results"][0]["value_inc_vat"]),
            "tariff_code": tariff_code,
          }

      return result
    except TimeoutError:
        _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
        raise TimeoutException()
  
  async def async_get_intelligent_dispatches(self, account_id: str, device_id: str):
    """Get the user's intelligent dispatches"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": intelligent_dispatches_query.format(account_id=account_id, device_id=device_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_get_intelligent_dispatches: {response_body}')

        current_state = None
        if (response_body is not None and "data" in response_body and "devices" in response_body["data"]):
          for device in response_body["data"]["devices"]:
            if device["id"] == device_id:
              current_state = device["status"]["currentState"]

        if (response_body is not None and "data" in response_body):
          return IntelligentDispatches(
            current_state,
            list(map(lambda ev: IntelligentDispatchItem(
                as_utc(parse_datetime(ev["start"])),
                as_utc(parse_datetime(ev["end"])),
                float(ev["delta"]) if "delta" in ev and ev["delta"] is not None else None,
                ev["meta"]["source"] if "meta" in ev and "source" in ev["meta"] else None,
                ev["meta"]["location"] if "meta" in ev and "location" in ev["meta"] else None,
              ), response_body["data"]["plannedDispatches"]
              if "plannedDispatches" in response_body["data"] and response_body["data"]["plannedDispatches"] is not None
              else [])
            ),
            list(map(lambda ev: IntelligentDispatchItem(
                as_utc(parse_datetime(ev["start"])),
                as_utc(parse_datetime(ev["end"])),
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
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
  
  async def async_get_intelligent_settings(self, account_id: str, device_id: str):
    """Get the user's intelligent settings"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_settings_query.format(account_id=account_id, device_id=device_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_get_intelligent_settings: {response_body}')

        _LOGGER.debug(f'Intelligent Settings: {response_body}')
        if (response_body is not None and "data" in response_body and "devices" in response_body["data"]):

          devices = list(response_body["data"]["devices"])
          if len(devices) == 1:
            smart_charge = devices[0]["status"]["isSuspended"] == False if "status" in devices[0] and "isSuspended" in devices[0]["status"] else None
            charging_preferences = devices[0]["chargingPreferences"] if "chargingPreferences" in devices[0] else None
            return IntelligentSettings(
              smart_charge,
              int(charging_preferences["weekdayTargetSoc"])
              if charging_preferences is not None and "weekdayTargetSoc" in charging_preferences
              else None,
              int(charging_preferences["weekendTargetSoc"])
              if charging_preferences is not None and "weekendTargetSoc" in charging_preferences
              else None,
              self.__ready_time_to_time__(charging_preferences["weekdayTargetTime"])
              if charging_preferences is not None and "weekdayTargetTime" in charging_preferences
              else None,
              self.__ready_time_to_time__(charging_preferences["weekendTargetTime"])
              if charging_preferences is not None and "weekendTargetTime" in charging_preferences
              else None
            )
        else:
          _LOGGER.error("Failed to retrieve intelligent settings")
      
      return None

    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
  
  def __ready_time_to_time__(self, time_str: str) -> time:
    if time_str is not None:
      parts = time_str.split(':')
      if len(parts) != 3:
        raise Exception(f"Unexpected number of parts in '{time_str}'")
      
      return time(int(parts[0]), int(parts[1]), int(parts[2]))

    return None
  
  async def async_update_intelligent_car_target_percentage(
      self, 
      account_id: str,
      device_id: str,
      target_percentage: int
    ):
    """Update a user's intelligent car target percentage"""
    await self.async_refresh_token()

    settings = await self.async_get_intelligent_settings(account_id, device_id)

    try:
      client = self._create_client_session()
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
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_update_intelligent_car_target_time(
      self,
      account_id: str,
      device_id: str,
      target_time: time,
    ):
    """Update a user's intelligent car target time"""
    await self.async_refresh_token()
    
    settings = await self.async_get_intelligent_settings(account_id, device_id)

    try:
      client = self._create_client_session()
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
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_turn_on_intelligent_bump_charge(
      self, account_id: str,
    ):
    """Turn on an intelligent bump charge"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_turn_on_bump_charge_mutation.format(
        account_id=account_id,
      ) }

      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_turn_on_intelligent_bump_charge: {response_body}')
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_turn_off_intelligent_bump_charge(
      self, account_id: str,
    ):
    """Turn off an intelligent bump charge"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_turn_off_bump_charge_mutation.format(
        account_id=account_id,
      ) }

      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_turn_off_intelligent_bump_charge: {response_body}')
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_turn_on_intelligent_smart_charge(
      self, account_id: str,
    ):
    """Turn on an intelligent bump charge"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_turn_on_smart_charge_mutation.format(
        account_id=account_id,
      ) }

      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_turn_on_intelligent_smart_charge: {response_body}')
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_turn_off_intelligent_smart_charge(
      self, account_id: str,
    ):
    """Turn off an intelligent bump charge"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_turn_off_smart_charge_mutation.format(
        account_id=account_id,
      ) }

      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_turn_off_intelligent_smart_charge: {response_body}')
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
  
  async def async_get_intelligent_device(self, account_id: str) -> IntelligentDevice:
    """Get the user's intelligent dispatches"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": intelligent_device_query.format(account_id=account_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_get_intelligent_device: {response_body}')

        result = []
        if (response_body is not None and "data" in response_body and "devices" in response_body["data"]):
          devices: list = response_body["data"]["devices"]

          for device in devices:
            if (device["deviceType"] != "ELECTRIC_VEHICLES" or device["status"]["current"] != "LIVE"):
              continue

            is_charger = device["__typename"] == "SmartFlexChargePoint"

            make = device["make"]
            model = device["model"]
            vehicleBatterySizeInKwh = None
            chargePointPowerInKw = None

            if is_charger:
              if "chargePointVariants" in response_body["data"] and response_body["data"]["chargePointVariants"] is not None:
                for charger in response_body["data"]["chargePointVariants"]:
                  if charger["make"] == make:
                    if "models" in charger and charger["models"] is not None:
                      for charger_model in charger["models"]:
                        if charger_model["model"] == model:
                          chargePointPowerInKw = float(charger_model["powerInKw"]) if "powerInKw" in charger_model and charger_model["powerInKw"] is not None else 0
                          break

                    break
            else:
              if "electricVehicles" in response_body["data"] and response_body["data"]["electricVehicles"] is not None:
                for charger in response_body["data"]["electricVehicles"]:
                  if charger["make"] == make:
                    if "models" in charger and charger["models"] is not None:
                      for charger_model in charger["models"]:
                        if charger_model["model"] == model:
                          vehicleBatterySizeInKwh = float(charger_model["batterySize"]) if "batterySize" in charger_model and charger_model["batterySize"] is not None else 0
                          break

                    break

            result.append(IntelligentDevice(
              device["id"],
              device["provider"],
              make,
              model,
              vehicleBatterySizeInKwh,
              chargePointPowerInKw,
              is_charger
            ))

          if len(result) > 1:
            _LOGGER.warning("Multiple intelligent devices discovered. Picking first one")

          return result[0] if len(result) > 0 else None
        else:
          _LOGGER.error("Failed to retrieve intelligent device")
      
      return None

    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
  
  async def async_get_wheel_of_fortune_spins(self, account_id: str) -> WheelOfFortuneSpinsResponse:
    """Get the user's wheel of fortune spins"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": wheel_of_fortune_query.format(account_id=account_id) }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_get_wheel_of_fortune_spins: {response_body}')

        if (response_body is not None and "data" in response_body and
            "wheelOfFortuneSpins" in response_body["data"]):
          
          spins = response_body["data"]["wheelOfFortuneSpins"]
          return WheelOfFortuneSpinsResponse(
            int(spins["electricity"]["remainingSpinsThisMonth"]) if "electricity" in spins and "remainingSpinsThisMonth" in spins["electricity"] else 0,
            int(spins["gas"]["remainingSpinsThisMonth"]) if "gas" in spins and "remainingSpinsThisMonth" in spins["gas"] else 0
          )
        else:
          _LOGGER.error("Failed to retrieve wheel of fortune spins")
      
      return None

    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
  
  async def async_spin_wheel_of_fortune(self, account_id: str, is_electricity: bool) -> int:
    """Get the user's wheel of fortune spins"""
    await self.async_refresh_token()

    try:
      client = self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": wheel_of_fortune_mutation.format(account_id=account_id, supply_type="ELECTRICITY" if is_electricity == True else "GAS") }
      headers = { "Authorization": f"JWT {self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        _LOGGER.debug(f'async_spin_wheel_of_fortune: {response_body}')

        if (response_body is not None and 
            "data" in response_body and
            "spinWheelOfFortune" in response_body["data"] and
            "spinResult" in response_body["data"]["spinWheelOfFortune"] and
            "prizeAmount" in response_body["data"]["spinWheelOfFortune"]["spinResult"]):
          
          return int(response_body["data"]["spinWheelOfFortune"]["spinResult"]["prizeAmount"])
        else:
          _LOGGER.error("Failed to spin wheel of fortune")
      
      return None
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  def __get_interval_end(self, item):
    return (item["end"].timestamp(), item["end"].fold)

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
    rate_local_valid_from = as_local(rate["start"])
    rate_local_valid_to = as_local(rate["end"])

    if use_utc:
        rate_utc_valid_from = as_utc(rate["start"])
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
      "start": as_utc(parse_datetime(item["interval_start"])),
      "end": as_utc(parse_datetime(item["interval_end"]))
    }

  async def __async_read_response__(self, response, url, ignore_errors = False):
    """Reads the response, logging any json errors"""

    text = await response.text()

    if response.status >= 400:
      if response.status >= 500:
        msg = f'DO NOT REPORT - Octopus Energy server error ({url}): {response.status}; {text}'
        _LOGGER.warning(msg)
        raise ServerException(msg)
      elif response.status in [401, 403]:
        msg = f'Failed to send request ({url}): {response.status}; {text}'
        _LOGGER.warning(msg)
        raise AuthenticationException(msg, [])
      elif response.status not in [404]:
        msg = f'Failed to send request ({url}): {response.status}; {text}'
        _LOGGER.warning(msg)
        raise RequestException(msg, [])
      
      _LOGGER.info(f"Response {response.status} for '{url}' received")
      return None

    data_as_json = None
    try:
      data_as_json = json.loads(text)
    except:
      raise Exception(f'Failed to extract response json: {url}; {text}')
    
    if ("graphql" in url and "errors" in data_as_json and ignore_errors == False):
      msg = f'Errors in request ({url}): {data_as_json["errors"]}'
      errors = list(map(lambda error: error["message"], data_as_json["errors"]))
      _LOGGER.warning(msg)

      for error in data_as_json["errors"]:
        if (error["extensions"]["errorCode"] in ("KT-CT-1139", "KT-CT-1111", "KT-CT-1143")):
          raise AuthenticationException(msg, errors)

      raise RequestException(msg, errors)
    
    return data_as_json
