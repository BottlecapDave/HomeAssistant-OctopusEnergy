
import re
from datetime import datetime, timedelta


from homeassistant.util.dt import (as_utc, parse_datetime)

from ..const import (
  REGEX_TARIFF_PARTS,
)
from ..utils.conversions import value_inc_vat_to_pounds
from .rate_information import get_current_rate_information

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

  # Find our latest agreement
  for agreement in agreements:
    if agreement["tariff_code"] is None:
      continue

    valid_from = as_utc(parse_datetime(agreement["start"]))

    if utcnow >= valid_from and (latest_valid_from is None or valid_from > latest_valid_from):

      latest_valid_to = None
      if "end" in agreement and agreement["end"] is not None:
        latest_valid_to = as_utc(parse_datetime(agreement["end"]))

      if latest_valid_to is None or latest_valid_to >= utcnow:
        latest_agreement = agreement
        latest_valid_from = valid_from

  if latest_agreement is not None:
    return latest_agreement["tariff_code"]
  
  return None

def get_off_peak_cost(current: datetime, rates: list):
  today_start = as_utc(current.replace(hour=0, minute=0, second=0, microsecond=0))
  today_end = today_start + timedelta(days=1)
  off_peak_cost = None

  rate_charges = {}
  if rates is not None:
    for rate in rates:
      if rate["start"] >= today_start and rate["end"] <= today_end:
        value = rate["value_inc_vat"]
        rate_charges[value] = (rate_charges[value] if value in rate_charges else value)
        if off_peak_cost is None or off_peak_cost > rate["value_inc_vat"]:
          off_peak_cost = rate["value_inc_vat"]

  return off_peak_cost if len(rate_charges) == 2 or len(rate_charges) == 3 else None

def is_off_peak(current: datetime, rates):
  off_peak_value = get_off_peak_cost(current, rates)

  rate_information = get_current_rate_information(rates, current)

  return (off_peak_value is not None and 
          rate_information is not None and 
          rate_information["current_rate"]["is_intelligent_adjusted"] == False and 
          value_inc_vat_to_pounds(off_peak_value) == rate_information["current_rate"]["value_inc_vat"])

def private_rates_to_public_rates(rates: list):
  if rates is None:
    return None

  new_rates = []

  for rate in rates:
    new_rate = {
      "start": rate["start"],
      "end": rate["end"],
      "value_inc_vat": value_inc_vat_to_pounds(rate["value_inc_vat"])
    }

    if "is_capped" in rate:
      new_rate["is_capped"] = rate["is_capped"]
      
    if "is_intelligent_adjusted" in rate:
      new_rate["is_intelligent_adjusted"] = rate["is_intelligent_adjusted"]

    new_rates.append(new_rate)

  return new_rates
