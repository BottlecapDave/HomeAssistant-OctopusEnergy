from datetime import date
from typing import Any

from pydantic import BaseModel, model_validator


class AccountBalanceTransaction(BaseModel):
  id: str | None = None
  # Lowercase GraphQL type name, one of charge, payment, refund or credit
  type: str
  posted_date: date | None = None
  title: str | None = None
  # Amount in pence as reported by the API. The sign depends on the type, e.g. export earnings are negative charges.
  # The API documents all of these as nullable, apart from the type.
  amount: int | None = None
  # Balance in pence after this transaction. Positive is in credit, negative is in debit.
  balance_carried_forward: int | None = None
  # The following are only available for charges
  is_export: bool | None = None
  consumption_start: date | None = None
  consumption_end: date | None = None
  consumption_quantity: float | None = None
  consumption_unit: str | None = None

  @model_validator(mode="before")
  @classmethod
  def map_node(cls, data: Any) -> Any:
    # Flatten the GraphQL node, which nests the consumption and uses different names
    if isinstance(data, dict) and "__typename" in data:
      consumption = data.get("consumption") or {}
      return {
        "id": data.get("id"),
        "type": str(data.get("__typename")).lower(),
        "posted_date": data.get("postedDate"),
        "title": data.get("title"),
        "amount": data.get("amount"),
        "balance_carried_forward": data.get("balanceCarriedForward"),
        "is_export": data.get("isExport"),
        "consumption_start": consumption.get("startDate"),
        "consumption_end": consumption.get("endDate"),
        "consumption_quantity": consumption.get("quantity"),
        "consumption_unit": consumption.get("unit"),
      }

    return data


class AccountBalanceResponse(BaseModel):
  # Balance in pence. Positive is in credit, negative is in debit.
  balance: int | None = None
  # The date the latest transaction was posted. The balance includes all transactions posted up to the end of that day.
  last_transaction_date: date | None = None
  # Most recent transactions, newest first
  transactions: list[AccountBalanceTransaction] = []

  @model_validator(mode="before")
  @classmethod
  def map_transactions(cls, data: Any) -> Any:
    # The API returns transactions as graphql edges, so flatten them
    if isinstance(data, dict) and "transactions" in data and isinstance(data["transactions"], dict):
      edges = data["transactions"].get("edges") or []
      transactions = [edge["node"] for edge in edges]
      return {
        "balance": data.get("balance"),
        "last_transaction_date": transactions[0].get("postedDate") if len(transactions) > 0 else None,
        "transactions": transactions,
      }

    return data
