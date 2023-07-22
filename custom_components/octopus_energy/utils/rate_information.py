from datetime import (datetime, timedelta)

def get_current_rate_information(rates, now: datetime):
  min_target = now.replace(hour=0, minute=0, second=0, microsecond=0)
  max_target = min_target + timedelta(days=1)

  min_rate_value = None
  max_rate_value = None
  total_rate_value = 0
  total_rates = 0
  current_rate = None

  if rates is not None:
    for period in rates:
      if now >= period["valid_from"] and now <= period["valid_to"]:
        current_rate = period

      if period["valid_from"] >= min_target and period["valid_to"] <= max_target:
        if min_rate_value is None or period["value_inc_vat"] < min_rate_value:
          min_rate_value = period["value_inc_vat"]

        if max_rate_value is None or period["value_inc_vat"] > max_rate_value:
          max_rate_value = period["value_inc_vat"]

        total_rate_value = total_rate_value + period["value_inc_vat"]
        total_rates = total_rates + 1

  if current_rate is not None:
    return {
      "rates": list(map(lambda x: {
        "valid_from": x["valid_from"],
        "valid_to":   x["valid_to"],
        "value_inc_vat": x["value_inc_vat"],
        "is_capped": x["is_capped"],
        "is_intelligent_adjusted": x["is_intelligent_adjusted"] if "is_intelligent_adjusted" in x else False
      }, rates)),
      "current_rate": current_rate,
      "min_rate_today": min_rate_value,
      "max_rate_today": max_rate_value,
      "average_rate_today": total_rate_value / total_rates
    }

  return None

def get_valid_from(rate):
  return rate["valid_from"]

def get_previous_rate_information(rates, now: datetime):
  current_rate = None
  applicable_rates = []

  if rates is not None:
    for period in reversed(rates):
      if now >= period["valid_from"] and now <= period["valid_to"]:
        current_rate = period

      if current_rate is not None and current_rate["value_inc_vat"] != period["value_inc_vat"]:
        if len(applicable_rates) == 0 or period["value_inc_vat"] == applicable_rates[0]["value_inc_vat"]:
          applicable_rates.append(period)
        else:
          break

  applicable_rates.sort(key=get_valid_from)

  if len(applicable_rates) > 0:
    return {
      "rates": list(map(lambda x: {
        "valid_from": x["valid_from"],
        "valid_to":   x["valid_to"],
        "value_inc_vat": x["value_inc_vat"],
        "is_capped": x["is_capped"],
        "is_intelligent_adjusted": x["is_intelligent_adjusted"] if "is_intelligent_adjusted" in x else False
      }, applicable_rates)),
      "previous_rate": {
        "valid_from": applicable_rates[0]["valid_from"],
        "valid_to": applicable_rates[-1]["valid_to"],
        "value_inc_vat": applicable_rates[0]["value_inc_vat"],
      }
    }

  return None

def get_next_rate_information(rates, now: datetime):
  current_rate = None
  applicable_rates = []

  if rates is not None:
    for period in rates:
      if now >= period["valid_from"] and now <= period["valid_to"]:
        current_rate = period

      if current_rate is not None and current_rate["value_inc_vat"] != period["value_inc_vat"]:
        if len(applicable_rates) == 0 or period["value_inc_vat"] == applicable_rates[0]["value_inc_vat"]:
          applicable_rates.append(period)
        else:
          break

  if len(applicable_rates) > 0:
    return {
      "rates": list(map(lambda x: {
        "valid_from": x["valid_from"],
        "valid_to":   x["valid_to"],
        "value_inc_vat": x["value_inc_vat"],
        "is_capped": x["is_capped"],
        "is_intelligent_adjusted": x["is_intelligent_adjusted"] if "is_intelligent_adjusted" in x else False
      }, applicable_rates)),
      "next_rate": {
        "valid_from": applicable_rates[0]["valid_from"],
        "valid_to": applicable_rates[-1]["valid_to"],
        "value_inc_vat": applicable_rates[0]["value_inc_vat"],
      }
    }

  return None