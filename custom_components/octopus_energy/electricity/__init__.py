import datetime

from ..utils.conversions import value_inc_vat_to_pounds
from ..utils import get_off_peak_cost

def __get_to(item):
    return item["end"]

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_to)
  return sorted

def calculate_electricity_consumption_and_cost(
    current: datetime,
    consumption_data,
    rate_data,
    standing_charge,
    last_reset,
    tariff_code,
    minimum_consumption_records = 0,
    round_cost = True
  ):
  if (consumption_data is not None and len(consumption_data) >= minimum_consumption_records and rate_data is not None and len(rate_data) > 0 and standing_charge is not None):

    sorted_consumption_data = __sort_consumption(consumption_data)

    # Only calculate our consumption if our data has changed
    if (last_reset is None or last_reset < sorted_consumption_data[0]["start"]):

      charges = []
      total_cost_in_pence = 0
      total_consumption = 0

      off_peak_cost = get_off_peak_cost(current, rate_data)
      total_cost_off_peak = 0
      total_cost_peak = 0
      total_consumption_off_peak = 0
      total_consumption_peak = 0

      for consumption in sorted_consumption_data:
        consumption_value = consumption["consumption"]
        consumption_from = consumption["start"]
        consumption_to = consumption["end"]
        total_consumption = total_consumption + consumption_value

        try:
          rate = next(r for r in rate_data if r["start"] == consumption_from and r["end"] == consumption_to)
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
          "start": rate["start"],
          "end": rate["end"],
          "rate": value_inc_vat_to_pounds(value),
          "consumption": consumption_value,
          "cost": round(cost / 100, 2) if round_cost else cost / 100
        })
      
      total_cost = round(total_cost_in_pence / 100, 2) if round_cost else total_cost_in_pence / 100
      total_cost_plus_standing_charge = round((total_cost_in_pence + standing_charge) / 100, 2) if round_cost else (total_cost_in_pence + standing_charge) / 100

      last_reset = sorted_consumption_data[0]["start"] if len(sorted_consumption_data) > 0 else None
      last_calculated_timestamp = sorted_consumption_data[-1]["end"] if len(sorted_consumption_data) > 0 else None

      result = {
        "standing_charge": round(standing_charge / 100, 2) if round_cost else standing_charge / 100,
        "total_cost_without_standing_charge": total_cost,
        "total_cost": total_cost_plus_standing_charge,
        "total_consumption": total_consumption,
        "last_reset": last_reset,
        "last_evaluated": last_calculated_timestamp,
        "charges": charges
      }

      if off_peak_cost is not None:
        result["total_cost_off_peak"] = round(total_cost_off_peak / 100, 2) if round_cost else total_cost_off_peak / 100
        result["total_cost_peak"] = round(total_cost_peak / 100, 2) if round_cost else total_cost_peak / 100
        result["total_consumption_off_peak"] = total_consumption_off_peak
        result["total_consumption_peak"] = total_consumption_peak

      return result

def get_electricity_tariff_override_key(serial_number: str, mpan: str) -> str:
  return f'electricity_previous_consumption_tariff_{serial_number}_{mpan}'