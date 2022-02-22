# Adapted from https://www.theenergyshop.com/guides/how-to-convert-gas-units-to-kwh
def convert_kwh_to_m3(value):
  m3_value = value * 3.6 # kWh Conversion factor
  m3_value = m3_value / 40 # Calorific value
  return round(m3_value / 1.02264, 3) # Volume correction factor

# Adapted from https://www.theenergyshop.com/guides/how-to-convert-gas-units-to-kwh
def convert_m3_to_kwh(value):
  kwh_value = value * 1.02264 # Volume correction factor
  kwh_value = kwh_value * 40.0 # Calorific value
  return round(kwh_value / 3.6) # kWh Conversion factor

async def calculate_gas_cost(client, consumption_data, last_calculated_timestamp, period_from, period_to, sensor):
  if (consumption_data != None and len(consumption_data) > 0):

    # Only calculate our consumption if our data has changed
    if (last_calculated_timestamp < consumption_data[-1]["interval_end"]):
      rates = await client.async_get_gas_rates(sensor["tariff_code"], period_from, period_to)
      standard_charge_result = await client.async_get_gas_standing_charge(sensor["tariff_code"], period_from, period_to)

      if (rates != None and len(rates) > 0 and standard_charge_result != None):
        standard_charge = standard_charge_result["value_inc_vat"]

        charges = []
        total_cost_in_pence = 0
        for consumption in consumption_data:
          value = consumption["consumption"]

          if sensor["is_smets1_meter"] == False:
            value = convert_m3_to_kwh(value)

          consumption_from = consumption["interval_start"]
          consumption_to = consumption["interval_end"]

          try:
            rate = next(r for r in rates if r["valid_from"] == consumption_from and r["valid_to"] == consumption_to)
          except StopIteration:
            raise Exception(f"Failed to find rate for consumption between {consumption_from} and {consumption_to} for tariff {sensor['tariff_code']}")

          cost = (rate["value_inc_vat"] * value)
          total_cost_in_pence = total_cost_in_pence + cost

          charges.append({
            "From": rate["valid_from"],
            "To": rate["valid_to"],
            "Rate": f'{rate["value_inc_vat"]}p',
            "Consumption": f'{value} kWh',
            "Cost": f'£{round(cost / 100, 2)}'
          })
        
        total_cost = round(total_cost_in_pence / 100, 2)
        total_cost_plus_standing_charge = round((total_cost_in_pence + standard_charge) / 100, 2)
        last_calculated_timestamp = consumption_data[-1]["interval_end"]

        return {
          "standing_charge": standard_charge,
          "total_without_standing_charge": total_cost,
          "total": total_cost_plus_standing_charge,
          "last_calculated_timestamp": last_calculated_timestamp,
          "charges": charges
        }