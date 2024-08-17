from datetime import (datetime, timedelta)

from homeassistant.util.dt import (as_local, as_utc)

from ..utils.conversions import value_inc_vat_to_pounds

def get_current_rate_information(rates, now: datetime):
  min_target = now.replace(hour=0, minute=0, second=0, microsecond=0)
  max_target = min_target + timedelta(days=1)

  min_rate_value = None
  max_rate_value = None
  total_rate_value = 0
  total_rates = 0
  current_rate = None

  applicable_rates = []
  is_adding_applicable_rates = True

  if rates is not None:
    for period in rates:
      if current_rate is None and len(applicable_rates) > 0 and applicable_rates[0]["value_inc_vat"] != period["value_inc_vat"]:
        applicable_rates.clear()

      if is_adding_applicable_rates and (len(applicable_rates) < 1 or current_rate is None or applicable_rates[0]["value_inc_vat"] == period["value_inc_vat"]):
        applicable_rates.append(period)
      elif current_rate is not None and len(applicable_rates) > 0 and applicable_rates[0]["value_inc_vat"] != period["value_inc_vat"]:
        is_adding_applicable_rates = False
      
      if now >= period["start"] and now <= period["end"]:
        current_rate = period

      if period["start"] >= min_target and period["end"] <= max_target:
        if min_rate_value is None or period["value_inc_vat"] < min_rate_value:
          min_rate_value = period["value_inc_vat"]

        if max_rate_value is None or period["value_inc_vat"] > max_rate_value:
          max_rate_value = period["value_inc_vat"]

        total_rate_value = total_rate_value + period["value_inc_vat"]
        total_rates = total_rates + 1

  if len(applicable_rates) > 0 and current_rate is not None:
    return {
      "all_rates": list(map(lambda x: {
        "start": x["start"],
        "end":   x["end"],
        "value_inc_vat": value_inc_vat_to_pounds(x["value_inc_vat"]),
        "is_capped": x["is_capped"],
        "is_intelligent_adjusted": x["is_intelligent_adjusted"] if "is_intelligent_adjusted" in x else False
      }, rates)),
      "applicable_rates": list(map(lambda x: {
        "start": x["start"],
        "end":   x["end"],
        "value_inc_vat": value_inc_vat_to_pounds(x["value_inc_vat"]),
        "is_capped": x["is_capped"],
        "is_intelligent_adjusted": x["is_intelligent_adjusted"] if "is_intelligent_adjusted" in x else False
      }, applicable_rates)),
      "current_rate": {
        "start": applicable_rates[0]["start"],
        "end": applicable_rates[-1]["end"],
        "tariff_code": current_rate["tariff_code"],
        "value_inc_vat": value_inc_vat_to_pounds(applicable_rates[0]["value_inc_vat"]),
        "is_capped": current_rate["is_capped"],
        "is_intelligent_adjusted": current_rate["is_intelligent_adjusted"] if "is_intelligent_adjusted" in current_rate else False
      },
      "min_rate_today": value_inc_vat_to_pounds(min_rate_value),
      "max_rate_today": value_inc_vat_to_pounds(max_rate_value),
      "average_rate_today": value_inc_vat_to_pounds(total_rate_value / total_rates)
    }

  return None

def get_from(rate):
  return rate["start"]

def get_previous_rate_information(rates, now: datetime):
  current_rate = None
  applicable_rates = []

  if rates is not None:
    for period in reversed(rates):
      if now >= period["start"] and now <= period["end"]:
        current_rate = period
        continue

      if current_rate is not None and current_rate["value_inc_vat"] != period["value_inc_vat"]:
        if len(applicable_rates) == 0 or period["value_inc_vat"] == applicable_rates[0]["value_inc_vat"]:
          applicable_rates.append(period)
        else:
          break
      elif len(applicable_rates) > 0:
        break

  applicable_rates.sort(key=get_from)

  if len(applicable_rates) > 0 and current_rate is not None:
    return {
      "applicable_rates": list(map(lambda x: {
        "start": x["start"],
        "end":   x["end"],
        "value_inc_vat": value_inc_vat_to_pounds(x["value_inc_vat"]),
        "is_capped": x["is_capped"],
        "is_intelligent_adjusted": x["is_intelligent_adjusted"] if "is_intelligent_adjusted" in x else False
      }, applicable_rates)),
      "previous_rate": {
        "start": applicable_rates[0]["start"],
        "end": applicable_rates[-1]["end"],
        "value_inc_vat": value_inc_vat_to_pounds(applicable_rates[0]["value_inc_vat"]),
      }
    }

  return None

def get_next_rate_information(rates, now: datetime):
  current_rate = None
  applicable_rates = []

  if rates is not None:
    for period in rates:
      if now >= period["start"] and now <= period["end"]:
        current_rate = period
        continue

      if current_rate is not None and current_rate["value_inc_vat"] != period["value_inc_vat"]:
        if len(applicable_rates) == 0 or period["value_inc_vat"] == applicable_rates[0]["value_inc_vat"]:
          applicable_rates.append(period)
        else:
          break
      elif len(applicable_rates) > 0:
        break

  if len(applicable_rates) > 0 and current_rate is not None:
    return {
      "applicable_rates": list(map(lambda x: {
        "start": x["start"],
        "end":   x["end"],
        "value_inc_vat": value_inc_vat_to_pounds(x["value_inc_vat"]),
        "is_capped": x["is_capped"],
        "is_intelligent_adjusted": x["is_intelligent_adjusted"] if "is_intelligent_adjusted" in x else False
      }, applicable_rates)),
      "next_rate": {
        "start": applicable_rates[0]["start"],
        "end": applicable_rates[-1]["end"],
        "value_inc_vat": value_inc_vat_to_pounds(applicable_rates[0]["value_inc_vat"]),
      }
    }

  return None

def get_min_max_average_rates(rates: list):
  min_rate = None
  max_rate = None
  average_rate = 0

  if rates is not None:
    for rate in rates:
      if min_rate is None or min_rate > rate["value_inc_vat"]:
        min_rate = rate["value_inc_vat"]

      if max_rate is None or max_rate < rate["value_inc_vat"]:
        max_rate = rate["value_inc_vat"]

      average_rate += rate["value_inc_vat"]

  return {
    "min": min_rate,
    "max": max_rate,
    # Round as there can be some minor inaccuracies with floats :(
    "average": round(average_rate / len(rates) if rates is not None and len(rates) > 0 else 1, 8)
  }

def get_unique_rates(current: datetime, rates: list):
  # Need to use as local to ensure we get the correct from/to periods relative to our local time
  today_start = as_utc(as_local(current).replace(hour=0, minute=0, second=0, microsecond=0))
  today_end = today_start + timedelta(days=1)

  rate_charges = []
  if rates is not None:
    for rate in rates:
      if rate["start"] >= today_start and rate["end"] <= today_end:
        value = rate["value_inc_vat"]
        if value not in rate_charges:
          rate_charges.append(value)

  rate_charges.sort()

  return rate_charges

def has_peak_rates(total_unique_rates: int):
  return total_unique_rates == 2 or total_unique_rates == 3

def get_peak_type(total_unique_rates: int, unique_rate_index: int):
  if has_peak_rates(total_unique_rates) == False:
    return None

  if unique_rate_index == 0:
    return "off_peak"
  elif unique_rate_index == 1:
    if (total_unique_rates == 2):
      return "peak"
    else:
      return "standard"
  elif total_unique_rates > 2 and unique_rate_index == 2:
    return "peak"
  
  return None

def get_rate_index(total_unique_rates: int, peak_type: str | None):
  if has_peak_rates(total_unique_rates) == False:
    return None

  if peak_type == "off_peak":
    return 0
  if peak_type == "standard":
    return 1
  if peak_type == "peak":
    if total_unique_rates == 2:
      return 1
    else:
      return 2
    
  return None

def get_peak_name(peak_type: str):
  if (peak_type == "off_peak"):
    return "Off Peak"
  if (peak_type == "peak"):
    return "Peak"
  if (peak_type == "standard"):
    return "Standard"
  
  return None