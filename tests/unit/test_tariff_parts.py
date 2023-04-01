import pytest

from custom_components.octopus_energy.utils import get_tariff_parts

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff_code,expected_energy,expected_rate,expected_product_code,expected_region",[
  ("G-1R-SUPER-GREEN-24M-21-07-30-A", "G", "1R", "SUPER-GREEN-24M-21-07-30", "A"),
  ("E-2R-SUPER-GREEN-24M-21-07-30-A", "E", "2R", "SUPER-GREEN-24M-21-07-30", "A")
])
async def test_get_tariff_parts(tariff_code, expected_energy, expected_rate, expected_product_code, expected_region):
  # Act
  result = get_tariff_parts(tariff_code)

  # Assert
  assert result != None
  assert "energy" in result
  assert result["energy"] == expected_energy
  assert "rate" in result
  assert result["rate"] == expected_rate
  assert "product_code" in result
  assert result["product_code"] == expected_product_code
  assert "region" in result
  assert result["region"] == expected_region

@pytest.mark.asyncio
async def test_get_tariff_parts_when_invalid_then_none_returned():
  # Act
  result = get_tariff_parts("invalid-tariff-code")