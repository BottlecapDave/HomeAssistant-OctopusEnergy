import pytest

from custom_components.octopus_energy.utils.rate_information import get_peak_name

@pytest.mark.asyncio
@pytest.mark.parametrize("total_unique_rates,unique_rate_index,expected_unique_id",[
  (1, 0, None),
  (2, 0, "Off Peak"),
  (2, 1, "Peak"),
  (2, 2, None),
  (3, 0, "Off Peak"),
  (3, 1, "Standard"),
  (3, 2, "Peak"),
  (3, 3, None),
  (4, 0, None)
])
async def test_when_called_then_correct_name_returned(total_unique_rates: int, unique_rate_index: int, expected_unique_id: str):
  # Act
  result = get_peak_name(total_unique_rates, unique_rate_index)

  # Assert
  assert result == expected_unique_id