import pytest

from custom_components.octopus_energy.intelligent import is_intelligent_product

@pytest.mark.asyncio
@pytest.mark.parametrize("product_code",[
  ("INTELLI-BB-VAR-23-03-01"),
  ("INTELLI-VAR-22-10-14"),
  ("INTELLI-22-03-29"),
  ("INTELLI-FIX-12M-25-04-10"),
  ("IOG-KDP-FIX-12M-25-04-10"),
])
async def test_when_product_code_is_valid_then_true_returned(product_code: str):
  # Act
  assert is_intelligent_product(product_code.upper()) == True
  assert is_intelligent_product(product_code.lower()) == True

@pytest.mark.asyncio
@pytest.mark.parametrize("product_code",[
  ("invalid-product-code"),
  ("INTELLI-FLUX-EXPORT-23-07-14"),
  ("INTELLI-FLUX-EXPORT-BB-23-07-14"),
  ("INTELLI-FLUX-IMPORT-23-07-14"),
  ("INTELLI-FLUX-IMPORT-BB-23-07-14"),
])
async def test_when_invalid_then_none_returned(product_code):
  # Act
  assert is_intelligent_product(product_code.upper()) == False
  assert is_intelligent_product(product_code.lower()) == False