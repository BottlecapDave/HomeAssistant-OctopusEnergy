import logging
from datetime import (datetime, timedelta, time)

from homeassistant.util.dt import (utcnow, parse_datetime)

from homeassistant.helpers import storage

from ..utils import get_active_tariff_code, get_tariff_parts

from ..const import DOMAIN

from ..api_client.intelligent_settings import IntelligentSettings

mock_intelligent_data_key = "MOCK_INTELLIGENT_DATA"

_LOGGER = logging.getLogger(__name__)

async def async_mock_intelligent_data(hass):
  mock_data = hass.data[DOMAIN][mock_intelligent_data_key] if mock_intelligent_data_key in hass.data[DOMAIN] else None
  if mock_data is None:
    store = storage.Store(hass, "1", "octopus_energy.mock_intelligent_responses")
    hass.data[DOMAIN][mock_intelligent_data_key] = await store.async_load() is not None
  
  _LOGGER.debug(f'MOCK_INTELLIGENT_DATA: {hass.data[DOMAIN][mock_intelligent_data_key]}')

  return hass.data[DOMAIN][mock_intelligent_data_key]

def mock_intelligent_dispatches():
  planned = []
  completed = []

  dispatches = [
    {
      "start": utcnow().replace(hour=19, minute=0, second=0, microsecond=0),
      "end": utcnow().replace(hour=20, minute=0, second=0, microsecond=0),
      "charge_in_kwh": 1,
      "source": "smart-charge"
    },
    {
      "start": utcnow().replace(hour=6, minute=0, second=0, microsecond=0),
      "end": utcnow().replace(hour=7, minute=0, second=0, microsecond=0),
      "charge_in_kwh": 1.2,
      "source": "smart-charge"
    },
    {
      "start": utcnow().replace(hour=7, minute=0, second=0, microsecond=0),
      "end": utcnow().replace(hour=8, minute=0, second=0, microsecond=0),
      "charge_in_kwh": 4.6,
      "source": "smart-charge"
    }
  ]

  for dispatch in dispatches:
    if (dispatch["end"] > utcnow()):
      planned.append(dispatch)
    else:
      completed.append(dispatch)

  return {
    "planned": planned,
    "completed": completed
  }

def mock_intelligent_settings():
  return IntelligentSettings(
    True,
    90,
    80,
    time(7,30),
    time(9,10),
  )

def mock_intelligent_device():
  return {
    "krakenflexDeviceId": "1",
		"vehicleMake": "Tesla",
		"vehicleModel": "Model Y",
    "vehicleBatterySizeInKwh": 75.0,
		"chargePointMake": "MyEnergi",
		"chargePointModel": "Zappi",
    "chargePointPowerInKw": 6.5 
  }

def is_intelligent_tariff(tariff_code: str):
  parts = get_tariff_parts(tariff_code.upper())

  return parts is not None and "INTELLI" in parts.product_code

def has_intelligent_tariff(current: datetime, account_info):
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      tariff_code = get_active_tariff_code(current, point["agreements"])
      if tariff_code is not None and is_intelligent_tariff(tariff_code):
        return True

  return False

def __get_dispatch(rate, dispatches, expected_source: str):
  for dispatch in dispatches:
    if (expected_source is None or dispatch["source"] == expected_source) and dispatch["start"] <= rate["valid_from"] and dispatch["end"] >= rate["valid_to"]:
      return dispatch
    
  return None

def adjust_intelligent_rates(rates, planned_dispatches, completed_dispatches):
  off_peak_rate = min(rates, key = lambda x: x["value_inc_vat"])
  adjusted_rates = []

  for rate in rates:
    if rate["value_inc_vat"] == off_peak_rate["value_inc_vat"]:
      adjusted_rates.append(rate)
      continue

    if __get_dispatch(rate, planned_dispatches, "smart-charge") is not None or __get_dispatch(rate, completed_dispatches, None) is not None:
      adjusted_rates.append({
        "valid_from": rate["valid_from"],
        "valid_to": rate["valid_to"],
        "value_inc_vat": off_peak_rate["value_inc_vat"],
        "is_capped": rate["is_capped"] if "is_capped" in rate else False,
        "is_intelligent_adjusted": True
      })
    else:
      adjusted_rates.append(rate)
    
  return adjusted_rates

def is_in_planned_dispatch(current_date: datetime, dispatches) -> bool:
  for event in dispatches:
    if (event["start"] <= current_date and event["end"] >= current_date):
      return True
  
  return False

def is_in_bump_charge(current_date: datetime, dispatches) -> bool:
  for event in dispatches:
    if (event["source"] == "bump-charge" and event["start"] <= current_date and event["end"] >= current_date):
      return True
  
  return False

def clean_previous_dispatches(time: datetime, dispatches):
  min_time = (time - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)

  new_dispatches = {}
  for dispatch in dispatches:
    # Some of our dispatches will be strings when loaded from cache, so convert
    start = parse_datetime(dispatch["start"]) if type(dispatch["start"]) == str else dispatch["start"]
    end = parse_datetime(dispatch["end"]) if type(dispatch["end"]) == str else dispatch["end"]
    if (start >= min_time):
      new_dispatches[(start, end)] = dispatch
      new_dispatches[(start, end)]["start"] = start
      new_dispatches[(start, end)]["end"] = end

  return list(new_dispatches.values())