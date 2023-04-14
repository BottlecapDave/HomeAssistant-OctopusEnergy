from ..api_client import OctopusEnergyApiClient

minimum_consumption_records = 2

def __get_interval_end(item):
    return item["interval_end"]

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_interval_end)
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

def calculate_gas_consumption(consumption_data, last_calculated_timestamp, consumption_units, calorific_value):
  if (consumption_data != None and len(consumption_data) > minimum_consumption_records):

    sorted_consumption_data = __sort_consumption(consumption_data)

    if (last_calculated_timestamp == None or last_calculated_timestamp < sorted_consumption_data[-1]["interval_end"]):
      total_m3 = 0
      total_kwh = 0

      consumption_parts = []
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

        total_m3 = total_m3 + current_consumption_m3
        total_kwh = total_kwh + current_consumption_kwh

        consumption_parts.append({
          "from": consumption["interval_start"],
          "to": consumption["interval_end"],
          "consumption_m3": current_consumption_m3,
          "consumption_kwh": current_consumption_kwh,
        })
      
      last_calculated_timestamp = sorted_consumption_data[-1]["interval_end"]

      return {
        "total_m3": round(total_m3, 3),
        "total_kwh": round(total_kwh, 3),
        "last_calculated_timestamp": last_calculated_timestamp,
        "consumptions": consumption_parts
      }
      
async def async_calculate_gas_cost(client: OctopusEnergyApiClient, consumption_data, last_calculated_timestamp, period_from, period_to, sensor, consumption_units, calorific_value):
  if (consumption_data != None and len(consumption_data) > minimum_consumption_records):

    sorted_consumption_data = __sort_consumption(consumption_data)

    # Only calculate our consumption if our data has changed
    if (last_calculated_timestamp == None or last_calculated_timestamp < sorted_consumption_data[-1]["interval_end"]):
      rates = await client.async_get_gas_rates(sensor["tariff_code"], period_from, period_to)
      standard_charge_result = await client.async_get_gas_standing_charge(sensor["tariff_code"], period_from, period_to)

      if (rates != None and len(rates) > 0 and standard_charge_result != None):
        standard_charge = standard_charge_result["value_inc_vat"]

        charges = []
        total_cost_in_pence = 0
        for consumption in sorted_consumption_data:
          value = consumption["consumption"]

          if consumption_units == "m³":
            value = convert_m3_to_kwh(value, calorific_value)

          consumption_from = consumption["interval_start"]
          consumption_to = consumption["interval_end"]

          try:
            rate = next(r for r in rates if r["valid_from"] == consumption_from and r["valid_to"] == consumption_to)
          except StopIteration:
            raise Exception(f"Failed to find rate for consumption between {consumption_from} and {consumption_to} for tariff {sensor['tariff_code']}")

          cost = (rate["value_inc_vat"] * value)
          total_cost_in_pence = total_cost_in_pence + cost

          charges.append({
            "from": rate["valid_from"],
            "to": rate["valid_to"],
            "rate": f'{rate["value_inc_vat"]}p',
            "consumption": f'{value} kWh',
            "cost": f'£{round(cost / 100, 2)}'
          })
        
        total_cost = round(total_cost_in_pence / 100, 2)
        total_cost_plus_standing_charge = round((total_cost_in_pence + standard_charge) / 100, 2)
        last_calculated_timestamp = sorted_consumption_data[-1]["interval_end"]

        return {
          "standing_charge": standard_charge,
          "total_without_standing_charge": total_cost,
          "total": total_cost_plus_standing_charge,
          "last_calculated_timestamp": last_calculated_timestamp,
          "charges": charges
        }