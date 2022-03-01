import pytest

from custom_components.octopus_energy.sensor_utils import convert_kwh_to_m3, convert_m3_to_kwh

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

@pytest.mark.asyncio
@pytest.mark.parametrize("kwh,expected_m3",[
  (11.363, 1),
  (56.813, 5)
])
async def test_convert_kwh_to_m3(kwh, expected_m3):
  # Act
  result = convert_kwh_to_m3(kwh)

  # Assert
  assert result == expected_m3