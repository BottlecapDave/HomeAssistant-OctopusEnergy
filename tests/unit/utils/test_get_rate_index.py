import pytest

from custom_components.octopus_energy.utils.rate_information import get_rate_index

@pytest.mark.asyncio
@pytest.mark.parametrize("total_unique_rates,peak_type,expected_index",[
  (1, None, None),
  (2, "off_peak", 0),
  (2, "peak", 1),
  (3, "off_peak", 0),
  (3, "standard", 1),
  (3, "peak", 2),
])
async def test_when_called_then_correct_rate_index_returned(total_unique_rates: list, peak_type: str, expected_index: int):
  # Act
  result = get_rate_index(total_unique_rates, peak_type)

  # Assert
  assert result == expected_index