from homeassistant.util.dt import (utcnow, as_utc, parse_datetime)

def get_active_agreement(agreements):
  now = utcnow()

  for agreement in agreements:
    
    valid_from = as_utc(parse_datetime(agreement["valid_from"]))
    
    valid_to = None
    if "valid_to" in agreement and agreement["valid_to"] != None:
      valid_to = as_utc(parse_datetime(agreement["valid_to"]))
    
    # Some agreements have no end date, which means they are still active with no end in sight
    if valid_from <= now and (valid_to == None or valid_to >= now):
      return agreement
  
  return None

# Adapted from https://www.theenergyshop.com/guides/how-to-convert-gas-units-to-kwh
def convert_kwh_to_m3(value):
  m3_value = value * 3.6 # kWh Conversion factor
  m3_value = m3_value / 40 # Calorific value
  return m3_value / 1.02264 # Volume correction factor