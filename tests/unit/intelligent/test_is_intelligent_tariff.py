import pytest

from custom_components.octopus_energy.intelligent import is_intelligent_tariff

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff_code",[
  ("E-1R-INTELLI-VAR-22-10-14-C".upper()),
  ("E-1R-INTELLI-VAR-22-10-14-C".lower()),
  ("E-1R-INTELLI-BB-VAR-23-03-01-C".upper()),
  ("E-1R-INTELLI-BB-VAR-23-03-01-C".lower()),
])
async def test_when_tariff_code_is_valid_then_true_returned(tariff_code: str):
  # Act
  assert is_intelligent_tariff(tariff_code.upper()) == True
  assert is_intelligent_tariff(tariff_code.lower()) == True

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff_code",[
  ("invalid-tariff-code".upper()),
  ("invalid-tariff-code".lower()),
  ("E-1R-INTELLI-FLUX-IMPORT-23-07-14-E".upper()),
  ("E-1R-INTELLI-FLUX-IMPORT-23-07-14-E".lower()),
])
async def test_when_invalid_then_none_returned(tariff_code):
  # Act
  assert is_intelligent_tariff(tariff_code) == False