from datetime import date
import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
async def test_when_get_account_balance_called_then_balance_is_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id

    # Act
    result = await client.async_get_account_balance(account_id)

    # Assert
    assert result is not None

    assert isinstance(result.balance, int)
    assert isinstance(result.transactions, list)
    for transaction in result.transactions:
        assert isinstance(transaction.id, str)
        assert transaction.type in ["charge", "payment", "refund", "credit"]
        assert isinstance(transaction.posted_date, date)
        assert isinstance(transaction.amount, int)
        assert transaction.balance_carried_forward is None or isinstance(transaction.balance_carried_forward, int)
        assert transaction.is_export is None or isinstance(transaction.is_export, bool)
        assert transaction.consumption_start is None or isinstance(transaction.consumption_start, date)
        assert transaction.consumption_end is None or isinstance(transaction.consumption_end, date)
        assert transaction.consumption_quantity is None or isinstance(transaction.consumption_quantity, float)
    assert result.last_transaction_date is None or isinstance(result.last_transaction_date, date)
