import logging
from datetime import (datetime, timedelta, time)
import re

from homeassistant.util.dt import (utcnow, parse_datetime)

from ..utils import get_active_tariff

from ..const import CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES, INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS, INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES, INTELLIGENT_SOURCE_BUMP_CHARGE_OPTIONS, INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS, REFRESH_RATE_IN_MINUTES_INTELLIGENT

from ..storage.intelligent_dispatches_history import IntelligentDispatchesHistory, IntelligentDispatchesHistoryItem
from ..api_client.intelligent_settings import IntelligentSettings
from ..api_client.intelligent_dispatches import IntelligentDispatchItem, IntelligentDispatches, SimpleIntelligentDispatchItem
from ..api_client.intelligent_device import IntelligentDevice

mock_intelligent_data_key = "MOCK_INTELLIGENT_DATA"

_LOGGER = logging.getLogger(__name__)

mock_intelligent_device_id_one = "1F-2B-3C-4D-5E-6F"
mock_intelligent_device_id_two = "6F-5B-4C-3D-2E-1F"

# Expected successful dispatches (UTC)
# 07:00 - 08:00 Smart Charge
# 10:10 - 10:30 Smart Charge (Late dispatch)
# 18:00 - 18:20 Smart Charge (Late dispatch)
# 19:00 - 20:00 Smart Charge

# Not expected to dispatch
# 11:00 - 11:20 Smart Charge (Removed before dispatch)
# 12:00 - 13:00 Bump Charge

def mock_intelligent_dispatches(current_state = "SMART_CONTROL_CAPABLE", device_id = mock_intelligent_device_id_one) -> IntelligentDispatches:
  planned: list[IntelligentDispatchItem] = []
  completed: list[IntelligentDispatchItem] = []

  dispatches = [
    IntelligentDispatchItem(
      utcnow().replace(hour=7, minute=0, second=0, microsecond=0),
      utcnow().replace(hour=8, minute=0, second=0, microsecond=0),
      4.6,
      None,
      "home"
    ),
    IntelligentDispatchItem(
      utcnow().replace(hour=12, minute=0, second=0, microsecond=0),
      utcnow().replace(hour=13, minute=0, second=0, microsecond=0),
      4.6,
      INTELLIGENT_SOURCE_BUMP_CHARGE_OPTIONS[-1].upper(),
      "home"
    )
  ]

  if device_id == mock_intelligent_device_id_one:
    dispatches.append(IntelligentDispatchItem(
      utcnow().replace(hour=19, minute=0, second=0, microsecond=0),
      utcnow().replace(hour=20, minute=0, second=0, microsecond=0),
      1,
      INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS[0],
      "home"
    ))

  # Simulate a pending dispatch being removed just before it begins
  if (utcnow() <= utcnow().replace(hour=11, minute=0, second=0, microsecond=0) - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)):
    dispatches.append(
      IntelligentDispatchItem(
        utcnow().replace(hour=11, minute=0, second=0, microsecond=0),
        utcnow().replace(hour=11, minute=20, second=0, microsecond=0),
        1.2,
        INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS[0].upper(),
        "home"
      )
    ) 

  # Simulate a dispatch coming in late
  if (utcnow() >= utcnow().replace(hour=10, minute=10, second=0, microsecond=0) - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)):
    dispatches.append(
      IntelligentDispatchItem(
        utcnow().replace(hour=10, minute=10, second=0, microsecond=0),
        utcnow().replace(hour=10, minute=30, second=0, microsecond=0),
        1.2,
        INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS[-1].upper(),
        "home"
      )
    )

  # Simulate a dispatch coming in late
  if (utcnow() >= utcnow().replace(hour=18, minute=0, second=0, microsecond=0) - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)):
    dispatches.append(
      IntelligentDispatchItem(
        utcnow().replace(hour=18, minute=0, second=0, microsecond=0),
        utcnow().replace(hour=18, minute=20, second=0, microsecond=0),
        1.2,
        INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS[0].upper(),
        "home"
      )
    )

  for dispatch in dispatches:
    if utcnow() >= dispatch.start and utcnow() <= dispatch.end:
      if (dispatch.source.lower() in INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS if dispatch.source is not None else False):
        current_state = "SMART_CONTROL_IN_PROGRESS"
      elif (dispatch.source.lower() in INTELLIGENT_SOURCE_BUMP_CHARGE_OPTIONS if dispatch.source is not None else False):
        current_state = "BOOSTING"
      else:
        # If there is one without a source, then don't push it to completed dispatch to simulate
        # a planned dispatch not turning into a completed dispatch
        continue

    if (dispatch.end > utcnow()):
      planned.append(dispatch)
    else:
      dispatch.source = None
      completed.append(dispatch)

  return IntelligentDispatches(current_state, planned, completed)

def mock_intelligent_settings():
  return IntelligentSettings(
    True,
    90,
    80,
    time(7,20),
    time(9,10),
  )

def mock_intelligent_devices():
  return [
    IntelligentDevice(
      mock_intelligent_device_id_one,
      "MYENERGI",
      "Myenergi",
      "Zappi smart EV",
      None,
      6.5,
      INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS
    ),
    IntelligentDevice(
      mock_intelligent_device_id_two,
      "TESLA",
      "TESLA",
      "Model Y",
      26.4,
      None,
      INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES
    )
  ]

def is_intelligent_product(product_code: str):
  # Need to ignore Octopus Intelligent Go tariffs
  return product_code is not None and (
    "INTELLI-BB-VAR" in product_code.upper() or
    "INTELLI-VAR" in product_code.upper() or
    "INTELLI-FIX" in product_code.upper() or
    product_code.upper().startswith("IOG") or
    re.search("INTELLI-[0-9]", product_code.upper()) is not None
  )

def has_intelligent_tariff(current: datetime, account_info):
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      tariff = get_active_tariff(current, point["agreements"])
      if tariff is not None and is_intelligent_product(tariff.product):
        return True

  return False

def get_applicable_dispatch_periods(planned_dispatches: list[IntelligentDispatchItem],
                                    started_dispatches: list[SimpleIntelligentDispatchItem],
                                    mode: str):
  dispatches: list[SimpleIntelligentDispatchItem] = []
  if planned_dispatches is not None and mode == CONFIG_MAIN_INTELLIGENT_RATE_MODE_PLANNED_AND_STARTED_DISPATCHES:
    for planned_dispatch in planned_dispatches:
      # Source as none counts as smart charge - https://forum.octopus.energy/t/pending-and-completed-octopus-intelligent-dispatches/8510/102
      if (planned_dispatch.source is not None and (planned_dispatch.source.lower() in INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS) == False):
        continue

      dispatch_exists = False

      for existing_dispatch in dispatches:
        # If the planned dispatch starts within the existing dispatch, extend the end
        if (planned_dispatch.start >= existing_dispatch.start and planned_dispatch.start <= existing_dispatch.end):
          existing_dispatch.end = max(existing_dispatch.end, planned_dispatch.end)
          dispatch_exists = True
        # If the planned dispatch ends within the existing dispatch, extend the start
        if (planned_dispatch.end <= existing_dispatch.end and planned_dispatch.end >= existing_dispatch.start):
          existing_dispatch.start = min(existing_dispatch.start, planned_dispatch.start)
          dispatch_exists = True

      if dispatch_exists == False:
        dispatches.append(SimpleIntelligentDispatchItem(planned_dispatch.start, planned_dispatch.end))

  if started_dispatches is not None:
    for started_dispatch in started_dispatches:
      dispatch_exists = False

      for existing_dispatch in dispatches:
        # If the started dispatch starts within the existing dispatch, extend the end
        if (started_dispatch.start >= existing_dispatch.start and started_dispatch.start <= existing_dispatch.end):
          existing_dispatch.end = max(existing_dispatch.end, started_dispatch.end)
          dispatch_exists = True
        # If the started dispatch ends within the existing dispatch, extend the start
        if (started_dispatch.end <= existing_dispatch.end and started_dispatch.end >= existing_dispatch.start):
          existing_dispatch.start = min(existing_dispatch.start, started_dispatch.start)
          dispatch_exists = True

      if dispatch_exists == False:
        dispatches.append(SimpleIntelligentDispatchItem(started_dispatch.start, started_dispatch.end))

  dispatches.sort(key = lambda x: x.start)
  return dispatches

def adjust_intelligent_rates(rates,
                             planned_dispatches: list[IntelligentDispatchItem],
                             started_dispatches: list[SimpleIntelligentDispatchItem],
                             mode: str):
  if len(rates) < 1:
    return rates

  off_peak_rate =  min(rates, key = lambda x: x["value_inc_vat"])
  adjusted_rates = []

  applicable_dispatches = get_applicable_dispatch_periods(planned_dispatches, started_dispatches, mode)

  for rate in rates:
    if rate["value_inc_vat"] == off_peak_rate["value_inc_vat"]:
      adjusted_rates.append(rate)
      continue

    applicable_dispatch: SimpleIntelligentDispatchItem | None = next(
      (dispatch for dispatch in applicable_dispatches 
      if (dispatch.start <= rate["start"] and dispatch.end >= rate["end"]) or # Rate is within dispatch
          (dispatch.start >= rate["start"] and dispatch.start < rate["end"]) or # dispatch starts within rate
          (dispatch.end > rate["start"] and dispatch.end <= rate["end"]) # dispatch ends within rate
      ),
      None
    )

    if (applicable_dispatch is not None):
      adjusted_rates.append({
        "start": rate["start"],
        "end": rate["end"],
        "tariff_code": rate["tariff_code"],
        "value_inc_vat": off_peak_rate["value_inc_vat"],
        "is_capped": rate["is_capped"] if "is_capped" in rate else False,
        "is_intelligent_adjusted": True
      })
    else:
      adjusted_rates.append(rate)
    
  return adjusted_rates

def is_in_bump_charge(current_date: datetime, dispatches: list[IntelligentDispatchItem]) -> bool:
  for dispatch in dispatches:
    if (dispatch.start <= current_date and dispatch.end >= current_date):
      return (dispatch.source.lower() in INTELLIGENT_SOURCE_BUMP_CHARGE_OPTIONS if dispatch.source is not None else False)
  
  return False

def clean_previous_dispatches(time: datetime, dispatches: list[IntelligentDispatchItem]) -> list[IntelligentDispatchItem]:
  min_time = (time - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)

  new_dispatches = {}
  for dispatch in dispatches:
    if (dispatch.start >= min_time):
      new_dispatches[(dispatch.start, dispatch.end)] = dispatch

  return list(new_dispatches.values())

def clean_intelligent_dispatch_history(time: datetime,
                                       dispatches: IntelligentDispatches,
                                       history: list[IntelligentDispatchesHistoryItem]) -> list[IntelligentDispatchItem]:
  history.sort(key = lambda x: x.timestamp)

  new_history: list[IntelligentDispatchesHistoryItem] = []
  previous_history_item: IntelligentDispatchesHistoryItem | None = None
  min_time = time - timedelta(days=2)
  
  for history_item in history:

    if history_item.timestamp >= min_time:
      # Ensure we have one record before the minimum stored time so we know what we had at the start
      if (len(new_history) == 0 and previous_history_item is not None):
        new_history.append(previous_history_item)

      new_history.append(history_item)

    previous_history_item = history_item

  # Ensure we have one record before the minimum stored time so we know what we had at the start
  if (len(new_history) == 0 and previous_history_item is not None):
    new_history.append(previous_history_item)

  if len(new_history) < 1 or has_dispatches_changed(new_history[-1].dispatches, dispatches):
    new_history.append(IntelligentDispatchesHistoryItem(
      time,
      dispatches)
    )

  return new_history

def dictionary_list_to_dispatches(dispatches: list):
  items = []
  if (dispatches is not None):
    for dispatch in dispatches:
      items.append(
        IntelligentDispatchItem(
          parse_datetime(dispatch["start"]),
          parse_datetime(dispatch["end"]),
          float(dispatch["charge_in_kwh"]) if "charge_in_kwh" in dispatch and dispatch["charge_in_kwh"] is not None else None,
          dispatch["source"] if "source" in dispatch else "",
          dispatch["location"] if "location" in dispatch else ""
        )
      )

  return items

def dispatches_to_dictionary_list(dispatches: list[IntelligentDispatchItem], ignore_none: bool):
  items = []
  if (dispatches is not None):
    for dispatch in dispatches:
      items.append(dispatch.to_dict(ignore_none))

  return items

def simple_dispatches_to_dictionary_list(dispatches: list[SimpleIntelligentDispatchItem]):
  items = []
  if (dispatches is not None):
    for dispatch in dispatches:
      items.append(dispatch.to_dict())

  return items

def get_current_and_next_dispatching_periods(current: datetime, applicable_dispatches: list[SimpleIntelligentDispatchItem]):
  current_dispatch = None
  next_dispatch = None

  if applicable_dispatches is not None:
    for applicable_dispatch in applicable_dispatches:
      if current >= applicable_dispatch.start:
        if current < applicable_dispatch.end:
          current_dispatch = applicable_dispatch
      else:
        next_dispatch = applicable_dispatch
        break
  
  return (current_dispatch, next_dispatch)

class IntelligentFeatures:
  def __init__(self,
               is_default_features: bool,
               bump_charge_supported: bool,
               charge_limit_supported: bool,
               planned_dispatches_supported: bool,
               ready_time_supported: bool,
               smart_charge_supported: bool,
               current_state_supported: bool):
    self.is_default_features = is_default_features
    self.bump_charge_supported = bump_charge_supported
    self.charge_limit_supported = charge_limit_supported
    self.planned_dispatches_supported = planned_dispatches_supported
    self.ready_time_supported = ready_time_supported
    self.smart_charge_supported = smart_charge_supported
    self.current_state_supported = current_state_supported

FULLY_SUPPORTED_INTELLIGENT_PROVIDERS = [
  "DAIKIN",
  "ECOBEE",
  "ENERGIZER",
  "ENPHASE",
  "ENODE",
  "FORD",
  "GIVENERGY",
  "HUAWEI",
  "JEDLIX",
  "JEDLIX-V2",
  "MYENERGI",
  "OCPP_WALLBOX",
  "SENSI",
  "SMARTCAR",
  "TESLA",
  "SMART_PEAR",
  "HYPERVOLT",
  "INDRA",
  "OCPP"
]

def get_intelligent_features(provider: str) -> IntelligentFeatures:
  normalised_provider = provider.upper() if provider is not None else None
  if normalised_provider == "OHME":
    return IntelligentFeatures(False, False, False, False, False, False, False)
  
  if normalised_provider is not None:
    for provider in FULLY_SUPPORTED_INTELLIGENT_PROVIDERS:
      if normalised_provider == provider or re.search(f"{provider}_V[0-9]+", normalised_provider) is not None:
        return IntelligentFeatures(False, True, True, True, True, True, True)

  return IntelligentFeatures(True, False, False, False, False, False, False)

def device_type_to_friendly_string(device_type: str) -> str:
  if device_type == INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLE_CHARGERS:
    return "Electric Vehicle Charger"
  elif device_type == INTELLIGENT_DEVICE_KIND_ELECTRIC_VEHICLES:
    return "Electric Vehicle"
  else:
    return device_type
  
def has_dispatch_items_changed(existing_dispatches: list[SimpleIntelligentDispatchItem], new_dispatches: list[SimpleIntelligentDispatchItem]):
  if len(existing_dispatches) != len(new_dispatches):
    return True

  if len(existing_dispatches) > 0:
    for i in range(0, len(existing_dispatches)):
      if (existing_dispatches[i].start != new_dispatches[i].start or
          existing_dispatches[i].end != new_dispatches[i].end):
        return True

  return False
  
def has_dispatches_changed(existing_dispatches: IntelligentDispatches, new_dispatches: IntelligentDispatches):
  return (
    existing_dispatches.current_state != new_dispatches.current_state or
    has_dispatch_items_changed(existing_dispatches.completed, new_dispatches.completed) or
    has_dispatch_items_changed(existing_dispatches.planned, new_dispatches.planned) or
    has_dispatch_items_changed(existing_dispatches.started, new_dispatches.started)
  )

def get_applicable_intelligent_dispatch_history(history: IntelligentDispatchesHistory, time: datetime) -> IntelligentDispatchesHistoryItem  | None:
  if history is None or history.history is None or len(history.history) == 0:
    return None

  applicable_history_item: IntelligentDispatchesHistoryItem | None = None
  for history_item in history.history:
    if history_item.timestamp <= time:
      applicable_history_item = history_item
    else:
      break

  return applicable_history_item