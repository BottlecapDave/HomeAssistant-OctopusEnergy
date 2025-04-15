import logging
from datetime import datetime, timedelta

from . import BaseCoordinatorResult, async_check_valid_product
from ..utils import get_active_tariff

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

_LOGGER = logging.getLogger(__name__)

class AccountCoordinatorResult(BaseCoordinatorResult):
  account: dict

  def __init__(self, last_evaluated: datetime, request_attempts: int, account: dict, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_ACCOUNT, None, last_error)
    self.account = account

async def async_refresh_account(
  hass,
  current: datetime,
  client: OctopusEnergyApiClient,
  account_id: str,
  previous_request: AccountCoordinatorResult
):
  if (current >= previous_request.next_refresh):
    account_info = None
    try:
      account_info = await client.async_get_account(account_id)

      if account_info is None:
        ir.async_create_issue(
          hass,
          DOMAIN,
          REPAIR_ACCOUNT_NOT_FOUND.format(account_id),
          is_fixable=False,
          severity=ir.IssueSeverity.ERROR,
          learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/account_not_found",
          translation_key="account_not_found",
          translation_placeholders={ "account_id": account_id },
        )
      else:
        _LOGGER.debug('Account information retrieved')

        ir.async_delete_issue(hass, DOMAIN, REPAIR_ACCOUNT_NOT_FOUND.format(account_id))
        ir.async_delete_issue(hass, DOMAIN, REPAIR_INVALID_API_KEY.format(account_id))

        if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
          for point in account_info["electricity_meter_points"]:
            active_tariff = get_active_tariff(current, point["agreements"])
            if active_tariff is not None:
              await async_check_valid_product(hass, account_id, client, active_tariff.product, True)

        if account_info is not None and len(account_info["gas_meter_points"]) > 0:
          for point in account_info["gas_meter_points"]:
            active_tariff = get_active_tariff(current, point["agreements"])
            if active_tariff is not None:
              await async_check_valid_product(hass, account_id, client, active_tariff.product, False)

        return AccountCoordinatorResult(current, 1, account_info)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise

      if isinstance(e, AuthenticationException):
        ir.async_create_issue(
          hass,
          DOMAIN,
          REPAIR_INVALID_API_KEY.format(account_id),
          is_fixable=False,
          severity=ir.IssueSeverity.ERROR,
          translation_key="invalid_api_key",
          translation_placeholders={ "account_id": account_id },
        )
      
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
      hass,
      current,
      client,
      account_id,
      hass.data[DOMAIN][account_id][DATA_ACCOUNT]
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