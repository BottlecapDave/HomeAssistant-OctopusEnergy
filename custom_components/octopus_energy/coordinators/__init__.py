from datetime import datetime, timedelta
import logging
from typing import Callable, Any

from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.util.dt import (as_utc)

from ..const import (
  DOMAIN,
)

from ..api_client import OctopusEnergyApiClient

from ..utils import (
  get_active_tariff
)
from ..utils.rate_information import get_min_max_average_rates
from ..utils.requests import calculate_next_refresh

from ..const import (
  DOMAIN,
  DATA_KNOWN_TARIFF,
)

_LOGGER = logging.getLogger(__name__)

class MultiCoordinatorEntity(CoordinatorEntity):
  def __init__(self, primary_coordinator, secondary_coordinators):
    CoordinatorEntity.__init__(self, primary_coordinator)
    self._secondary_coordinators = secondary_coordinators

  async def async_added_to_hass(self) -> None:
    """When entity is added to hass."""
    await super().async_added_to_hass()
    for secondary_coordinator in self._secondary_coordinators:
      self.async_on_remove(
          secondary_coordinator.async_add_listener(
            self._handle_coordinator_update, self.coordinator_context
          )
      )

class BaseCoordinatorResult:
  last_evaluated: datetime
  last_retrieved: datetime
  next_refresh: datetime
  request_attempts: int
  refresh_rate_in_minutes: float
  last_error: Exception | None

  def __init__(self, last_evaluated: datetime, request_attempts: int, refresh_rate_in_minutes: float, last_retrieved: datetime | None = None, last_error: Exception | None = None):
    self.last_evaluated = last_evaluated
    self.last_retrieved = last_retrieved if last_retrieved is not None else last_evaluated
    self.request_attempts = request_attempts
    self.next_refresh = calculate_next_refresh(last_evaluated, request_attempts, refresh_rate_in_minutes)
    self.last_error = last_error
    _LOGGER.debug(f'last_evaluated: {last_evaluated}; last_retrieved: {last_retrieved}; request_attempts: {request_attempts}; refresh_rate_in_minutes: {refresh_rate_in_minutes}; next_refresh: {self.next_refresh}; last_error: {self.last_error}')

async def async_check_valid_product(hass, account_id: str, client: OctopusEnergyApiClient, product_code: str, is_electricity: bool):
  tariff_key = f'{DATA_KNOWN_TARIFF}_{product_code}'
  try:
    _LOGGER.debug(f"Retrieving product information for '{product_code}'")
    product = await client.async_get_product(product_code)
    if product is None:
      ir.async_create_issue(
        hass,
        DOMAIN,
        f"unknown_product_{product_code}",
        is_fixable=False,
        severity=ir.IssueSeverity.ERROR,
        learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/unknown_product",
        translation_key="unknown_product",
        translation_placeholders={ "type": "Electricity" if is_electricity else "Gas", "product_code": product_code },
      )
    else:
      hass.data[DOMAIN][account_id][tariff_key] = True
  except:
    _LOGGER.debug(f"Failed to retrieve product info for '{product_code}'")

def __raise_rate_event(event_key: str,
                       rates: list,
                       additional_attributes: "dict[str, Any]",
                       fire_event: Callable[[str, "dict[str, Any]"], None]):
  
  min_max_average_rates = get_min_max_average_rates(rates)

  event_data = { "rates": rates, "min_rate": min_max_average_rates["min"], "max_rate": min_max_average_rates["max"], "average_rate": min_max_average_rates["average"] }
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
  today_end = as_utc((now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))

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

def get_electricity_meter_tariff(current: datetime, account_info, target_mpan: str, target_serial_number: str):
  if len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff = get_active_tariff(current, point["agreements"])
      # The type of meter (ie smart vs dumb) can change the tariff behaviour, so we
      # have to enumerate the different meters being used for each tariff as well.
      for meter in point["meters"]:
        if active_tariff is not None and point["mpan"] == target_mpan and meter["serial_number"] == target_serial_number:
          return active_tariff
           
  return None

def get_gas_meter_tariff(current: datetime, account_info, target_mprn: str, target_serial_number: str):
  if len(account_info["gas_meter_points"]) > 0:
    for point in account_info["gas_meter_points"]:
      active_tariff = get_active_tariff(current, point["agreements"])
      for meter in point["meters"]:
        if active_tariff is not None and point["mprn"] == target_mprn and meter["serial_number"] == target_serial_number:
           return active_tariff
           
  return None

def combine_rates(old_rates: list | None, new_rates: list | None, period_from: datetime, period_to: datetime):
  if new_rates is None:
    return None
  
  combined_rates = []
  combined_rates.extend(new_rates)

  if old_rates is not None:
    for rate in old_rates:
      if rate["start"] >= period_from and rate["end"] <= period_to:
        is_present = False
        for existing_rate in combined_rates:
          if existing_rate["start"] == rate["start"]:
            is_present = True
            break

        if is_present == False:
          combined_rates.append(rate)

    combined_rates.sort(key=lambda x: x["start"])

  return combined_rates