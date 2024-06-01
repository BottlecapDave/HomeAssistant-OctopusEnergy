import pytest

from custom_components.octopus_energy.utils.tariff_check import is_agile_tariff

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff_code,expected_result",[
  ("E-1R-AGILE-FLEX-22-11-25-B", True),
  ("E-1R-INTELLI-VAR-22-10-14-C", False),
])
async def test_when_tariff_code_is_valid_then_true_returned(tariff_code: str, expected_result: bool):
  # Act
  assert is_agile_tariff(tariff_code.upper()) == expected_result
  assert is_agile_tariff(tariff_code.lower()) == expected_result

@pytest.mark.asyncio
async def test_when_invalid_then_false_returned():
  # Act
  assert is_agile_tariff("invalid-tariff-code") == False