from datetime import (datetime, timedelta)

from ..api_client import OctopusEnergyApiClient

def __get_interval_end(item):
    return item["interval_end"]

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_interval_end)
  return sorted

minimum_consumption_records = 2

def calculate_electricity_consumption(consumption_data, last_reset):
  if (consumption_data != None and len(consumption_data) > minimum_consumption_records):

    sorted_consumption_data = __sort_consumption(consumption_data)

    if (last_reset == None or last_reset < sorted_consumption_data[0]["interval_start"]):
      total = 0

      consumption_parts = []
      for consumption in sorted_consumption_data:
        total = total + consumption["consumption"]

        current_consumption = consumption["consumption"]

        consumption_parts.append({
          "from": consumption["interval_start"],
          "to": consumption["interval_end"],
          "consumption": current_consumption,
        })
      
      last_reset = sorted_consumption_data[0]["interval_start"]
      last_calculated_timestamp = sorted_consumption_data[-1]["interval_end"]

      return {
        "total": total,
        "last_reset": last_reset,
        "last_calculated_timestamp": last_calculated_timestamp,
        "consumptions": consumption_parts
      }

async def async_calculate_electricity_cost(client: OctopusEnergyApiClient, consumption_data, last_reset, period_from, period_to, tariff_code, is_smart_meter):
  if (consumption_data != None and len(consumption_data) > minimum_consumption_records):

    sorted_consumption_data = __sort_consumption(consumption_data)

    # Only calculate our consumption if our data has changed
    if (last_reset is None or last_reset < sorted_consumption_data[-1]["interval_end"]):
      rates = await client.async_get_electricity_rates(tariff_code, is_smart_meter, period_from, period_to)
      standard_charge_result = await client.async_get_electricity_standing_charge(tariff_code, period_from, period_to)

      if (rates is not None and len(rates) > 0 and standard_charge_result is not None):
        standard_charge = standard_charge_result["value_inc_vat"]

        charges = []
        total_cost_in_pence = 0
        rate_charges = {}
        for consumption in sorted_consumption_data:
          consumption_value = consumption["consumption"]
          consumption_from = consumption["interval_start"]
          consumption_to = consumption["interval_end"]

          try:
            rate = next(r for r in rates if r["valid_from"] == consumption_from and r["valid_to"] == consumption_to)
          except StopIteration:
            raise Exception(f"Failed to find rate for consumption between {consumption_from} and {consumption_to} for tariff {tariff_code}")

          value = rate["value_inc_vat"]
          cost = (value * consumption_value)
          total_cost_in_pence = total_cost_in_pence + cost

          rate_charges[value] = (rate_charges[value] if value in rate_charges else 0) + cost

          charges.append({
            "from": rate["valid_from"],
            "to": rate["valid_to"],
            "rate": f'{value}p',
            "consumption": f'{consumption_value} kWh',
            "cost": f'£{round(cost / 100, 2)}'
          })
        
        total_cost = round(total_cost_in_pence / 100, 2)
        total_cost_plus_standing_charge = round((total_cost_in_pence + standard_charge) / 100, 2)

        last_reset = sorted_consumption_data[0]["interval_start"]
        last_calculated_timestamp = sorted_consumption_data[-1]["interval_end"]

        result = {
          "standing_charge": standard_charge,
          "total_without_standing_charge": total_cost,
          "total": total_cost_plus_standing_charge,
          "last_reset": last_reset,
          "last_calculated_timestamp": last_calculated_timestamp,
          "charges": charges
        }

        if len(rate_charges) == 2:
          key_one = list(rate_charges.keys())[0]
          key_two = list(rate_charges.keys())[1]

          if (rate_charges[key_one] < rate_charges[key_two]):
            result["total_off_peak"] = round(rate_charges[key_one] / 100, 2)
            result["total_peak"] = round(rate_charges[key_two] / 100, 2)
          else:
            result["total_off_peak"] = round(rate_charges[key_two] / 100, 2)
            result["total_peak"] = round(rate_charges[key_one] / 100, 2)

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
        "is_capped": x["is_capped"]
      }, rates)),
      "current_rate": current_rate,
      "min_rate_today": min_rate_value,
      "max_rate_today": max_rate_value,
      "average_rate_today": total_rate_value / total_rates
    }

  return None
