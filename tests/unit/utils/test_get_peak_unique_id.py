import pytest

from custom_components.octopus_energy.utils.rate_information import get_peak_unique_id

@pytest.mark.asyncio
@pytest.mark.parametrize("unique_rates,unique_rate_index,expected_unique_id",[
  ([1], 0, None),
  ([1, 2], 0, "off_peak"),
  ([1, 2], 1, "peak"),
  ([1, 2], 2, None),
  ([1, 2, 3], 0, "off_peak"),
  ([1, 2, 3], 1, "standard"),
  ([1, 2, 3], 2, "peak"),
  ([1, 2, 3], 3, None),
  ([1, 2, 3, 4], 0, None)
])
async def test_when_called_then_correct_unique_id_returned(unique_rates: list, unique_rate_index: int, expected_unique_id: str):
  # Act
  result = get_peak_unique_id(unique_rates, unique_rate_index)

  # Assert
  assert result == expected_unique_id