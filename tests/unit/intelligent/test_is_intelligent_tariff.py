import pytest

from custom_components.octopus_energy.intelligent import is_intelligent_tariff

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff_code",[
  ("E-1R-INTELLI-VAR-22-10-14-C"),
])
async def test_when_tariff_code_is_valid_then_true_returned(tariff_code: str):
  # Act
  assert is_intelligent_tariff(tariff_code.upper()) == True
  assert is_intelligent_tariff(tariff_code.lower()) == True

@pytest.mark.asyncio
async def test_when_invalid_then_none_returned():
  # Act
  assert is_intelligent_tariff("invalid-tariff-code") == False