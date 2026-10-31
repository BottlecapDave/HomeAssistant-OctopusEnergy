import json
from datetime import date
from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.octopus_energy.api_client import (
  OctopusEnergyApiClient,
  RequestException,
  TimeoutException,
  account_balance_query,
  integration_context_header,
)
from custom_components.octopus_energy.api_client.account_balance import AccountBalanceResponse, AccountBalanceTransaction
from custom_components.octopus_energy.const import ACCOUNT_BALANCE_TRANSACTIONS_TO_RETRIEVE


@pytest.mark.asyncio
@pytest.mark.parametrize("balance,edges,expected_date", [
  (12345, [{"node": {"__typename": "Payment", "id": "1", "postedDate": "2022-02-10", "amount": 100}}], date(2022, 2, 10)),
  (0, [{"node": {"__typename": "Payment", "id": "1", "postedDate": "2022-02-10", "amount": 100}}], date(2022, 2, 10)),
  (-12345, [{"node": {"__typename": "Payment", "id": "1", "postedDate": "2022-02-10", "amount": 100}}], date(2022, 2, 10)),
  (None, [], None),
  (500, [], None),
])
async def test_authenticated_account_balance_query(balance, edges, expected_date):
  client = OctopusEnergyApiClient("test-api-key")
  client._graphql_token = "test-token"
  response = Mock(status=200)
  response.request_info.headers = {integration_context_header: "account-balance"}
  response.text = AsyncMock(return_value=json.dumps({
    "data": {"account": {"balance": balance, "transactions": {"edges": edges}}},
  }))
  session = Mock()
  session.post.return_value.__aenter__ = AsyncMock(return_value=response)
  session.post.return_value.__aexit__ = AsyncMock(return_value=False)
  with patch.object(client, "async_refresh_token", AsyncMock()) as refresh_token:
    with patch.object(client, "_create_client_session", AsyncMock(return_value=session)):
      result = await client.async_get_account_balance("A-12345678")

  refresh_token.assert_awaited_once()
  session.post.assert_called_once_with(
    "https://api.oegb-kraken.energy/v1/graphql/",
    json={
      "query": account_balance_query,
      "variables": {"accountNumber": "A-12345678", "transactionsToRetrieve": ACCOUNT_BALANCE_TRANSACTIONS_TO_RETRIEVE},
    },
    headers={"Authorization": "test-token", integration_context_header: "account-balance"},
  )
  assert result.balance == balance
  assert result.last_transaction_date == expected_date
  assert len(result.transactions) == len(edges)


@pytest.mark.asyncio
@pytest.mark.parametrize("body", [
  None,
  {},
  {"data": None},
  {"data": {}},
  {"data": {"account": None}},
  {"data": {"account": {}}},
])
async def test_incomplete_response_raises_request_exception(body):
  client = OctopusEnergyApiClient("test-api-key")
  session = Mock()
  session.post.return_value.__aenter__ = AsyncMock()
  session.post.return_value.__aexit__ = AsyncMock(return_value=False)
  with patch.object(client, "async_refresh_token", AsyncMock()):
    with patch.object(client, "_create_client_session", AsyncMock(return_value=session)):
      with patch.object(client, "__async_read_response__", AsyncMock(return_value=body)):
        with pytest.raises(RequestException):
          await client.async_get_account_balance("A-12345678")


@pytest.mark.asyncio
async def test_graphql_errors_are_raised():
  client = OctopusEnergyApiClient("test-api-key")
  response = Mock(status=200)
  response.request_info.headers = {}
  response.text = AsyncMock(return_value=json.dumps({"errors": [{"message": "Balance unavailable"}]}))
  session = Mock()
  session.post.return_value.__aenter__ = AsyncMock(return_value=response)
  session.post.return_value.__aexit__ = AsyncMock(return_value=False)
  with patch.object(client, "async_refresh_token", AsyncMock()):
    with patch.object(client, "_create_client_session", AsyncMock(return_value=session)):
      with pytest.raises(RequestException):
        await client.async_get_account_balance("A-12345678")


@pytest.mark.asyncio
async def test_timeout_is_translated_to_api_exception():
  client = OctopusEnergyApiClient("test-api-key")
  with patch.object(client, "async_refresh_token", AsyncMock()):
    with patch.object(client, "_create_client_session", AsyncMock(side_effect=TimeoutError)):
      with pytest.raises(TimeoutException):
        await client.async_get_account_balance("A-12345678")


def test_transactions_are_mapped_from_edges():
  data = AccountBalanceResponse.model_validate({
    "balance": 5000,
    "transactions": {"edges": [
      {"node": {
        "__typename": "Charge", "id": "101", "postedDate": "2022-02-10", "title": "Electricity",
        "amount": 250, "balanceCarriedForward": 5000, "isExport": False,
        "consumption": {"startDate": "2022-02-10", "endDate": "2022-02-10", "quantity": "12.5", "unit": "kWh"},
      }},
      {"node": {"__typename": "Credit", "id": "102", "postedDate": "2022-02-09", "title": "Goodwill", "amount": 1000, "balanceCarriedForward": 5250}},
      {"node": {"__typename": "Payment", "id": "104", "postedDate": "2022-02-07", "title": "Direct debit", "amount": 3000, "balanceCarriedForward": 2250}},
      {"node": {"__typename": "Refund", "id": "103", "postedDate": "2022-02-08", "title": None, "amount": 2000, "balanceCarriedForward": 4250}},
    ]},
  })

  assert data.last_transaction_date == date(2022, 2, 10)
  assert data.transactions == [
    AccountBalanceTransaction(
      id="101", type="charge", posted_date=date(2022, 2, 10), title="Electricity", amount=250, balance_carried_forward=5000,
      is_export=False, consumption_start=date(2022, 2, 10), consumption_end=date(2022, 2, 10), consumption_quantity=12.5, consumption_unit="kWh"
    ),
    AccountBalanceTransaction(id="102", type="credit", posted_date=date(2022, 2, 9), title="Goodwill", amount=1000, balance_carried_forward=5250),
    AccountBalanceTransaction(id="104", type="payment", posted_date=date(2022, 2, 7), title="Direct debit", amount=3000, balance_carried_forward=2250),
    AccountBalanceTransaction(id="103", type="refund", posted_date=date(2022, 2, 8), title=None, amount=2000, balance_carried_forward=4250),
  ]


def test_empty_edges_gives_no_transactions():
  data = AccountBalanceResponse.model_validate({"balance": 1, "transactions": {"edges": []}})
  assert data.transactions == []
  assert data.last_transaction_date is None


def test_null_transaction_fields_are_mapped_to_none():
  data = AccountBalanceResponse.model_validate({
    "balance": 1,
    "transactions": {"edges": [
      {"node": {"__typename": "Charge", "id": None, "postedDate": None, "title": None, "amount": None, "balanceCarriedForward": None, "isExport": None, "consumption": None}},
    ]},
  })

  assert data.last_transaction_date is None
  assert data.transactions == [AccountBalanceTransaction(type="charge")]
