import pytest

from custom_components.octopus_energy.account import get_account_balance_in_pounds

@pytest.mark.parametrize("balance_in_pence,expected",[
  (None, None),
  (0, 0),
  (12345, 123.45),
  (-12345, -123.45),
  (1, 0.01),
  (-1, -0.01),
])
def test_when_balance_provided_then_pounds_returned(balance_in_pence: int | None, expected: float | None):
  assert get_account_balance_in_pounds(balance_in_pence) == expected
