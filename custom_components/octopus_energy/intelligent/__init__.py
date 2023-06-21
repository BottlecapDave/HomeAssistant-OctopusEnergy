from datetime import (datetime, timedelta)

from homeassistant.util.dt import (parse_datetime)

from ..utils import get_tariff_parts

def is_intelligent_tariff(tariff_code: str):
  parts = get_tariff_parts(tariff_code.upper())

  return parts is not None and "INTELLI" in parts.product_code

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