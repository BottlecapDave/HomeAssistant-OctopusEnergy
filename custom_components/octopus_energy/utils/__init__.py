
import re
from datetime import datetime, timedelta

from homeassistant.util.dt import (as_local, as_utc, parse_datetime)

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

def get_tariff_parts(tariff_code: str) -> TariffParts:
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

class Tariff:
  product: str
  code: str

  def __init__(self, product: str, code: str):
    self.product = product
    self.code = code

def is_day_night_tariff(tariff_code: str) -> bool:
  tariff_parts = get_tariff_parts(tariff_code)
  return tariff_parts is not None and "2" in tariff_parts.rate

def get_active_tariff(utcnow: datetime, agreements):
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
    return Tariff(latest_agreement["product_code"], latest_agreement["tariff_code"])
  
  return None

def get_off_peak_cost(current: datetime, rates: list):
  # Need to use as local to ensure we get the correct from/to periods relative to our local time
  today_start = as_utc(as_local(current).replace(hour=0, minute=0, second=0, microsecond=0))
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

class OffPeakTime:
  start: datetime
  end: datetime

  def __init__(self, start, end):
    self.start = start
    self.end = end

def get_off_peak_times(current: datetime, rates: list, include_intelligent_adjusted = False):
  off_peak_value = get_off_peak_cost(current, rates)
  times: list[OffPeakTime] = []

  if rates is not None and off_peak_value is not None:
    start = None
    rates_length = len(rates)
    for rate_index in range(rates_length):
      rate = rates[rate_index]
      if (rate["value_inc_vat"] == off_peak_value and 
          ("is_intelligent_adjusted" not in rate or rate["is_intelligent_adjusted"] == False or include_intelligent_adjusted)):
        if start is None:
          start = rate["start"]
      elif start is not None:
        end = rates[rate_index - 1]["end"]
        if end >= current:
          times.append(OffPeakTime(start, end))
        start = None
    
    if start is not None:
      end = rates[-1]["end"]
      if end >= current:
        times.append(OffPeakTime(start, end))

  return times

def private_rates_to_public_rates(rates: list):
  if rates is None:
    return None

  new_rates = []

  for rate in rates:
    new_rate = {
      "start": as_local(rate["start"]),
      "end": as_local(rate["end"]),
      "value_inc_vat": value_inc_vat_to_pounds(rate["value_inc_vat"])
    }

    if "is_capped" in rate:
      new_rate["is_capped"] = rate["is_capped"]
      
    if "is_intelligent_adjusted" in rate:
      new_rate["is_intelligent_adjusted"] = rate["is_intelligent_adjusted"]

    new_rates.append(new_rate)

  return new_rates
