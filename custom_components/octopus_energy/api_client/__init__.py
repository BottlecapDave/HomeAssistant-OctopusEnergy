import base64
import logging
import json
from typing import Any, List
import aiohttp
import asyncio
from asyncio import TimeoutError
from datetime import (datetime, timedelta, time, timezone)

from homeassistant.util.dt import (as_utc, now, as_local, parse_datetime, parse_date)

from ..const import INTEGRATION_VERSION, INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS

from ..utils import (
  is_day_night_tariff,
)

from .intelligent_device import IntelligentDevice
from .octoplus import OctoplusScratchcardResponse, RedeemOctoplusPointsResponse
from .intelligent_dispatches import DecimalReading, IntelligentDispatchItem, IntelligentDispatches
from .saving_sessions import JoinSavingSessionResponse, SavingSession, SavingSessionsResponse
from .wheel_of_fortune import WheelOfFortuneSpinsResponse
from .free_electricity_sessions import FreeElectricitySession, FreeElectricitySessionsResponse
from .heat_pump import HeatPumpResponse
from .intelligent_device_settings import IntelligentDeviceSettingPreferenceSchedule, IntelligentDeviceSettings

_LOGGER = logging.getLogger(__name__)

# Octopus rate limit token retrieval per account. A failed attempt does not
# update our token expiry, so without a cooldown every subsequent request
# attempts to retrieve a new token, which keeps the rate limit tripped.
MINIMUM_TOKEN_RETRIEVAL_COOLDOWN_IN_MINUTES = 1
MAXIMUM_TOKEN_RETRIEVAL_COOLDOWN_IN_MINUTES = 30

api_token_query = '''mutation {{
	obtainKrakenToken(input: {{ APIKey: "{api_key}" }}) {{
		token
    refreshToken
    refreshExpiresIn
	}}
}}'''

api_token_refresh_query = '''mutation {{
	obtainKrakenToken(input: {{ refreshToken: "{refresh_token}" }}) {{
		token
    refreshToken
    refreshExpiresIn
	}}
}}'''

account_query = '''query {{
  octoplusAccountInfo(accountNumber: "{account_id}") {{
    enrollmentStatus
  }}
  properties(accountNumber: "{account_id}") {{
      id
      occupancyPeriods {{
              effectiveTo
            }}
    }}
  account(accountNumber: "{account_id}") {{
    
    electricityAgreements(active: true) {{
			meterPoint {{
				mpan
				direction
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
    export
	}}
}}'''

intelligent_dispatches_query = '''query {{
  devices(accountNumber: "{account_id}", deviceId: "{device_id}") {{
		id
    status {{
      currentState
      ... on SmartFlexVehicleStatus {{
        stateOfCharge {{
          value
          timestamp
        }}
      }}
      ... on SmartFlexChargePointStatus {{
        stateOfCharge {{
          value
          timestamp
        }}
      }}
    }}
  }}
  flexPlannedDispatches(deviceId:"{device_id}") {{
    start
    end
    type
    energyAddedKwh
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
    preferences {{
      targetType
      unit
      mode
      schedules {{
        dayOfWeek
        time
        min
        max
        upperLimit
      }}
    }}
	}}
}}'''

intelligent_settings_mutation = '''mutation {{
  setDevicePreferences(input: {{
    deviceId: "{device_id}"
    mode: CHARGE
    unit: PERCENTAGE
    schedules: [{schedules}]
  }}) {{
    id
  }}
}}'''

intelligent_settings_mutation_schedule = '''{{
  dayOfWeek: {day_of_week}
  time: "{target_time}"
  max: "{target_percentage}"
}}'''

intelligent_turn_on_bump_charge_mutation = '''mutation {{
	updateBoostCharge(input: {{
    deviceId: "{device_id}"
    action: BOOST
  }}) {{
    id
  }}
}}'''

intelligent_turn_off_bump_charge_mutation = '''mutation {{
	updateBoostCharge(input: {{
    deviceId: "{device_id}"
    action: CANCEL
  }}) {{
    id
  }}
}}'''

intelligent_turn_on_smart_charge_mutation = '''mutation {{
  updateDeviceSmartControl(input: {{
    deviceId: "{device_id}"
    action: UNSUSPEND
  }}) {{
    id
  }}
}}'''

intelligent_turn_off_smart_charge_mutation = '''mutation {{
  updateDeviceSmartControl(input: {{
    deviceId: "{device_id}"
    action: SUSPEND
  }}) {{
    id
  }}
}}'''

intelligent_set_charging_duration_capped_mutation = '''mutation {{
  updateIsChargingDurationCapped(input: {{
    deviceId: "{device_id}"
    enabled: {enabled}
  }}) {{
    id
  }}
}}'''

octoplus_points_query = '''query octoplus_points {
	loyaltyPointLedgers {
		balanceCarriedForward
  }
}'''

octoplus_scratchcard_query = '''query getActiveScratchcardDataV1($accountNumber: String!) {
  octoplusActiveScratchcardData(accountNumber: $accountNumber) {
    activeSession {
      startsAt
      endsAt
      externalReference
    }
    scratchcard {
      externalReference
      status
      offer {
        slug
        featureDisplayText
      }
      prize {
        __typename
      }
    }
  }
}'''

backend_octoplus_saving_session_join_mutation = '''mutation {{
	joinSavingSessionsEvent(input: {{
		accountNumber: "{account_id}"
		eventCode: "{event_code}"
	}}) {{
		joinedEventCodes
	}}
}}
'''

backend_octoplus_saving_session_query = '''query {{
	savingSessions {{
    events(includeDev: false) {{
			id
      code
			rewardPerKwhInOctoPoints
			startAt
			endAt
      devEvent
      targetRegion {{
        regionId
      }}
      eventType
      capacityStatus
		}}
		account(accountNumber: "{account_id}") {{
      signedUpMeterPoint {{
        regionId
      }}
			hasJoinedCampaign
      tokenBalance
			joinedEvents {{
				eventId
				startAt
				endAt
        rewardGivenInOctoPoints
        eventType
			}}
		}}
	}}
}}'''

backend_redeem_weekend_happy_hour_mutation = '''mutation {{
	bookSavingSessionsWeekendHappyHourEvent(input: {{
		accountNumber: "{account_id}"
		eventCode: "{event_code}"
	}}) {{
    bookedEvent {{
		  eventId
    }}
	}}
}}'''

backend_wheel_of_fortune_query = '''query {{
  electricity: wheelOfFortuneSpinsAllowed(fuelType:ELECTRICITY, accountNumber: "{account_id}") {{
    spinsAllowed
  }}
  gas: wheelOfFortuneSpinsAllowed(fuelType:GAS, accountNumber: "{account_id}") {{
    spinsAllowed
  }}
}}'''

backend_wheel_of_fortune_mutation = '''mutation {{
  spinWheelOfFortune(input: {{ accountNumber: "{account_id}", fuelType: {fuel_type} }}) {{
    prize {{
      value
    }}
  }}
}}'''

redeem_octoplus_points_account_credit_mutation = '''mutation {{
  redeemLoyaltyPointsForAccountCredit(input: {{
    accountNumber: "{account_id}",
    points: {points}
  }}) {{
    pointsRedeemed
  }}
}}
'''

backend_heat_pump_set_zone_mode_without_setpoint_mutation = '''
mutation {{
  heatPumpSetZoneMode(accountNumber: "{account_id}", euid: "{euid}", operationParameters: {{
    zone: {zone_id},
    mode: {zone_mode}
  }}) {{
    transactionId
  }}
}}
'''

backend_heat_pump_set_zone_mode_with_setpoint_mutation = '''
mutation {{
  heatPumpSetZoneMode(accountNumber: "{account_id}", euid: "{euid}", operationParameters: {{
    zone: {zone_id},
    mode: {zone_mode},
    setpointInCelsius: {target_temperature}
  }}) {{
    transactionId
  }}
}}
'''

backend_heat_pump_boost_zone_mutation = '''
mutation {{
  heatPumpSetZoneMode(accountNumber: "{account_id}", euid: "{euid}", operationParameters: {{
    zone: {zone_id},
    mode: BOOST,
    setpointInCelsius: {target_temperature},
    endAt: "{end_at}"
  }}) {{
    transactionId
  }}
}}
'''

backend_heat_pump_update_flow_temp_config_mutation = '''
mutation {{
  heatPumpUpdateFlowTemperatureConfiguration(
    accountNumber: "{account_id}"
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
    transactionIds {{
      transactionId
    }}
  }}
}}
'''

backend_heat_pump_status_and_config_query = '''
query {{
  heatPumpControllerStatus(accountNumber: "{account_id}", euid: "{euid}") {{
    sensors {{
      code
      connectivity {{
        online
        retrievedAt
      }}
      telemetry {{
        temperatureInCelsius
        humidityPercentage
        voltage
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
  heatPumpLivePerformance(accountNumber: "{account_id}", euid: "{euid}") {{
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
  heatPumpControllerConfiguration(accountNumber: "{account_id}", euid: "{euid}") {{
    controller {{
      state
      heatPumpTimezone
      connected
    }}
    heatPump {{
      serialNumber
      model
      hardwareVersion
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
  heatPumpLifetimePerformance(accountNumber: "{account_id}", euid: "{euid}") {{
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

backend_heat_pump_ids_query = '''
query {{
  heatPumpControllersAtLocation(accountNumber: "{account_id}", propertyId: "{property_id}") {{
    controller {{
      euid
    }}
  }}
}}
'''

backend_heat_pump_set_hush_mode_mutation = '''
mutation {{
  heatPumpSetHushMode(accountNumber: "{account_id}" euid: "{euid}" hushModeEnabled: {is_enabled}) {{
    transactionId
  }}
}}
'''

power_down_event_types = ["TURN_DOWN"]
power_up_event_types = ["TURN_UP", "WEEKEND_HAPPY_HOUR"]

user_agent_value = "bottlecapdave-ha-octopus-energy"

integration_context_header = "Ha-Integration-Context"

# Not a fan of this, but no other way to identify this type of tariff. Hopefully OE don't change their tariff structure
intelligent_tariffs = [
  "IOG-SMB",
]

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

def get_standing_charge(data: list, tariff_code: str, favour_direct_debit_rates: bool):
  for item in data:
    if ("payment_method" in item and
        item["payment_method"] is not None and
        (
          (item["payment_method"].lower() == "direct_debit" and favour_direct_debit_rates != True) or
          (item["payment_method"].lower() != "direct_debit" and favour_direct_debit_rates != False)
        )):
      continue

    return {
      "start": parse_datetime(item["valid_from"]) if "valid_from" in item and item["valid_from"] is not None else None,
      "end": parse_datetime(item["valid_to"]) if "valid_to" in item and item["valid_to"] is not None else None,
      "value_inc_vat": float(item["value_inc_vat"]),
      "tariff_code": tariff_code,
    }
  
  return None

class ApiException(Exception): ...

class ServerException(ApiException): ...

class TimeoutException(ApiException): ...

class RequestException(ApiException):
  errors: list[str]

  def __init__(self, message: str, errors: list[str]):
    super().__init__(message)
    self.errors = errors

class AuthenticationException(RequestException): ...

class IntelligentBoostChargeException(RequestException):
  refusal_reason: str | None

  def __init__(self, message: str, errors: list[str], refusal_reason: str | None):
    super().__init__(message, errors)
    self.refusal_reason = refusal_reason

def process_boost_charge_refusal(reason: str):
  if reason == "BC_DEVICE_NOT_YET_LIVE":
    return "Device is not yet live"
  if reason == "BC_DEVICE_RETIRED":
    return "Device is retired"
  if reason == "BC_DEVICE_SUSPENDED":
    return "Device is suspended"
  if reason == "BC_DEVICE_DISCONNECTED":
    return "Device is disconnected"
  if reason == "BC_DEVICE_NOT_AT_HOME":
    return "Device is not at home"
  if reason == "BC_BOOST_CHARGE_IN_PROGRESS":
    return "Boost charge already in progress"
  if reason == "BC_DEVICE_FULLY_CHARGED":
    return "Device is already fully charged"
  
  return None

def process_graphql_response(data: Any, url: str, request_context: str, ignore_errors: bool, accepted_error_codes: list[str]):
  if ("graphql" in url and "errors" in data and ignore_errors == False):
    msg = f'Errors in request ({url}) ({request_context}): {data["errors"]}'
    errors = list(map(lambda error: error["message"].strip(".,!"), data["errors"]))
    errors_as_string = ', '.join(errors)
    _LOGGER.warning(msg)

    for error in data["errors"]:
      if ("extensions" in error and
          "errorCode" in error["extensions"] and
          error["extensions"]["errorCode"] in ("KT-CT-1139", "KT-CT-1111", "KT-CT-1143", "KT-CT-1134", "KT-CT-1135", "OE-0103")):
        raise AuthenticationException(f"Authentication failed - {errors_as_string}. See logs for more details.", errors)

      if ("extensions" in error and
          "errorCode" in error["extensions"] and
          error["extensions"]["errorCode"] in accepted_error_codes):
        return None

      if ("extensions" in error and
          "boostChargeRefusalReasons" in error["extensions"]):
        refusal_reason = process_boost_charge_refusal(error["extensions"]["boostChargeRefusalReasons"])
        raise IntelligentBoostChargeException(f"Boost failed - {refusal_reason} - {errors_as_string}. See logs for more details.", errors, refusal_reason)

    raise RequestException(f"Failed - {errors_as_string}. See logs for more details.", errors)
  
  return data

def calculate_token_retrieval_cooldown(failure_count: int) -> timedelta:
  """Calculates how long to wait before attempting to retrieve a new token, based on
  the number of consecutive failures we've had while attempting to retrieve one"""
  if (failure_count < 1):
    return timedelta(minutes=0)

  minutes = MINIMUM_TOKEN_RETRIEVAL_COOLDOWN_IN_MINUTES * (2 ** (failure_count - 1))
  return timedelta(minutes=min(minutes, MAXIMUM_TOKEN_RETRIEVAL_COOLDOWN_IN_MINUTES))

class OctopusEnergyApiClient:

  def __init__(self, api_key, electricity_price_cap = None, gas_price_cap = None, timeout_in_seconds = 20, favour_direct_debit_rates = True):
    if (api_key is None):
      raise Exception('API KEY is not set')

    self._api_key = api_key
    self._base_url = 'https://api.oegb-kraken.energy'
    self._backend_base_url = 'https://api.backend.octopus.energy'

    self._graphql_token = None
    self._graphql_expiration = None
    self._graphql_refresh_token = None
    self._graphql_refresh_expiration = None

    self._product_tracker_cache = dict()
    self._tariff_links_cache = dict()

    self._electricity_price_cap = electricity_price_cap
    self._gas_price_cap = gas_price_cap
    self._favour_direct_debit_rates = favour_direct_debit_rates

    self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout_in_seconds, sock_read=timeout_in_seconds)
    self._default_headers = { "user-agent": f'{user_agent_value}/{INTEGRATION_VERSION}' }

    self._session = None
    self._is_api_key_invalid = False
    self._token_retrieval_failures = 0
    self._token_retrieval_cooldown_until = None

    # Use asyncio locks for async methods
    self._session_lock = asyncio.Lock()
    self._refresh_token_lock = asyncio.Lock()
    self._tariff_link_lock = asyncio.Lock()

  async def async_close(self):
    async with self._session_lock:
      if self._session is not None:
        await self._session.close()

  async def _create_client_session(self):
    if self._session is not None:
      return self._session
    
    async with self._session_lock:
      if self._session is not None:
        return self._session
      
      self._session = aiohttp.ClientSession(headers=self._default_headers, skip_auto_headers=['User-Agent'])
      return self._session

  async def async_refresh_token(self):
    """Refresh user token"""
    if (self._graphql_expiration is not None and (self._graphql_expiration - timedelta(minutes=5)) > now()):
      return

    async with self._refresh_token_lock:
      if self._is_api_key_invalid:
        _LOGGER.debug("API key has previously been marked as invalid - skipping refresh")
        raise AuthenticationException("API key has previously been marked as invalid - skipping refresh", [])

      # Check that our token wasn't refreshed while waiting for the lock
      if (self._graphql_expiration is not None and (self._graphql_expiration - timedelta(minutes=5)) > now()):
        return

      if (self._token_retrieval_cooldown_until is not None and self._token_retrieval_cooldown_until > now()):
        msg = f"Token retrieval is in cooldown until {self._token_retrieval_cooldown_until} after {self._token_retrieval_failures} consecutive failure(s) - skipping refresh"
        _LOGGER.debug(msg)
        raise ServerException(msg)

      if (self._graphql_refresh_expiration is not None and self._graphql_refresh_expiration < now()):
        _LOGGER.debug("Refresh token expired - clearing")
        self._graphql_refresh_token = None
        self._graphql_expiration = None

      try:
        try:
          await self.__async_fetch_token()
        except AuthenticationException:
          if (self._graphql_refresh_token is not None):
            _LOGGER.debug("Failed to refresh auth token using refresh token, attempting to use original API key")
            self._graphql_refresh_token = None
            self._graphql_expiration = None
            
            try:
              await self.__async_fetch_token()
            except AuthenticationException:
              _LOGGER.error("Failed to refresh auth token using original API key")
              self._is_api_key_invalid = True
              raise
          else:
            _LOGGER.error("Failed to refresh auth token using original API key")
            self._is_api_key_invalid = True
            raise

      except TimeoutError:
        _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
        raise TimeoutException()
      except ServerException:
        self._token_retrieval_failures += 1
        self._token_retrieval_cooldown_until = now() + calculate_token_retrieval_cooldown(self._token_retrieval_failures)
        _LOGGER.debug(f"Failed to retrieve auth token {self._token_retrieval_failures} time(s) in a row - not attempting again until {self._token_retrieval_cooldown_until}")
        raise

      self._token_retrieval_failures = 0
      self._token_retrieval_cooldown_until = None

  async def __async_fetch_token(self):
    client = await self._create_client_session()
    url = f'{self._base_url}/v1/graphql/'
    payload = { "query": api_token_query.format(api_key=self._api_key) if self._graphql_refresh_token is None else api_token_refresh_query.format(refresh_token=self._graphql_refresh_token) }
    headers = { integration_context_header: "refresh-token" }
    async with client.post(url, headers=headers, json=payload) as token_response:
      token_response_body = await self.__async_read_response__(token_response, url)
      if (token_response_body is not None and 
          "data" in token_response_body and
          "obtainKrakenToken" in token_response_body["data"] and 
          token_response_body["data"]["obtainKrakenToken"] is not None and
          "token" in token_response_body["data"]["obtainKrakenToken"] and
          "refreshToken" in token_response_body["data"]["obtainKrakenToken"] and
          "refreshExpiresIn" in token_response_body["data"]["obtainKrakenToken"]):
        
        self._graphql_token = token_response_body["data"]["obtainKrakenToken"]["token"]
        self._graphql_refresh_token = token_response_body["data"]["obtainKrakenToken"]["refreshToken"]
        self._graphql_refresh_expiration = datetime.fromtimestamp(token_response_body["data"]["obtainKrakenToken"]["refreshExpiresIn"], tz=timezone.utc)
        self._graphql_expiration = self.__decode_jwt_expiry(self._graphql_token)
      elif (self._graphql_expiration is None or self._graphql_expiration < now()):
        raise AuthenticationException("Failed to retrieve auth token and current token is expired", [])
      else:
        _LOGGER.error("Failed to retrieve auth token")

  def __decode_jwt_expiry(self, token: str):
    try:
      payload = token.split(".")[1]
      payload += "=" * (-len(payload) % 4)
      claims = json.loads(base64.urlsafe_b64decode(payload))

      if "exp" in claims:
        return datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
      
      raise Exception("Failed to decode JWT expiry - no 'exp' claim found")
    except Exception:
      _LOGGER.debug("Failed to decode JWT expiry - falling back to default expiration", exc_info=True)
      raise

  def map_electricity_meters(self, meter_point):
    is_export = (meter_point["meterPoint"]["direction"] == 'EXPORT') \
      if "meterPoint" in meter_point and "direction" in meter_point["meterPoint"] and meter_point["meterPoint"]["direction"] is not None \
      else None
    meters = list(
      map(lambda m: {
        "active_from": parse_date(m["activeFrom"]) if m["activeFrom"] is not None else None,
        "active_to": parse_date(m["activeTo"]) if m["activeTo"] is not None else None,
        "serial_number": m["serialNumber"],
        "is_export": is_export if is_export is not None else m["smartExportElectricityMeter"] is not None,
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
  
  def map_properties(self, properties):
    property_ids = []
    for property in properties:
      if ("occupancyPeriods" in property and property["occupancyPeriods"] is not None):
        for period in property["occupancyPeriods"]:
          if "effectiveTo" in period and (period["effectiveTo"] is None or parse_datetime(period["effectiveTo"]) < now()):
            property_ids.append(property["id"])
    return property_ids

  async def async_check_headers(self):
    """Checks the headers are set correctly"""
    try:
      request_context = "test-headers"
      client = await self._create_client_session()
      url = f'http://httpbin.org/headers'
      headers = { "Authorization": f"TEST", integration_context_header: request_context }
      async with client.get(url, headers=headers) as response:

        text = await response.text()
        response_body = json.loads(text)

        integration_context_header_present = integration_context_header in response_body['headers'] and response_body['headers'][integration_context_header] == request_context
        authorization_header_present = 'Authorization' in response_body['headers'] and response_body['headers']['Authorization'] == 'TEST'
        user_agent_header_present = 'User-Agent' in response_body['headers'] and response_body['headers']['User-Agent'] == self._default_headers['user-agent']
        
        _LOGGER.debug(f'integration_context_header_present: {integration_context_header_present}; authorization_header_present: {authorization_header_present}; user_agent_header_present: {user_agent_header_present}')
        _LOGGER.debug(f'Header response: {text}')

        return (
          integration_context_header_present and
          authorization_header_present and
          user_agent_header_present
        )
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
    return None
    
  async def async_get_account(self, account_id):
    """Get the user's account"""
    await self.async_refresh_token()

    try:
      request_context = "get-account"
      client = await self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": account_query.format(account_id=account_id) }
      headers = { "Authorization": f"{self._graphql_token}", integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as account_response:
        account_response_body = await self.__async_read_response__(account_response, url)
        _LOGGER.debug(f'account: {account_response_body}')

        if (account_response_body is not None and 
            "data" in account_response_body and 
            "account" in account_response_body["data"] and 
            account_response_body["data"]["account"] is not None):
          return {
            "id": account_id,
            "octoplus_enrolled": account_response_body["data"]["octoplusAccountInfo"]["enrollmentStatus"] == "ENROLLED" 
            if "octoplusAccountInfo" in account_response_body["data"] and "enrollmentStatus" in account_response_body["data"]["octoplusAccountInfo"]
            else False,
            "property_ids": list(
              self.map_properties(
                account_response_body["data"]["properties"]
                if "data" in account_response_body and "properties" in account_response_body["data"]
                else []
              )
            ),
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

  async def async_run_graphql_query(self, query: str, variables: dict | None = None, target: str = "octopus"):
    """Runs an arbitrary graphql query/mutation. This is intended to be used for debugging purposes only.

    `target` determines which graphql endpoint the query is sent to - "octopus" for the standard api, or "kraken" for the backend api.
    """
    await self.async_refresh_token()

    if target == "octopus":
      base_url = self._backend_base_url
    elif target == "kraken":
      base_url = self._base_url
    else:
      raise ValueError(f"Unknown target '{target}' - expected 'octopus' or 'kraken'")

    try:
      client = await self._create_client_session()
      url = f'{base_url}/v1/graphql/'

      payload = { "query": query }
      if variables is not None:
        payload["variables"] = variables

      headers = { "Authorization": f"{self._graphql_token}" }
      async with client.post(url, json=payload, headers=headers) as response:
        # Errors are surfaced to the caller as part of the response, rather than raised, so they can be inspected for debugging purposes
        return await self.__async_read_response__(response, url, ignore_errors=True)

    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_heat_pump_ids(self, account_id: str, property_ids: list[str]):
    """Get the user's heat pump ids"""
    await self.async_refresh_token()

    try:
      request_context = "heatpump-ids"
      client = await self._create_client_session()
      url = f'{self._backend_base_url}/v1/graphql/'
      
      heat_pump_ids = []
      for (property_id) in property_ids:
        payload = { "query": backend_heat_pump_ids_query.format(account_id=account_id, property_id=property_id) }
        headers = { "Authorization": f"{self._graphql_token}", integration_context_header: request_context }
        async with client.post(url, json=payload, headers=headers) as heat_pump_response:
          response = await self.__async_read_response__(heat_pump_response, url)

          if (response is not None
              and "data" in response
              and "heatPumpControllersAtLocation" in response["data"]):
            
            heat_pump_ids.extend(list(
              map(
                lambda controller: controller["controller"]["euid"],
                response["data"]["heatPumpControllersAtLocation"]
              )
            ))

      return heat_pump_ids

    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_heat_pump_configuration_and_status(self, account_id: str, euid: str):
    """Get a heat pump configuration and status"""
    await self.async_refresh_token()

    try:
      request_context = "heatpump-configuration"
      client = await self._create_client_session()
      url = f'{self._backend_base_url}/v1/graphql/'
      payload = {
        "query": backend_heat_pump_status_and_config_query.format(
          account_id=account_id,
          euid=euid,
        )
      }
      headers = { "Authorization": f"{self._graphql_token}", integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as heat_pump_response:
        response = await self.__async_read_response__(heat_pump_response, url)

        if (response is not None
            and "data" in response
            and "heatPumpControllerConfiguration" in response["data"]
            and "heatPumpControllerStatus" in response["data"]
            and "heatPumpLifetimePerformance" in response["data"]
            and "heatPumpLivePerformance" in response["data"]):
          return HeatPumpResponse.model_validate(response["data"])

      return None

    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_set_heat_pump_hush_mode(self, account_id: str, euid: str, is_enabled: bool):
    """Get a heat pump configuration and status"""
    await self.async_refresh_token()

    try:
      request_context = "heatpump-hush-mode"
      client = await self._create_client_session()
      url = f'{self._backend_base_url}/v1/graphql/'
      payload = {
        "query": backend_heat_pump_set_hush_mode_mutation.format(
          account_id=account_id,
          euid=euid,
          is_enabled=str(is_enabled).lower()
        )
      }
      headers = { "Authorization": f"{self._graphql_token}", integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as heat_pump_response:
        await self.__async_read_response__(heat_pump_response, url)

      return None

    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_set_heat_pump_flow_temp_config(self, account_id: str, euid: str, weather_comp_enabled: bool, weather_comp_min_temperature: float, weather_comp_max_temperature: float, fixed_flow_temperature: float):
    """Sets the flow temperature for a given heat pump zone"""
    await self.async_refresh_token()

    try:
      request_context = "set-heatpump-flow-temp"
      client = await self._create_client_session()
      url = f'{self._backend_base_url}/v1/graphql/'
      query = backend_heat_pump_update_flow_temp_config_mutation.format(account_id=account_id, euid=euid, weather_comp_enabled=str(weather_comp_enabled).lower(), weather_comp_min_temperature=weather_comp_min_temperature, weather_comp_max_temperature=weather_comp_max_temperature, fixed_flow_temperature=fixed_flow_temperature)
      payload = { "query": query }
      headers = { "Authorization": f"{self._graphql_token}", integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as heat_pump_response:
        await self.__async_read_response__(heat_pump_response, url)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_set_heat_pump_zone_mode(self, account_id: str, euid: str, zone_id: str, zone_mode: str, target_temperature: float | None):
    """Sets the mode for a given heat pump zone"""
    await self.async_refresh_token()

    try:
      request_context = "set-heatpump-mode"
      client = await self._create_client_session()
      url = f'{self._backend_base_url}/v1/graphql/'
      query = (backend_heat_pump_set_zone_mode_with_setpoint_mutation.format(account_id=account_id, euid=euid, zone_id=zone_id, zone_mode=zone_mode, target_temperature=target_temperature) 
               if target_temperature is not None 
               else backend_heat_pump_set_zone_mode_without_setpoint_mutation.format(account_id=account_id, euid=euid, zone_id=zone_id, zone_mode=zone_mode))
      payload = { "query": query }
      headers = { "Authorization": f"{self._graphql_token}", integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as heat_pump_response:
        await self.__async_read_response__(heat_pump_response, url)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
  async def async_boost_heat_pump_zone(self, account_id: str, euid: str, zone_id: str, end_datetime: datetime, target_temperature: float):
    """Boost a given heat pump zone"""
    await self.async_refresh_token()

    try:
      request_context = "set-heatpump-boost"
      client = await self._create_client_session()
      url = f'{self._backend_base_url}/v1/graphql/'
      query = backend_heat_pump_boost_zone_mutation.format(account_id=account_id, euid=euid, zone_id=zone_id, end_at=end_datetime.isoformat(sep="T"), target_temperature=target_temperature) 
      payload = { "query": query }
      headers = { "Authorization": f"{self._graphql_token}", integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as heat_pump_response:
        await self.__async_read_response__(heat_pump_response, url)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_saving_sessions(self, account_id: str) -> SavingSessionsResponse:
    """Get the user's seasons savings"""
    await self.async_refresh_token()

    try:
      request_context = "saving-sessions"
      client = await self._create_client_session()
      url = f'{self._backend_base_url}/v1/graphql/'
      payload = { "query": backend_octoplus_saving_session_query.format(account_id=account_id) }
      headers = { "Authorization": f"{self._graphql_token}", integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as account_response:
        response_body = await self.__async_read_response__(account_response, url)

        if (response_body is not None and "data" in response_body):

          available_power_down_events = []
          available_power_up_events = []
          joined_power_down_events = []
          joined_power_up_events = []

          for ev in response_body["data"]["savingSessions"]["events"]:
            saving_session_event = SavingSession(ev["id"],
                                                 ev["code"],
                                                 as_utc(parse_datetime(ev["startAt"])),
                                                 as_utc(parse_datetime(ev["endAt"])),
                                                 ev["rewardPerKwhInOctoPoints"],
                                                 list(map(lambda gsp: f"{gsp['regionId']}", ev["targetRegion"]))
                                                 if "targetRegion" in ev and ev["targetRegion"] is not None
                                                 else None,
                                                 ev["capacityStatus"])
            if ev["eventType"] in power_down_event_types:
              available_power_down_events.append(saving_session_event)
            elif ev["eventType"] in power_up_event_types and saving_session_event.availability is not None:
              available_power_up_events.append(saving_session_event)

          for ev in response_body["data"]["savingSessions"]["account"]["joinedEvents"]:
            saving_session_event = SavingSession(ev["eventId"],
                                                 None,
                                                 as_utc(parse_datetime(ev["startAt"])),
                                                 as_utc(parse_datetime(ev["endAt"])),
                                                 ev["rewardGivenInOctoPoints"],
                                                 None,
                                                 None)
            if ev["eventType"] in power_down_event_types:
              joined_power_down_events.append(saving_session_event)
            elif ev["eventType"] in power_up_event_types:
              joined_power_up_events.append(saving_session_event)

          return SavingSessionsResponse(available_power_down_events,
                                        joined_power_down_events,
                                        available_power_up_events,
                                        joined_power_up_events,
                                        f"{response_body['data']['savingSessions']['account']['signedUpMeterPoint']['regionId']}"
                                        if "signedUpMeterPoint" in response_body["data"]["savingSessions"]["account"] and response_body["data"]["savingSessions"]["account"]["signedUpMeterPoint"] is not None
                                        else None,
                                        int(response_body["data"]["savingSessions"]["account"]["tokenBalance"]))
        else:
          _LOGGER.error("Failed to retrieve saving sessions")
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

    return None

  async def async_get_free_electricity_sessions(self, account_id: str) -> FreeElectricitySessionsResponse:
    """Get the user's free electricity sessions"""

    try:
      request_context = "free-electricity-sessions"
      client = await self._create_client_session()
      url = f'https://oe-api.davidskendall.co.uk/free_electricity.json'
      payload = { }
      headers = { integration_context_header: request_context }
      async with client.get(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)

        if (response_body is not None and "data" in response_body):
          sessions = []
          for item in response_body["data"]:
            if "is_test" in item and item["is_test"] == True:
              continue

            sessions.append(FreeElectricitySession(
              item["id"],
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

  async def async_get_octoplus_scratchcard(self, account_id: str) -> OctoplusScratchcardResponse:
    """Get the account's active Octoplus scratchcard data."""
    await self.async_refresh_token()

    try:
      request_context = "octoplus-scratchcard"
      client = await self._create_client_session()
      url = f'{self._backend_base_url}/v1/graphql/'
      payload = {
        "query": octoplus_scratchcard_query,
        "variables": {"accountNumber": account_id},
      }
      headers = { "Authorization": f"{self._graphql_token}", integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        data = response_body.get("data") if response_body is not None else None
        scratchcard_data = data.get("octoplusActiveScratchcardData") if data is not None else None
        if scratchcard_data is not None and "activeSession" in scratchcard_data and "scratchcard" in scratchcard_data:
          return OctoplusScratchcardResponse.model_validate(scratchcard_data)
        raise RequestException("Failed to retrieve Octoplus scratchcard data", [])
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_octoplus_points(self):
    """Get the user's octoplus points"""
    await self.async_refresh_token()

    try:
      request_context = "octoplus-points"
      client = await self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      # Get account response
      payload = { "query": octoplus_points_query }
      headers = { "Authorization": f"JWT {self._graphql_token}", integration_context_header: request_context }
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

  async def async_redeem_weekend_happy_hour(self, account_id: str, event_code: str) -> JoinSavingSessionResponse:
    """Redeem a weekend happy hour"""
    await self.async_refresh_token()

    try:
      request_context = "redeem-weekend-happy-hour"
      client = await self._create_client_session()
      url = f'{self._backend_base_url}/v1/graphql/'
      payload = { "query": backend_redeem_weekend_happy_hour_mutation.format(account_id=account_id, event_code=event_code) }
      headers = { "Authorization": self._graphql_token, integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as join_response:
        try:
          await self.__async_read_response__(join_response, url)
          return JoinSavingSessionResponse(True, [])
        except RequestException as e:
          _LOGGER.info(e)
          return JoinSavingSessionResponse(False, e.errors)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
  
  async def async_join_octoplus_saving_session(self, account_id: str, event_code: str) -> JoinSavingSessionResponse:
    """Join a saving session"""
    await self.async_refresh_token()

    try:
      request_context = "join-saving-session"
      client = await self._create_client_session()
      url = f'{self._backend_base_url}/v1/graphql/'
      payload = { "query": backend_octoplus_saving_session_join_mutation.format(account_id=account_id, event_code=event_code) }
      headers = { "Authorization": f"{self._graphql_token}", integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as join_response:

        try:
          await self.__async_read_response__(join_response, url)
          return JoinSavingSessionResponse(True, [])
        except RequestException as e:
          _LOGGER.info(e)
          return JoinSavingSessionResponse(False, e.errors)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
  async def async_redeem_octoplus_points_into_account_credit(self, account_id: str, points_to_redeem: int) -> RedeemOctoplusPointsResponse:
    """Redeem octoplus points"""
    await self.async_refresh_token()

    try:
      request_context = "redeem-octoplus-points"
      client = await self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'
      payload = { "query": redeem_octoplus_points_account_credit_mutation.format(account_id=account_id, points=points_to_redeem) }
      headers = { "Authorization": f"JWT {self._graphql_token}", integration_context_header: request_context }
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
      request_context = "home-mini-consumption"
      client = await self._create_client_session()
      url = f'{self._base_url}/v1/graphql/'

      payload = { "query": live_consumption_query.format(device_id=device_id, period_from=period_from.strftime("%Y-%m-%dT%H:%M:%S%z"), period_to=period_to.strftime("%Y-%m-%dT%H:%M:%S%z")) }
      headers = { "Authorization": f"JWT {self._graphql_token}", integration_context_header: request_context }
      async with client.post(url, json=payload, headers=headers) as live_consumption_response:
        response_body = await self.__async_read_response__(live_consumption_response, url)

        if (response_body is not None and "data" in response_body and "smartMeterTelemetry" in response_body["data"] and response_body["data"]["smartMeterTelemetry"] is not None and len(response_body["data"]["smartMeterTelemetry"]) > 0):
          return list(map(lambda mp: {
            "total_consumption": float(mp["consumption"]) / 1000 if "consumption" in mp and mp["consumption"] is not None else None,
            "total_export": float(mp["export"]) / 1000 if "export" in mp and mp["export"] is not None else None,
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
      request_context = "electricity-rates"
      client = await self._create_client_session()
      auth = aiohttp.BasicAuth(self._api_key, '')
      page = 1
      has_more_rates = True
      while has_more_rates:
        url = f'{self._base_url}/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates?period_from={period_from.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}&period_to={period_to.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}&page={page}'
        headers = { integration_context_header: request_context }
        async with client.get(url, auth=auth, headers=headers) as response:
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
