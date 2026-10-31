from datetime import datetime
from typing import Any

from ..api_client.account_balance import AccountBalanceTransaction
from ..utils import get_active_tariff
from ..utils.conversions import pence_to_pounds_pence


def get_account_balance_in_pounds(balance_in_pence: int | None) -> float | None:
  return pence_to_pounds_pence(balance_in_pence) if balance_in_pence is not None else None


def get_account_balance_transactions_in_pounds(transactions: list[AccountBalanceTransaction]) -> list[dict[str, Any]]:
  return [
    {
      "id": transaction.id,
      "type": transaction.type,
      "posted_date": transaction.posted_date,
      "title": transaction.title,
      "amount": get_account_balance_in_pounds(transaction.amount),
      "balance_after": get_account_balance_in_pounds(transaction.balance_carried_forward),
      "is_export": transaction.is_export,
      "consumption_start": transaction.consumption_start,
      "consumption_end": transaction.consumption_end,
      "consumption_quantity": transaction.consumption_quantity,
      "consumption_unit": transaction.consumption_unit,
    }
    for transaction in transactions
  ]


def has_active_tariff(current: datetime, account_info: dict[str, Any] | None) -> bool:
  """Determine if any electricity or gas meter point on the account has an active tariff."""
  if account_info is None:
    return False

  for point in account_info["electricity_meter_points"] + account_info["gas_meter_points"]:
    # We only care about points that have meters and active agreements, as with the other entities
    if len(point["meters"]) > 0 and get_active_tariff(current, point["agreements"]) is not None:
      return True

  return False
