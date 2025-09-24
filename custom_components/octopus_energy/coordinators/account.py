import logging
from datetime import datetime, timedelta
from typing import Callable

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from homeassistant.helpers import issue_registry as ir

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,

  DATA_CLIENT,
  DATA_ACCOUNT,
  DATA_ACCOUNT_COORDINATOR,
  REFRESH_RATE_IN_MINUTES_ACCOUNT,
  REPAIR_ACCOUNT_NOT_FOUND,
  REPAIR_INVALID_API_KEY,
)

from ..api_client import ApiException, AuthenticationException, OctopusEnergyApiClient
from . import BaseCoordinatorResult
from ..utils import get_active_tariff
from ..utils.repairs import safe_repair_key

_LOGGER = logging.getLogger(__name__)

class AccountCoordinatorResult(BaseCoordinatorResult):
  account: dict

  def __init__(self, last_evaluated: datetime, request_attempts: int, account: dict, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_ACCOUNT, None, last_error)
    self.account = account

def raise_product_not_found(hass, product_code: str, is_electricity: bool):
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

def raise_account_not_found(hass, account_id: str):
  ir.async_create_issue(
    hass,
    DOMAIN,
    safe_repair_key(REPAIR_ACCOUNT_NOT_FOUND, account_id),
    is_fixable=False,
    severity=ir.IssueSeverity.ERROR,
    learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/account_not_found",
    translation_key="account_not_found",
    translation_placeholders={ "account_id": account_id },
  )

def clear_issue(hass, key: str):
  ir.async_delete_issue(hass, DOMAIN, key)

def raise_invalid_api_key(hass, account_id: str):
  ir.async_create_issue(
    hass,
    DOMAIN,
    safe_repair_key(REPAIR_INVALID_API_KEY, account_id),
    is_fixable=False,
    severity=ir.IssueSeverity.ERROR,
    translation_key="invalid_api_key",
    translation_placeholders={ "account_id": account_id },
  )

def raise_meter_added(hass, account_id: str, mprn_mpan: str, serial_number: str, is_electricity: bool):
  ir.async_create_issue(
    hass,
    DOMAIN,
    safe_repair_key("meter_added_{}_{}_{}_{}", account_id, mprn_mpan, serial_number, is_electricity),
    is_fixable=False,
    severity=ir.IssueSeverity.WARNING,
    translation_key="meter_added",
    translation_placeholders={ "account_id": account_id, "mprn_mpan": mprn_mpan, "serial_number": serial_number, "meter_type": "Electricity" if is_electricity else "Gas" },
  )

def raise_meter_removed(hass, account_id: str, mprn_mpan: str, serial_number: str, is_electricity: bool):
  ir.async_create_issue(
    hass,
    DOMAIN,
    safe_repair_key("meter_removed_{}_{}_{}_{}", account_id, mprn_mpan, serial_number, is_electricity),
    is_fixable=False,
    severity=ir.IssueSeverity.WARNING,
    learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/meter_removed",
    translation_key="meter_removed",
    translation_placeholders={ "account_id": account_id, "mprn_mpan": mprn_mpan, "serial_number": serial_number, "meter_type": "Electricity" if is_electricity else "Gas" },
  )

async def async_check_valid_product(client: OctopusEnergyApiClient, product_code: str, is_electricity: bool, raise_product_not_found: Callable[[str, bool], None]):
  try:
    _LOGGER.debug(f"Retrieving product information for '{product_code}'")
    product = await client.async_get_product(product_code)
    if product is None:
      raise_product_not_found(product_code, is_electricity)
  except:
    _LOGGER.debug(f"Failed to retrieve product info for '{product_code}'")

def get_active_electricity_meters(current: datetime, account_info: dict) -> dict[tuple[str, str], str]:
  unique_meters = {}
  if account_info is not None:
    if "electricity_meter_points" in account_info and account_info["electricity_meter_points"] is not None:
      for point in account_info["electricity_meter_points"]:
        active_tariff = get_active_tariff(current, point["agreements"])
        if active_tariff is not None:
          for meter in point["meters"]:
            mpan = point["mpan"]
            serial_number = meter["serial_number"]
            key = (mpan, serial_number)
            unique_meters[key] = active_tariff
  
  return unique_meters

def get_active_gas_meters(current: datetime, account_info: dict) -> dict[tuple[str, str], str]:
  unique_meters = {}
  if account_info is not None:
    if "gas_meter_points" in account_info and account_info["gas_meter_points"] is not None:
      for point in account_info["gas_meter_points"]:
        active_tariff = get_active_tariff(current, point["agreements"])
        if active_tariff is not None:
          for meter in point["meters"]:
            mprn = point["mprn"]
            serial_number = meter["serial_number"]
            key = (mprn, serial_number)
            unique_meters[key] = active_tariff
  
  return unique_meters

def check_for_removed_and_added_meters(account_id: str,
                                       previous_meters: dict[tuple[str, str], str],
                                       current_meters: dict[tuple[str, str], str],
                                       is_electricity: bool,
                                       raise_meter_removed: Callable[[str, str, bool], None],
                                       raise_meter_added: Callable[[str, str, bool], None],
                                       clear_issue: Callable[[str], None]):
  removed_meters = []
  added_meters = []

  for previous_key in previous_meters.keys():
    # Delete legacy issues
    clear_issue("meter_removed_{}_{}_{}_{}".format(account_id, previous_key[0], previous_key[1], is_electricity))

    if previous_key not in current_meters:
      raise_meter_removed(previous_key[0], previous_key[1], is_electricity)

  for current_key in current_meters.keys():
    # Delete legacy issues
    clear_issue("meter_added_{}_{}_{}_{}".format(account_id, current_key[0], current_key[1], is_electricity))

    if current_key not in previous_meters:
      raise_meter_added(current_key[0], current_key[1], is_electricity)

  return removed_meters, added_meters

async def async_refresh_account(
  current: datetime,
  client: OctopusEnergyApiClient,
  account_id: str,
  previous_request: AccountCoordinatorResult,
  raise_account_not_found: Callable[[], None],
  raise_invalid_api_key: Callable[[], None],
  raise_product_not_found: Callable[[str, bool], None],
  raise_meter_removed: Callable[[str, str, bool], None],
  raise_meter_added: Callable[[str, str, bool], None],
  clear_issue: Callable[[str], None]
):
  if (current >= previous_request.next_refresh):
    account_info = None
    try:
      account_info = await client.async_get_account(account_id)

      if account_info is None:
        raise_account_not_found()
      else:
        _LOGGER.debug('Account information retrieved')

        # Delete legacy issues
        clear_issue(REPAIR_ACCOUNT_NOT_FOUND.format(account_id))
        clear_issue(REPAIR_INVALID_API_KEY.format(account_id))

        clear_issue(safe_repair_key(REPAIR_ACCOUNT_NOT_FOUND, account_id))
        clear_issue(safe_repair_key(REPAIR_INVALID_API_KEY, account_id))

        previous_unique_electricity_meters = get_active_electricity_meters(current, previous_request.account) if previous_request.account is not None else {}
        previous_unique_gas_meters = get_active_gas_meters(current, previous_request.account) if previous_request.account is not None else {}
        current_unique_electricity_meters = get_active_electricity_meters(current, account_info)
        current_unique_gas_meters = get_active_gas_meters(current, account_info)

        check_for_removed_and_added_meters(account_id, previous_unique_electricity_meters, current_unique_electricity_meters, True, raise_meter_removed, raise_meter_added, clear_issue)
        check_for_removed_and_added_meters(account_id, previous_unique_gas_meters, current_unique_gas_meters, False, raise_meter_removed, raise_meter_added, clear_issue)

        for meter_key in current_unique_electricity_meters.keys():
          product = current_unique_electricity_meters[meter_key].product
          await async_check_valid_product(client, product, True, raise_product_not_found)

        for meter_key in current_unique_gas_meters.keys():
          product = current_unique_gas_meters[meter_key].product
          await async_check_valid_product(client, product, False, raise_product_not_found)

        return AccountCoordinatorResult(current, 1, account_info)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise

      if isinstance(e, AuthenticationException):
        raise_invalid_api_key()
      
      result = AccountCoordinatorResult(
        previous_request.last_evaluated,
        previous_request.request_attempts + 1,
        previous_request.account,
        last_error=e
      )
      
      if (result.request_attempts == 2):
        _LOGGER.warning(f'Failed to retrieve account information - using cached version. See diagnostics sensor for more information.')
      
      return result

  return previous_request

async def async_setup_account_info_coordinator(hass, account_id: str):
  async def async_update_account_data():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]

    if DATA_ACCOUNT not in hass.data[DOMAIN][account_id] or hass.data[DOMAIN][account_id][DATA_ACCOUNT] is None:
      raise Exception("Failed to find account information")

    hass.data[DOMAIN][account_id][DATA_ACCOUNT] = await async_refresh_account(
      current,
      client,
      account_id,
      hass.data[DOMAIN][account_id][DATA_ACCOUNT],
      lambda: raise_account_not_found(hass, account_id),
      lambda: raise_invalid_api_key(hass, account_id),
      lambda product_code, is_electricity: raise_product_not_found(hass, product_code, is_electricity),
      lambda mprn_mpan, serial_number, is_electricity: raise_meter_removed(hass, account_id, mprn_mpan, serial_number, is_electricity),
      lambda mprn_mpan, serial_number, is_electricity: raise_meter_added(hass, account_id, mprn_mpan, serial_number, is_electricity),
      lambda key: clear_issue(hass, key)
    )
    
    return hass.data[DOMAIN][account_id][DATA_ACCOUNT]

  hass.data[DOMAIN][account_id][DATA_ACCOUNT_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"update_account-{account_id}",
    update_method=async_update_account_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )
