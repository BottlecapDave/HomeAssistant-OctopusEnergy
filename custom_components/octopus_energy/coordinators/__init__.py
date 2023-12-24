from datetime import datetime, timedelta
import logging
from typing import Callable, Any
from custom_components.octopus_energy.utils.requests import calculate_next_refresh

from homeassistant.helpers import issue_registry as ir
from homeassistant.util.dt import (as_utc)

from ..const import (
  DOMAIN,
)

from ..api_client import OctopusEnergyApiClient

from ..utils import (
  get_active_tariff_code,
  get_tariff_parts
)

from ..const import (
  DOMAIN,
  DATA_KNOWN_TARIFF,
)

_LOGGER = logging.getLogger(__name__)

class BaseCoordinatorResult:
  last_retrieved: datetime
  next_refresh: datetime
  request_attempts: int
  refresh_rate_in_minutes: int

  def __init__(self, last_retrieved: datetime, request_attempts: int, refresh_rate_in_minutes: int):
    self.last_retrieved = last_retrieved
    self.request_attempts = request_attempts
    self.next_refresh = calculate_next_refresh(last_retrieved, request_attempts, refresh_rate_in_minutes)
    _LOGGER.debug(f'last_retrieved: {last_retrieved}; request_attempts: {request_attempts}; refresh_rate_in_minutes: {refresh_rate_in_minutes}; next_refresh: {self.next_refresh}')

async def async_check_valid_tariff(hass, client: OctopusEnergyApiClient, tariff_code: str, is_electricity: bool):
  tariff_key = f'{DATA_KNOWN_TARIFF}_{tariff_code}'
  if (tariff_key not in hass.data[DOMAIN]):
    tariff_parts = get_tariff_parts(tariff_code)
    if tariff_parts is None:
      ir.async_create_issue(
        hass,
        DOMAIN,
        f"unknown_tariff_format_{tariff_code}",
        is_fixable=False,
        severity=ir.IssueSeverity.ERROR,
        learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/unknown_tariff_format",
        translation_key="unknown_tariff_format",
        translation_placeholders={ "type": "Electricity" if is_electricity else "Gas", "tariff_code": tariff_code },
      )
    else:
      try:
        _LOGGER.debug(f"Retrieving product information for '{tariff_parts.product_code}'")
        product = await client.async_get_product(tariff_parts.product_code)
        if product is None:
          ir.async_create_issue(
            hass,
            DOMAIN,
            f"unknown_tariff_{tariff_code}",
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/unknown_tariff",
            translation_key="unknown_tariff",
            translation_placeholders={ "type": "Electricity" if is_electricity else "Gas", "tariff_code": tariff_code },
          )
        else:
          hass.data[DOMAIN][tariff_key] = True
      except:
        _LOGGER.debug(f"Failed to retrieve product info for '{tariff_parts.product_code}'")

def __raise_rate_event(event_key: str,
                       rates: list,
                       additional_attributes: "dict[str, Any]",
                       fire_event: Callable[[str, "dict[str, Any]"], None]):
  
  min_rate = None
  max_rate = None
  average_rate = 0
  for rate in rates:
    if min_rate is None or min_rate > rate["value_inc_vat"]:
      min_rate = rate["value_inc_vat"]

    if max_rate is None or max_rate < rate["value_inc_vat"]:
      max_rate = rate["value_inc_vat"]

    average_rate += rate["value_inc_vat"]

  print(average_rate)
  event_data = { "rates": rates, "min_rate": min_rate, "max_rate": max_rate, "average_rate": average_rate / len(rates) }
  event_data.update(additional_attributes)
  fire_event(event_key, event_data)

def raise_rate_events(now: datetime,
                      rates: list, 
                      additional_attributes: "dict[str, Any]",
                      fire_event: Callable[[str, "dict[str, Any]"], None],
                      previous_event_key: str,
                      current_event_key: str,
                      next_event_key: str):
  
  today_start = as_utc(now.replace(hour=0, minute=0, second=0, microsecond=0))
  today_end = today_start + timedelta(days=1)

  previous_rates = []
  current_rates = []
  next_rates = []

  for rate in rates:
    if (rate["start"] < today_start):
      previous_rates.append(rate)
    elif (rate["start"] >= today_end):
      next_rates.append(rate)
    else:
      current_rates.append(rate)

  __raise_rate_event(previous_event_key, previous_rates, additional_attributes, fire_event)
  __raise_rate_event(current_event_key, current_rates, additional_attributes, fire_event)
  __raise_rate_event(next_event_key, next_rates, additional_attributes, fire_event)

def get_electricity_meter_tariff_code(current: datetime, account_info, target_mpan: str, target_serial_number: str):
  if len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff_code = get_active_tariff_code(current, point["agreements"])
      # The type of meter (ie smart vs dumb) can change the tariff behaviour, so we
      # have to enumerate the different meters being used for each tariff as well.
      for meter in point["meters"]:
        if active_tariff_code is not None and point["mpan"] == target_mpan and meter["serial_number"] == target_serial_number:
           return active_tariff_code
           
  return None

def get_gas_meter_tariff_code(current: datetime, account_info, target_mprn: str, target_serial_number: str):
  if len(account_info["gas_meter_points"]) > 0:
    for point in account_info["gas_meter_points"]:
      active_tariff_code = get_active_tariff_code(current, point["agreements"])
      for meter in point["meters"]:
        if active_tariff_code is not None and point["mprn"] == target_mprn and meter["serial_number"] == target_serial_number:
           return active_tariff_code
           
  return None