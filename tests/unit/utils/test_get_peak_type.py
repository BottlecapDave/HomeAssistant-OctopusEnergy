import pytest

from custom_components.octopus_energy.utils.rate_information import get_peak_type

@pytest.mark.asyncio
@pytest.mark.parametrize("total_unique_rates,unique_rate_index,expected_unique_id",[
  (1, 0, None),
  (2, 0, "off_peak"),
  (2, 1, "peak"),
  (2, 2, None),
  (3, 0, "off_peak"),
  (3, 1, "standard"),
  (3, 2, "peak"),
  (3, 3, None),
  (4, 0, None)
])
async def test_when_called_then_correct_peak_type_returned(total_unique_rates: list, unique_rate_index: int, expected_unique_id: str):
  # Act
  result = get_peak_type(total_unique_rates, unique_rate_index)

  # Assert
  assert result == expected_unique_id