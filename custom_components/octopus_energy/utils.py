from datetime import timedelta
from homeassistant.util.dt import (as_utc, parse_datetime)

import re

from .const import (
  REGEX_TARIFF_PARTS,
  REGEX_OFFSET_PARTS,
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

def get_active_tariff_code(utcnow, agreements):
  latest_agreement = None
  latest_valid_from = None

  # Find our latest agreement
  for agreement in agreements:
    valid_from = as_utc(parse_datetime(agreement["valid_from"]))

    if utcnow >= valid_from and (latest_valid_from == None or valid_from > latest_valid_from):

      latest_valid_to = None
      if "valid_to" in agreement and agreement["valid_to"] != None:
        latest_valid_to = as_utc(parse_datetime(agreement["valid_to"]))

      if latest_valid_to == None or latest_valid_to >= utcnow:
        latest_agreement = agreement
        latest_valid_from = valid_from

  if latest_agreement != None:
    return latest_agreement["tariff_code"]
  
  return None

def apply_offset(date_time, offset, inverse = False):
  matches = re.search(REGEX_OFFSET_PARTS, offset)
  if matches == None:
    raise Exception(f'Unable to extract offset: {offset}')

  symbol = matches[1]
  hours = float(matches[2])
  minutes = float(matches[3])
  seconds = float(matches[4])

  if ((symbol == "-" and inverse == False) or (symbol != "-" and inverse == True)):
    return date_time - timedelta(hours=hours, minutes=minutes, seconds=seconds)
  
  return date_time + timedelta(hours=hours, minutes=minutes, seconds=seconds)
    