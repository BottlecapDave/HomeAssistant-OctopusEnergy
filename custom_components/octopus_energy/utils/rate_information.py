from datetime import (datetime, timedelta)

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

      if current_rate is not None and current_rate["value_inc_vat"] != period["value_inc_vat"]:
        if len(applicable_rates) == 0 or period["value_inc_vat"] == applicable_rates[0]["value_inc_vat"]:
          applicable_rates.append(period)
        else:
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

      if current_rate is not None and current_rate["value_inc_vat"] != period["value_inc_vat"]:
        if len(applicable_rates) == 0 or period["value_inc_vat"] == applicable_rates[0]["value_inc_vat"]:
          applicable_rates.append(period)
        else:
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