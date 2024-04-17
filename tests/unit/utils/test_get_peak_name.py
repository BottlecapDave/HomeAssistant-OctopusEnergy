import pytest

from custom_components.octopus_energy.utils.rate_information import get_peak_name

@pytest.mark.asyncio
@pytest.mark.parametrize("unique_rates,unique_rate_index,expected_unique_id",[
  ([1], 0, None),
  ([1, 2], 0, "Off Peak"),
  ([1, 2], 1, "Peak"),
  ([1, 2], 2, None),
  ([1, 2, 3], 0, "Off Peak"),
  ([1, 2, 3], 1, "Standard"),
  ([1, 2, 3], 2, "Peak"),
  ([1, 2, 3], 3, None),
  ([1, 2, 3, 4], 0, None)
])
async def test_when_called_then_correct_name_returned(unique_rates: list, unique_rate_index: int, expected_unique_id: str):
  # Act
  result = get_peak_name(unique_rates, unique_rate_index)

  # Assert
  assert result == expected_unique_id