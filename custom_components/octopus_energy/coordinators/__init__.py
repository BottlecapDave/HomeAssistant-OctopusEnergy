from datetime import datetime, timedelta
import logging
from typing import Callable, Any

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
        learn_more_url="https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/blob/develop/_docs/repairs/unknown_tariff_format.md",
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
            learn_more_url="https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/blob/develop/_docs/repairs/unknown_tariff.md",
            translation_key="unknown_tariff",
            translation_placeholders={ "type": "Electricity" if is_electricity else "Gas", "tariff_code": tariff_code },
          )
        else:
          hass.data[DOMAIN][tariff_key] = True
      except:
        _LOGGER.debug(f"Failed to retrieve product info for '{tariff_parts.product_code}'")

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
    if (rate["valid_from"] < today_start):
      previous_rates.append(rate)
    elif (rate["valid_from"] >= today_end):
      next_rates.append(rate)
    else:
      current_rates.append(rate)

  event_data = { "rates": previous_rates }
  event_data.update(additional_attributes)
  fire_event(previous_event_key, event_data)
  
  event_data = { "rates": current_rates }
  event_data.update(additional_attributes)
  fire_event(current_event_key, event_data)
  
  event_data = { "rates": next_rates }
  event_data.update(additional_attributes)
  fire_event(next_event_key, event_data)

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