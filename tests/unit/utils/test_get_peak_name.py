import pytest

from custom_components.octopus_energy.utils.rate_information import get_peak_name

@pytest.mark.asyncio
@pytest.mark.parametrize("peak_type,expected_name",[
  (None, None),
  ("off_peak", "Off Peak"),
  ("peak", "Peak"),
  ("standard", "Standard"),
  ("blah", None),
])
async def test_when_called_then_correct_name_returned(peak_type: str, expected_name: str):
  # Act
  result = get_peak_name(peak_type)

  # Assert
  assert result == expected_name