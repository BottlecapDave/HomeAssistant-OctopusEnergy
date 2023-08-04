from datetime import (datetime)

def get_total_consumption(consumption: list):
  total_consumption = 0
  for item in consumption:
    total_consumption += item["consumption"]

  return total_consumption

def get_current_consumption_delta(current_datetime: datetime, current_total_consumption: float, previous_updated: datetime, previous_total_consumption: float):
  if (previous_total_consumption is None or previous_updated is None):
    return None
  
  if (current_datetime.date() == previous_updated.date()):
    return (current_total_consumption - previous_total_consumption)
  
  return current_total_consumption