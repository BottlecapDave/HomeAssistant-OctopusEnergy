from datetime import (datetime, timedelta)

from ..utils import get_off_peak_cost

def __get_interval_end(item):
    return item["interval_end"]

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_interval_end)
  return sorted

minimum_consumption_records = 2

async def async_calculate_electricity_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    last_reset,
    tariff_code
  ):
  if (consumption_data is not None and len(consumption_data) > minimum_consumption_records and rate_data is not None and len(rate_data) > 0 and standing_charge is not None):

    sorted_consumption_data = __sort_consumption(consumption_data)

    # Only calculate our consumption if our data has changed
    if (last_reset is None or last_reset < sorted_consumption_data[0]["interval_start"]):

      charges = []
      total_cost_in_pence = 0
      total_consumption = 0

      off_peak_cost = get_off_peak_cost(rate_data)
      total_cost_off_peak = 0
      total_cost_peak = 0
      total_consumption_off_peak = 0
      total_consumption_peak = 0

      for consumption in sorted_consumption_data:
        consumption_value = consumption["consumption"]
        consumption_from = consumption["interval_start"]
        consumption_to = consumption["interval_end"]
        total_consumption = total_consumption + consumption_value

        try:
          rate = next(r for r in rate_data if r["valid_from"] == consumption_from and r["valid_to"] == consumption_to)
        except StopIteration:
          raise Exception(f"Failed to find rate for consumption between {consumption_from} and {consumption_to} for tariff {tariff_code}")

        value = rate["value_inc_vat"]
        cost = (value * consumption_value)
        total_cost_in_pence = total_cost_in_pence + cost

        if value == off_peak_cost:
          total_consumption_off_peak = total_consumption_off_peak + consumption_value
          total_cost_off_peak = total_cost_off_peak + cost
        else:
          total_consumption_peak = total_consumption_peak + consumption_value
          total_cost_peak = total_cost_peak + cost

        charges.append({
          "from": rate["valid_from"],
          "to": rate["valid_to"],
          "rate": value,
          "consumption": consumption_value,
          "cost": f'£{round(cost / 100, 2)}'
        })
      
      total_cost = round(total_cost_in_pence / 100, 2)
      total_cost_plus_standing_charge = round((total_cost_in_pence + standing_charge) / 100, 2)

      last_reset = sorted_consumption_data[0]["interval_start"]
      last_calculated_timestamp = sorted_consumption_data[-1]["interval_end"]

      result = {
        "standing_charge": standing_charge,
        "total_cost_without_standing_charge": total_cost,
        "total_cost": total_cost_plus_standing_charge,
        "total_consumption": total_consumption,
        "last_reset": last_reset,
        "last_calculated_timestamp": last_calculated_timestamp,
        "charges": charges
      }

      if off_peak_cost is not None:
        result["total_cost_off_peak"] = round(total_cost_off_peak / 100, 2)
        result["total_cost_peak"] = round(total_cost_peak / 100, 2)
        result["total_consumption_off_peak"] = total_consumption_off_peak
        result["total_consumption_peak"] = total_consumption_peak

      return result
      
def get_rate_information(rates, target: datetime):
  min_target = target.replace(hour=0, minute=0, second=0, microsecond=0)
  max_target = min_target + timedelta(days=1)

  min_rate_value = None
  max_rate_value = None
  total_rate_value = 0
  total_rates = 0
  current_rate = None

  if rates is not None:
    for period in rates:
      if target >= period["valid_from"] and target <= period["valid_to"]:
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
        "from": x["valid_from"],
        "to":   x["valid_to"],
        "rate": x["value_inc_vat"],
        "is_capped": x["is_capped"],
        "is_intelligent_adjusted": x["is_intelligent_adjusted"] if "is_intelligent_adjusted" in x else False
      }, rates)),
      "current_rate": current_rate,
      "min_rate_today": min_rate_value,
      "max_rate_today": max_rate_value,
      "average_rate_today": total_rate_value / total_rates
    }

  return None

def get_electricity_tariff_override_key(serial_number: str, mpan: str) -> str:
  return f'electricity_previous_consumption_tariff_{serial_number}_{mpan}'