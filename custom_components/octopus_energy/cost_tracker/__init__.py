from datetime import datetime, timedelta
import logging

from homeassistant.components.sensor import (
  SensorStateClass,
)

from homeassistant.helpers.entity import DeviceInfo

from ..utils.conversions import pence_to_pounds_pence, round_pounds, value_inc_vat_to_pounds
from ..utils.cost import consumption_cost_in_pence

_LOGGER = logging.getLogger(__name__)

def get_device_info_from_device_entry(device_entry):
  if device_entry is None:
    return None

  return DeviceInfo(
    identifiers=device_entry.identifiers,
    name=device_entry.name,
    connections=device_entry.connections,
    manufacturer=device_entry.manufacturer,
    model=device_entry.model,
    sw_version=device_entry.sw_version
  )

class CostTrackerResult:
  tracked_consumption_data: list
  untracked_consumption_data: list

  def __init__(self, tracked_consumption_data: list, untracked_consumption_data: list):
    self.tracked_consumption_data = tracked_consumption_data
    self.untracked_consumption_data = untracked_consumption_data

def __add_consumption(consumption_data: list, target_start: datetime, target_end: datetime, value: float):
  consumption_added = False
  for consumption in consumption_data:
    if (consumption["start"] == target_start and consumption["end"] == target_end):
      consumption_added = True
      consumption["consumption"] += value
      break

  if consumption_added == False:
    consumption_data.append({
      "start": target_start,
      "end": target_end,
      "consumption": value
    })

  return consumption_data

def add_consumption(current: datetime,
                    tracked_consumption_data: list,
                    untracked_consumption_data: list,
                    new_value: float,
                    old_value: float,
                    new_last_reset: datetime,
                    old_last_reset: datetime,
                    is_accumulative_value: bool,
                    is_tracking: bool,
                    is_manual_reset_enabled: bool = False,
                    state_class: str = None):
  if new_value is None:
    return

  # Some total increasing sensors are misbehaving and sometimes drop slightly (https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/901),
  # so we'll have a threshold based on https://github.com/home-assistant/core/issues/57551#issuecomment-942130660
  mean = new_value + (old_value if old_value is not None else 0) / 2
  if mean == 0:
    return
  
  diff = new_value - (old_value if old_value is not None else 0)

  diff_percentage = abs((diff / mean) * 100)
  if (is_accumulative_value == False or 
      (new_last_reset is not None and old_last_reset is not None and new_last_reset > old_last_reset) or
      # Based on https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes, when the new value is less than the old value
      # this represents a reset.
      (state_class == SensorStateClass.TOTAL_INCREASING and old_value is not None and diff < 0 and diff_percentage > 10)):
    value = new_value
  elif old_value is not None:
    value = diff
  else:
    # Can't calculate accurately without an old value
    return

  start_of_day = current.replace(hour=0, minute=0, second=0, microsecond=0)
  target_start = current.replace(minute=(0 if current.minute < 30 else 30), second=0, microsecond=0)
  target_end = target_start + timedelta(minutes=30)

  new_tracked_consumption_data = tracked_consumption_data.copy()
  new_untracked_consumption_data = untracked_consumption_data.copy()
  
  # If we've gone into a new day, then reset the consumption result, unless manual reset is enabled
  if (is_manual_reset_enabled == False and
      ((new_tracked_consumption_data is not None and len(new_tracked_consumption_data) > 0 and
       (new_tracked_consumption_data[0]["start"].year != start_of_day.year or new_tracked_consumption_data[0]["start"].month != start_of_day.month or new_tracked_consumption_data[0]["start"].day != start_of_day.day)) or
      
       (new_untracked_consumption_data is not None and len(new_untracked_consumption_data) > 0 and
       (new_untracked_consumption_data[0]["start"].year != start_of_day.year or new_untracked_consumption_data[0]["start"].month != start_of_day.month or new_untracked_consumption_data[0]["start"].day != start_of_day.day)))):
    new_tracked_consumption_data = []
    new_untracked_consumption_data = []

  if is_tracking:
    new_tracked_consumption_data = __add_consumption(new_tracked_consumption_data, target_start, target_end, value)
  else:
    new_untracked_consumption_data = __add_consumption(new_untracked_consumption_data, target_start, target_end, value)

  return CostTrackerResult(new_tracked_consumption_data, new_untracked_consumption_data)

class AccumulativeCostTrackerResult:
  accumulative_data: list
  total_consumption: float
  total_cost: float

  def __init__(self, accumulative_data: list, total_consumption: float, total_cost: float):
    self.accumulative_data = accumulative_data
    self.total_consumption = total_consumption
    self.total_cost = total_cost

def accumulate_cost(current: datetime, accumulative_data: list, new_cost: float, new_consumption: float) -> AccumulativeCostTrackerResult:
  start_of_day = current.replace(hour=0, minute=0, second=0, microsecond=0)
  
  if accumulative_data is None:
    accumulative_data = []

  total_cost = 0
  total_consumption = 0
  is_day_added = False
  new_accumulative_data = []
  for item in accumulative_data:
    new_item = item.copy()
    
    if "start" in new_item and new_item["start"] == start_of_day:
      new_item["cost"] = new_cost
      new_item["consumption"] = new_consumption
      is_day_added = True

    if "consumption" in new_item:
      total_consumption += new_item["consumption"]

    if "cost" in new_item:
      total_cost += new_item["cost"]

    new_accumulative_data.append(new_item)

  if is_day_added == False:
    new_accumulative_data.append({
      "start": start_of_day,
      "end": start_of_day + timedelta(days=1),
      "cost": new_cost,
      "consumption": new_consumption,
    })

    total_consumption += new_consumption
    total_cost += new_cost

  return AccumulativeCostTrackerResult(new_accumulative_data, total_consumption, total_cost)

def __get_to(item):
    return (item["end"].timestamp(), item["end"].fold)

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_to)
  return sorted

def calculate_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    last_reset,
    minimum_consumption_records = 0,
    target_rate = None
  ):
  if (consumption_data is not None and len(consumption_data) >= minimum_consumption_records and rate_data is not None and len(rate_data) > 0 and standing_charge is not None):

    sorted_consumption_data = __sort_consumption(consumption_data)

    # Only calculate our consumption if our data has changed
    if (last_reset is None or last_reset < sorted_consumption_data[0]["start"]):

      charges = []
      total_cost = 0
      total_consumption = 0

      for consumption in sorted_consumption_data:
        consumption_value = consumption["consumption"]
        consumption_from = consumption["start"]
        consumption_to = consumption["end"]

        try:
          rate = next(r for r in rate_data if r["start"] == consumption_from and r["end"] == consumption_to)
        except StopIteration:
          raise Exception(f"Failed to find rate for consumption between {consumption_from} and {consumption_to}")

        value = rate["value_inc_vat"]

        if target_rate is not None and value != target_rate:
          continue

        total_consumption = total_consumption + consumption_value
        cost = pence_to_pounds_pence(consumption_cost_in_pence(consumption_value, value))
        cost_raw = (consumption_value * value) / 100
        total_cost = total_cost + cost_raw

        current_charge = {
          "start": rate["start"],
          "end": rate["end"],
          "rate": value_inc_vat_to_pounds(value),
          "consumption": consumption_value,
          "cost": cost,
          "cost_raw": cost_raw,
        }

        charges.append(current_charge)
      
      total_cost = round_pounds(total_cost)
      total_cost_plus_standing_charge = total_cost + pence_to_pounds_pence(standing_charge)

      last_reset = sorted_consumption_data[0]["start"] if len(sorted_consumption_data) > 0 else None
      last_calculated_timestamp = sorted_consumption_data[-1]["end"] if len(sorted_consumption_data) > 0 else None

      result = {
        "standing_charge": pence_to_pounds_pence(standing_charge),
        "total_cost_without_standing_charge": total_cost,
        "total_cost": total_cost_plus_standing_charge,
        "total_consumption": total_consumption,
        "last_reset": last_reset,
        "last_evaluated": last_calculated_timestamp,
        "charges": charges,
      }

      return result
    else:
      _LOGGER.debug(f'Skipping consumption and cost calculation as last reset has not changed - last_reset: {last_reset}; consumption start: {sorted_consumption_data[0]["start"]}')
  else:
    _LOGGER.debug(f'Skipping consumption and cost calculation due to lack of data; consumption: {len(consumption_data) if consumption_data is not None else 0}; rates: {len(rate_data) if rate_data is not None else 0}; standing_charge: {standing_charge}')