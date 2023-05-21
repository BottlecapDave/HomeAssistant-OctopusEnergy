from datetime import datetime, timedelta
import pytest

from integration import (get_test_context)
from custom_components.octopus_energy.utils.tariff_check import check_tariff_override_valid
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
@pytest.mark.parametrize("original_tariff_code,tariff_code,expected_error_message",[
  ('E-1R-SUPER-GREEN-24M-21-07-30-A', 'G-1R-SUPER-GREEN-24M-21-07-30-A', "Energy must match 'E'"),
  ('G-1R-SUPER-GREEN-24M-21-07-30-A', 'E-1R-SUPER-GREEN-24M-21-07-30-A', "Energy must match 'G'"),
  ('E-1R-SUPER-GREEN-24M-21-07-30-A', 'E-1R-SUPER-GREEN-24M-21-07-30-B', "Region must match 'A'"),
  ('G-1R-SUPER-GREEN-24M-21-07-30-A', 'G-1R-SUPER-GREEN-24M-21-07-30-B', "Region must match 'A'"),
])
async def test_when_calculate_gas_cost_using_real_data_then_calculation_returned(original_tariff_code, tariff_code, expected_error_message):
  # Arrange
  context = get_test_context()
  client = OctopusEnergyApiClient("NOT_REAL")
  
  # Act
  result = await check_tariff_override_valid(client, original_tariff_code, tariff_code)

  # Assert
  assert result == expected_error_message