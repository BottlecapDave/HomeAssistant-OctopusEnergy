from ..utils.conversions import value_inc_vat_to_pounds

def __get_to(item):
    return item["end"]

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_to)
  return sorted

# Adapted from https://www.theenergyshop.com/guides/how-to-convert-gas-units-to-kwh
def convert_m3_to_kwh(value, calorific_value):
  kwh_value = value * 1.02264 # Volume correction factor
  kwh_value = kwh_value * calorific_value # Calorific value
  return round(kwh_value / 3.6, 3) # kWh Conversion factor

# Adapted from https://www.theenergyshop.com/guides/how-to-convert-gas-units-to-kwh
def convert_kwh_to_m3(value, calorific_value):
  m3_value = value * 3.6 # kWh Conversion factor
  m3_value = m3_value / calorific_value # Calorific value
  return round(m3_value / 1.02264, 3) # Volume correction factor
      
def calculate_gas_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    last_reset,
    consumption_units,
    calorific_value
  ):
  if (consumption_data is not None and len(consumption_data) > 0 and rate_data is not None and len(rate_data) > 0 and standing_charge is not None):

    sorted_consumption_data = __sort_consumption(consumption_data)

    # Only calculate our consumption if our data has changed
    if (last_reset == None or last_reset < sorted_consumption_data[0]["start"]):

      charges = []
      total_cost_in_pence = 0
      total_consumption_m3 = 0
      total_consumption_kwh = 0
      for consumption in sorted_consumption_data:
        current_consumption_m3 = 0
        current_consumption_kwh = 0

        current_consumption = consumption["consumption"]
        
        if consumption_units == "m³":
          current_consumption_m3 = current_consumption
          current_consumption_kwh = convert_m3_to_kwh(current_consumption, calorific_value)
        else:
          current_consumption_m3 = convert_kwh_to_m3(current_consumption, calorific_value)
          current_consumption_kwh = current_consumption

        total_consumption_m3 = total_consumption_m3 + current_consumption_m3
        total_consumption_kwh = total_consumption_kwh + current_consumption_kwh

        consumption_from = consumption["start"]
        consumption_to = consumption["end"]

        try:
          rate = next(r for r in rate_data if r["start"] == consumption_from and r["end"] == consumption_to)
        except StopIteration:
          raise Exception(f"Failed to find rate for consumption between {consumption_from} and {consumption_to}")

        value = rate["value_inc_vat"]
        cost = (value * current_consumption_kwh)
        total_cost_in_pence = total_cost_in_pence + cost

        charges.append({
          "start": rate["start"],
          "end": rate["end"],
          "rate": value_inc_vat_to_pounds(value),
          "consumption_m3": current_consumption_m3,
          "consumption_kwh": current_consumption_kwh,
          "cost": round(cost / 100, 2)
        })
      
      total_cost = round(total_cost_in_pence / 100, 2)
      total_cost_plus_standing_charge = round((total_cost_in_pence + standing_charge) / 100, 2)
      last_reset = sorted_consumption_data[0]["start"]
      last_calculated_timestamp = sorted_consumption_data[-1]["end"]

      return {
        "standing_charge": round(standing_charge / 100, 2),
        "total_cost_without_standing_charge": total_cost,
        "total_cost": total_cost_plus_standing_charge,
        "total_consumption_m3": total_consumption_m3,
        "total_consumption_kwh": total_consumption_kwh,
        "last_reset": last_reset,
        "last_evaluated": last_calculated_timestamp,
        "charges": charges
      }
    
def get_gas_tariff_override_key(serial_number: str, mprn: str) -> str:
  return f'gas_previous_consumption_tariff_{serial_number}_{mprn}'