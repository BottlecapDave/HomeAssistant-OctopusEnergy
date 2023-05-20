from datetime import (datetime)

from ..utils import get_tariff_parts

def is_intelligent_tariff(tariff_code: str):
  parts = get_tariff_parts(tariff_code.upper())

  return parts is not None and "INTELLI" in parts.product_code

def __get_dispatch(rate, dispatches):
  for dispatch in dispatches:
    if dispatch["source"] == "smart-charge" and dispatch["start"] <= rate["valid_from"] and dispatch["end"] >= rate["valid_to"]:
      return dispatch
    
  return None

def adjust_intelligent_rates(rates, planned_dispatches, completed_dispatches):
  off_peak_rate = min(rates, key = lambda x: x["value_inc_vat"])
  adjusted_rates = []

  for rate in rates:
    if rate["value_inc_vat"] == off_peak_rate:
      adjusted_rates.append(rate)
      continue

    if __get_dispatch(rate, planned_dispatches) is not None or __get_dispatch(rate, completed_dispatches) is not None:
      adjusted_rates.append({
        "valid_from": rate["valid_from"],
        "valid_to": rate["valid_to"],
        "value_inc_vat": off_peak_rate["value_inc_vat"]
      })
    else:
      adjusted_rates.append(rate)
    
  return adjusted_rates

def is_in_planned_dispatch(current_date: datetime, dispatches) -> bool:
  for event in dispatches:
    if (event["start"] <= current_date and event["end"] >= current_date):
      return True
  
  return False