from datetime import datetime, timedelta

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
                    is_tracking: bool):
  if is_accumulative_value == False or (new_last_reset is not None and old_last_reset is not None and new_last_reset > old_last_reset):
    value = new_value
  elif old_value is not None:
    value = new_value - old_value
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