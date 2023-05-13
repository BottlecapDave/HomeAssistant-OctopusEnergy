import pytest

from custom_components.octopus_energy.utils import get_off_peak_cost

@pytest.mark.asyncio
@pytest.mark.parametrize("rates,expected_off_peak_cost",[
  ([{ "value_inc_vat": 1 }], None),
  ([{ "value_inc_vat": 1 }, { "value_inc_vat": 2 }], 1),
  ([{ "value_inc_vat": 1 }, { "value_inc_vat": 2 }, { "value_inc_vat": 3 }], None),
])
async def test_when_correct_number_of_rates_available_then_off_peak_cost_retrieved(rates, expected_off_peak_cost):
  # Act
  result = get_off_peak_cost(rates)

  # Assert
  assert result == expected_off_peak_cost