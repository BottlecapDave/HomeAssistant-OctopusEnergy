import pytest

from custom_components.octopus_energy.gas import convert_m3_to_kwh

@pytest.mark.asyncio
@pytest.mark.parametrize("m3,calorificValue,expected_kwh",[
  (1, 40, 11.363),
  (5, 40, 56.813)
])
async def test_convert_m3_to_kwh(m3, calorificValue, expected_kwh):
  # Act
  result = convert_m3_to_kwh(m3, calorificValue)

  # Assert
  assert result == expected_kwh