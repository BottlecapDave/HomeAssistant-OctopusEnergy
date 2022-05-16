import pytest

from custom_components.octopus_energy.sensor_utils import convert_m3_to_kwh

@pytest.mark.asyncio
@pytest.mark.parametrize("m3,expected_kwh",[
  (1, 11.363),
  (5, 56.813)
])
async def test_convert_m3_to_kwh(m3, expected_kwh):
  # Act
  result = convert_m3_to_kwh(m3)

  # Assert
  assert result == expected_kwh