from datetime import datetime, timedelta

from homeassistant.components.sensor import (
  SensorStateClass,
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
  
  # If we've gone into a new day, then reset the consumption result
  if ((new_tracked_consumption_data is not None and len(new_tracked_consumption_data) > 0 and
      (new_tracked_consumption_data[0]["start"].year != start_of_day.year or new_tracked_consumption_data[0]["start"].month != start_of_day.month or new_tracked_consumption_data[0]["start"].day != start_of_day.day)) or
      
      (new_untracked_consumption_data is not None and len(new_untracked_consumption_data) > 0 and
      (new_untracked_consumption_data[0]["start"].year != start_of_day.year or new_untracked_consumption_data[0]["start"].month != start_of_day.month or new_untracked_consumption_data[0]["start"].day != start_of_day.day))):
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

  