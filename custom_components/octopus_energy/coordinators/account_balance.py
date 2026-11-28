import logging
from datetime import datetime, timedelta
from typing import Any, Callable

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,
  DATA_CLIENT,
  DATA_ACCOUNT_BALANCE,
  EVENT_ACCOUNT_BALANCE,
  REFRESH_RATE_IN_MINUTES_ACCOUNT_BALANCE,
)

from ..account import get_account_balance_in_pounds, get_account_balance_transactions_in_pounds
from ..api_client import ApiException, OctopusEnergyApiClient
from ..api_client.account_balance import AccountBalanceResponse
from . import BaseCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class AccountBalanceCoordinatorResult(BaseCoordinatorResult):
  last_evaluated: datetime
  data: AccountBalanceResponse | None

  def __init__(self, last_evaluated: datetime, request_attempts: int, data: AccountBalanceResponse | None, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_ACCOUNT_BALANCE, None, last_error)
    self.data = data

async def async_refresh_account_balance(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_id: str,
    existing_result: AccountBalanceCoordinatorResult | None,
    fire_event: Callable[[str, "dict[str, Any]"], None],
    force_update: bool = False
) -> AccountBalanceCoordinatorResult:
  if existing_result is None or force_update or current >= existing_result.next_refresh:
    try:
      data = await client.async_get_account_balance(account_id)

      fire_event(EVENT_ACCOUNT_BALANCE, {
        "account_id": account_id,
        "balance": get_account_balance_in_pounds(data.balance),
        "last_transaction_date": data.last_transaction_date,
        "transactions": get_account_balance_transactions_in_pounds(data.transactions),
      })

      return AccountBalanceCoordinatorResult(current, 1, data)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise

      result = None
      if (existing_result is not None):
        result = AccountBalanceCoordinatorResult(existing_result.last_evaluated, existing_result.request_attempts + 1, existing_result.data, last_error=e)
        if (result.request_attempts == 2):
          _LOGGER.warning(f'Failed to retrieve account balance - using cached data. See diagnostics sensor for more information.')
      else:
        result = AccountBalanceCoordinatorResult(
          # We want to force into our fallback mode
          current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_ACCOUNT_BALANCE),
          2,
          None,
          last_error=e
        )
        _LOGGER.warning(f'Failed to retrieve account balance. See diagnostics sensor for more information.')

      return result

  return existing_result

async def async_setup_account_balance_coordinator(hass, account_id: str):
  async def async_update_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]

    hass.data[DOMAIN][account_id][DATA_ACCOUNT_BALANCE] = await async_refresh_account_balance(
      current,
      client,
      account_id,
      hass.data[DOMAIN][account_id][DATA_ACCOUNT_BALANCE] if DATA_ACCOUNT_BALANCE in hass.data[DOMAIN][account_id] else None,
      hass.bus.async_fire
    )

    return hass.data[DOMAIN][account_id][DATA_ACCOUNT_BALANCE]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"account_balance_{account_id}",
    update_method=async_update_data,
    # We update every minute, but we will only actually retrieve data every REFRESH_RATE_IN_MINUTES_ACCOUNT_BALANCE minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  return coordinator
