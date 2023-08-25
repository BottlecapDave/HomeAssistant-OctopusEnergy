from datetime import datetime, timedelta
from homeassistant.util.dt import (as_utc, parse_datetime)

import re

from ..const import (
  REGEX_TARIFF_PARTS,
)

class TariffParts:
  energy: str
  rate: str
  product_code: str
  region: str

  def __init__(self, energy: str, rate: str, product_code: str, region: str):
    self.energy = energy
    self.rate = rate
    self.product_code = product_code
    self.region = region

def get_tariff_parts(tariff_code) -> TariffParts:
  matches = re.search(REGEX_TARIFF_PARTS, tariff_code)
  if matches is None:
    return None
  
  # If our energy or rate isn't extracted, then assume is electricity and "single" rate as that's 
  # where our experimental tariffs are
  energy = matches.groupdict()["energy"] or "E"
  rate = matches.groupdict()["rate"] or "1R"
  product_code =matches.groupdict()["product_code"]
  region = matches.groupdict()["region"]

  return TariffParts(energy, rate, product_code, region)

def get_active_tariff_code(utcnow: datetime, agreements):
  latest_agreement = None
  latest_valid_from = None
  next_agreement = None

  # Find our latest agreement
  for agreement in agreements:
    if agreement["tariff_code"] is None:
      continue

    valid_from = as_utc(parse_datetime(agreement["valid_from"]))

    # Keep track of the next agreement in case we can't find an active one
    next_valid_from = as_utc(parse_datetime(next_agreement["valid_from"])) if next_agreement is not None else None
    if (utcnow < valid_from and (next_valid_from is None or valid_from < next_valid_from)):
      next_agreement = agreement

    if utcnow >= valid_from and (latest_valid_from is None or valid_from > latest_valid_from):

      latest_valid_to = None
      if "valid_to" in agreement and agreement["valid_to"] is not None:
        latest_valid_to = as_utc(parse_datetime(agreement["valid_to"]))

      if latest_valid_to is None or latest_valid_to >= utcnow:
        latest_agreement = agreement
        latest_valid_from = valid_from

  if latest_agreement is not None:
    return latest_agreement["tariff_code"]
  elif next_agreement is not None:
    return next_agreement["tariff_code"]
  
  return None

def get_off_peak_cost(rates):
  off_peak_cost = None

  rate_charges = {}
  for rate in rates:
    value = rate["value_inc_vat"]
    rate_charges[value] = (rate_charges[value] if value in rate_charges else value)
    if off_peak_cost is None or off_peak_cost > rate["value_inc_vat"]:
      off_peak_cost = rate["value_inc_vat"]

  return off_peak_cost if len(rate_charges) == 2 else None