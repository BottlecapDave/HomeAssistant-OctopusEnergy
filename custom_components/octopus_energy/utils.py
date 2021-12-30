from homeassistant.util.dt import (utcnow, as_utc, parse_datetime)

import re

from .const import (
  REGEX_TARIFF_PARTS
)

def get_tariff_parts(tariff_code):
  matches = re.search(REGEX_TARIFF_PARTS, tariff_code)
  if matches == None:
    raise Exception(f'Unable to extract product code from tariff code: {tariff_code}')

  # According to https://www.guylipman.com/octopus/api_guide.html#s1b, this part should indicate if we're dealing
  # with standard rates or day/night rates
  energy = matches[1]
  rate = matches[2]
  product_code = matches[3]
  region = matches[4]

  return {
    "energy": energy,
    "rate": rate,
    "product_code": product_code,
    "region": region
  }

def get_active_tariff_code(agreements):
  now = utcnow()

  latest_agreement = None
  latest_valid_from = None

  # Find our latest agreement
  for agreement in agreements:
    valid_from = as_utc(parse_datetime(agreement["valid_from"]))

    if latest_valid_from == None or valid_from > latest_valid_from:
      latest_agreement = agreement
      latest_valid_from = valid_from

  if latest_agreement != None:
    now = utcnow()

    latest_valid_to = None
    if "valid_to" in latest_agreement and latest_agreement["valid_to"] != None:
      latest_valid_to = as_utc(parse_datetime(latest_agreement["valid_to"]))

    # If there is no end for our latest agreement, then it is our most active
    if latest_valid_to == None or latest_valid_to >= now:
      return latest_agreement["tariff_code"]
  
  return None

# Adapted from https://www.theenergyshop.com/guides/how-to-convert-gas-units-to-kwh
def convert_kwh_to_m3(value):
  m3_value = value * 3.6 # kWh Conversion factor
  m3_value = m3_value / 40 # Calorific value
  return round(m3_value / 1.02264, 3) # Volume correction factor