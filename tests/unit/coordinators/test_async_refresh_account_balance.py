import pytest
import mock
from datetime import date, datetime, timedelta

from custom_components.octopus_energy.const import EVENT_ACCOUNT_BALANCE, REFRESH_RATE_IN_MINUTES_ACCOUNT_BALANCE
from custom_components.octopus_energy.coordinators.account_balance import AccountBalanceCoordinatorResult, async_refresh_account_balance
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.account_balance import AccountBalanceResponse, AccountBalanceTransaction

account_id = "A-12345678"
current_utc_timestamp = datetime.strptime("2022-02-12T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_and_previous_data_is_available_then_previous_data_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  previous_data = AccountBalanceCoordinatorResult(current_utc_timestamp, 1, AccountBalanceResponse(balance=1234))
  fired_events = []

  # Act
  result = await async_refresh_account_balance(
    current_utc_timestamp,
    client,
    account_id,
    previous_data,
    lambda name, data: fired_events.append((name, data))
  )

  # Assert
  assert result == previous_data
  assert len(fired_events) == 0

@pytest.mark.asyncio
@pytest.mark.parametrize("existing_result,force_update",[
  (None, False),
  (AccountBalanceCoordinatorResult(current_utc_timestamp, 1, AccountBalanceResponse(balance=1)), True),
  (AccountBalanceCoordinatorResult(current_utc_timestamp - timedelta(minutes=REFRESH_RATE_IN_MINUTES_ACCOUNT_BALANCE), 1, AccountBalanceResponse(balance=1)), False),
])
async def test_when_refresh_is_due_and_data_retrieved_then_data_returned_and_event_fired(existing_result: AccountBalanceCoordinatorResult | None, force_update: bool):
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  expected_data = AccountBalanceResponse(balance=-12345, last_transaction_date=date(2022, 2, 10), transactions=[AccountBalanceTransaction(id="1", type="payment", posted_date=date(2022, 2, 10), title="Payment", amount=5000, balance_carried_forward=-12345)])
  fired_events = []

  async def async_mocked_get_account_balance(*args, **kwargs):
    return expected_data

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account_balance=async_mocked_get_account_balance):
    # Act
    result = await async_refresh_account_balance(
      current_utc_timestamp,
      client,
      account_id,
      existing_result,
      lambda name, data: fired_events.append((name, data)),
      force_update
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp
    assert result.next_refresh == current_utc_timestamp + timedelta(minutes=REFRESH_RATE_IN_MINUTES_ACCOUNT_BALANCE)
    assert result.request_attempts == 1
    assert result.data == expected_data
    assert result.last_error is None

    assert fired_events == [(EVENT_ACCOUNT_BALANCE, { "account_id": account_id, "balance": -123.45, "last_transaction_date": date(2022, 2, 10), "transactions": [{ "id": "1", "type": "payment", "posted_date": date(2022, 2, 10), "title": "Payment", "amount": 50.0, "balance_after": -123.45, "is_export": None, "consumption_start": None, "consumption_end": None, "consumption_quantity": None, "consumption_unit": None }] })]

@pytest.mark.asyncio
async def test_when_refresh_fails_and_no_previous_data_then_fallback_result_returned_and_no_event_fired():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  fired_events = []
  expected_error = RequestException("foo", [])

  async def async_mocked_get_account_balance(*args, **kwargs):
    raise expected_error

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account_balance=async_mocked_get_account_balance):
    # Act
    result = await async_refresh_account_balance(
      current_utc_timestamp,
      client,
      account_id,
      None,
      lambda name, data: fired_events.append((name, data))
    )

    # Assert
    assert result is not None
    assert result.data is None
    assert result.request_attempts == 2
    assert result.last_error == expected_error
    assert result.next_refresh > current_utc_timestamp
    assert len(fired_events) == 0

@pytest.mark.asyncio
async def test_when_refresh_fails_and_previous_data_available_then_previous_data_retained_and_no_event_fired():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  fired_events = []
  expected_error = RequestException("foo", [])
  previous_data = AccountBalanceCoordinatorResult(
    current_utc_timestamp - timedelta(minutes=REFRESH_RATE_IN_MINUTES_ACCOUNT_BALANCE),
    1,
    AccountBalanceResponse(balance=500)
  )

  async def async_mocked_get_account_balance(*args, **kwargs):
    raise expected_error

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account_balance=async_mocked_get_account_balance):
    # Act
    result = await async_refresh_account_balance(
      current_utc_timestamp,
      client,
      account_id,
      previous_data,
      lambda name, data: fired_events.append((name, data))
    )

    # Assert
    assert result is not None
    assert result.data == previous_data.data
    assert result.last_evaluated == previous_data.last_evaluated
    assert result.request_attempts == 2
    assert result.last_error == expected_error
    assert len(fired_events) == 0

@pytest.mark.asyncio
async def test_when_unexpected_exception_raised_then_exception_is_raised():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")

  async def async_mocked_get_account_balance(*args, **kwargs):
    raise Exception("not an api exception")

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account_balance=async_mocked_get_account_balance):
    # Act
    with pytest.raises(Exception):
      await async_refresh_account_balance(current_utc_timestamp, client, account_id, None, lambda name, data: None)

@pytest.mark.asyncio
async def test_when_balance_is_none_then_event_fired_with_none_balance():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  fired_events = []

  async def async_mocked_get_account_balance(*args, **kwargs):
    return AccountBalanceResponse(balance=None)

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account_balance=async_mocked_get_account_balance):
    # Act
    result = await async_refresh_account_balance(
      current_utc_timestamp,
      client,
      account_id,
      None,
      lambda name, data: fired_events.append((name, data))
    )

    # Assert
    assert result.data == AccountBalanceResponse(balance=None)
    assert fired_events == [(EVENT_ACCOUNT_BALANCE, { "account_id": account_id, "balance": None, "last_transaction_date": None, "transactions": [] })]
