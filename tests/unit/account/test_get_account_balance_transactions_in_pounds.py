from datetime import date

from custom_components.octopus_energy.account import get_account_balance_transactions_in_pounds
from custom_components.octopus_energy.api_client.account_balance import AccountBalanceTransaction

def test_when_no_transactions_then_empty_list_returned():
  assert get_account_balance_transactions_in_pounds([]) == []

def test_when_transactions_provided_then_pence_converted_to_pounds_and_raw_sign_kept():
  transactions = [
    AccountBalanceTransaction(
      id="1", type="charge", posted_date=date(2022, 2, 10), title="Electricity", amount=-250, balance_carried_forward=-12345,
      is_export=True, consumption_start=date(2022, 2, 9), consumption_end=date(2022, 2, 10), consumption_quantity=12.5, consumption_unit="kWh"
    ),
    AccountBalanceTransaction(id="2", type="payment", posted_date=date(2022, 2, 9), amount=5000, balance_carried_forward=None),
  ]

  assert get_account_balance_transactions_in_pounds(transactions) == [
    {
      "id": "1", "type": "charge", "posted_date": date(2022, 2, 10), "title": "Electricity", "amount": -2.5, "balance_after": -123.45,
      "is_export": True, "consumption_start": date(2022, 2, 9), "consumption_end": date(2022, 2, 10),
      "consumption_quantity": 12.5, "consumption_unit": "kWh",
    },
    {
      "id": "2", "type": "payment", "posted_date": date(2022, 2, 9), "title": None, "amount": 50.0, "balance_after": None,
      "is_export": None, "consumption_start": None, "consumption_end": None, "consumption_quantity": None, "consumption_unit": None,
    },
  ]

def test_when_transaction_values_are_none_then_none_returned():
  result = get_account_balance_transactions_in_pounds([AccountBalanceTransaction(type="credit")])

  assert result[0]["id"] is None
  assert result[0]["posted_date"] is None
  assert result[0]["amount"] is None
  assert result[0]["balance_after"] is None
