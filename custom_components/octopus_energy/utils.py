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

async def async_get_active_tariff_code(agreements, client):
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
    tariff_parts = get_tariff_parts(latest_agreement["tariff_code"])

    latest_valid_to = None
    if "valid_to" in latest_agreement and latest_agreement["valid_to"] != None:
      latest_valid_to = as_utc(parse_datetime(latest_agreement["valid_to"]))

    # If there is no end for our latest agreement, then it is our most active
    if latest_valid_to == None or latest_valid_to >= now:
      return latest_agreement["tariff_code"]
      
    # If our latest agreement was a fixed rate and is in the past, then we must have moved into a variable rate
    # (according to Octopus support), therefore we need to find the latest variable rate that
    if latest_valid_to < now and "FIX" in tariff_parts["product_code"]:
      products = await client.async_get_products(True)

      variable_product = None
      for product in products:
        available_from = as_utc(parse_datetime(product["available_from"]))
        if product["code"].startswith("VAR") and (variable_product == None or available_from < now):
          variable_product = product

      if variable_product != None:
        return f'{tariff_parts["energy"]}-{tariff_parts["rate"]}-{variable_product["code"]}-{tariff_parts["region"]}'
  
  return None

# Adapted from https://www.theenergyshop.com/guides/how-to-convert-gas-units-to-kwh
def convert_kwh_to_m3(value):
  m3_value = value * 3.6 # kWh Conversion factor
  m3_value = m3_value / 40 # Calorific value
  return round(m3_value / 1.02264, 3) # Volume correction factor