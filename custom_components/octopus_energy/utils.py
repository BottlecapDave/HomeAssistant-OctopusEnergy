from datetime import datetime, timedelta
from homeassistant.util.dt import (as_utc, parse_datetime)

import re

from .const import (
  REGEX_TARIFF_PARTS,
)

def get_tariff_parts(tariff_code):
  matches = re.search(REGEX_TARIFF_PARTS, tariff_code)
  if matches is None:
    return None
  
  # If our energy or rate isn't extracted, then assume is electricity and "single" rate as that's 
  # where our experimental tariffs are
  energy = matches.groupdict()["energy"] or "E"
  rate = matches.groupdict()["rate"] or "1R"
  product_code =matches.groupdict()["product_code"]
  region = matches.groupdict()["region"]

  return {
    "energy": energy,
    "rate": rate,
    "product_code": product_code,
    "region": region
  }

def get_active_tariff_code(utcnow: datetime, agreements):
  latest_agreement = None
  latest_valid_from = None

  # Find our latest agreement
  for agreement in agreements:
    if agreement["tariff_code"] is None:
      continue

    valid_from = as_utc(parse_datetime(agreement["valid_from"]))

    if utcnow >= valid_from and (latest_valid_from is None or valid_from > latest_valid_from):

      latest_valid_to = None
      if "valid_to" in agreement and agreement["valid_to"] is not None:
        latest_valid_to = as_utc(parse_datetime(agreement["valid_to"]))

      if latest_valid_to is None or latest_valid_to >= utcnow:
        latest_agreement = agreement
        latest_valid_from = valid_from

  if latest_agreement is not None:
    return latest_agreement["tariff_code"]
  
  return None

def get_valid_from(rate):
  return rate["valid_from"]
    
def rates_to_thirty_minute_increments(data, period_from: datetime, period_to: datetime, tariff_code: str, price_cap: float = None):
  """Process the collection of rates to ensure they're in 30 minute periods"""
  starting_period_from = period_from
  results = []
  if ("results" in data):
    items = data["results"]
    items.sort(key=get_valid_from)

    # We need to normalise our data into 30 minute increments so that all of our rates across all tariffs are the same and it's 
    # easier to calculate our target rate sensors
    for item in items:
      value_inc_vat = float(item["value_inc_vat"])

      is_capped = False
      if (price_cap is not None and value_inc_vat > price_cap):
        value_inc_vat = price_cap
        is_capped = True

      if "valid_from" in item and item["valid_from"] is not None:
        valid_from = as_utc(parse_datetime(item["valid_from"]))

        # If we're on a fixed rate, then our current time could be in the past so we should go from
        # our target period from date otherwise we could be adjusting times quite far in the past
        if (valid_from < starting_period_from):
          valid_from = starting_period_from
      else:
        valid_from = starting_period_from

      # Some rates don't have end dates, so we should treat this as our period to target
      if "valid_to" in item and item["valid_to"] is not None:
        target_date = as_utc(parse_datetime(item["valid_to"]))

        # Cap our target date to our end period
        if (target_date > period_to):
          target_date = period_to
      else:
        target_date = period_to
      
      while valid_from < target_date:
        valid_to = valid_from + timedelta(minutes=30)
        results.append({
          "value_inc_vat": value_inc_vat,
          "valid_from": valid_from,
          "valid_to": valid_to,
          "tariff_code": tariff_code,
          "is_capped": is_capped
        })

        valid_from = valid_to
        starting_period_from = valid_to
    
  return results

def get_off_peak_cost(rates):
  off_peak_cost = None

  rate_charges = {}
  for rate in rates:
    value = rate["value_inc_vat"]
    rate_charges[value] = (rate_charges[value] if value in rate_charges else value)
    if off_peak_cost is None or off_peak_cost > rate["value_inc_vat"]:
      off_peak_cost = rate["value_inc_vat"]

  return off_peak_cost if len(rate_charges) == 2 else None