from datetime import datetime, timedelta

def add_consumption(current: datetime, consumption_data: list, new_value: float, old_value: float, is_accumulative_value):
  start_of_day = current.replace(hour=0, minute=0, second=0, microsecond=0)
  target_start = current.replace(minute=0 if current.minute % 30 == 0 else 30, second=0, microsecond=0)
  target_end = target_start + timedelta(minutes=30)

  # If we've gone into a new day, then reset the consumption result
  new_consumption_data = consumption_data
  if (consumption_data is not None and len(consumption_data) > 0 and
      (consumption_data[0]["start"].year != start_of_day.year or consumption_data[0]["start"].month != start_of_day.month or consumption_data[0]["start"].day != start_of_day.day)):
    new_consumption_data = []

  if is_accumulative_value == False:
    value = new_value
  elif old_value is not None:
    value = new_value - old_value
  else:
    # Can't calculate accurately without an old value
    return

  consumption_added = False
  for consumption in new_consumption_data:
    if (consumption["start"] == target_start and consumption["end"] == target_end):
      consumption_added = True
      consumption["consumption"] += value
      break

  if consumption_added == False:
    new_consumption_data.append({
      "start": target_start,
      "end": target_end,
      "consumption": value
    })

  return new_consumption_data