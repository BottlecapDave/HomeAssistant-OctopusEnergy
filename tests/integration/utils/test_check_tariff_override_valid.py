from datetime import datetime, timedelta
import pytest

from integration import (get_test_context)
from custom_components.octopus_energy.utils.tariff_check import check_tariff_override_valid
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

@pytest.mark.asyncio
@pytest.mark.parametrize("original_tariff_code,tariff_code,expected_error_message",[
  ('B-1R-SUPER-GREEN-24M-21-07-30-A', 'B-1R-SUPER-GREEN-24M-21-07-30-A', "Unexpected energy 'B'"),
  ('E-1R-SUPER-GREEN-24M-21-07-30-A', 'G-1R-SUPER-GREEN-24M-21-07-30-A', "Energy must match 'E'"),
  ('G-1R-SUPER-GREEN-24M-21-07-30-A', 'E-1R-SUPER-GREEN-24M-21-07-30-A', "Energy must match 'G'"),
  ('E-1R-SUPER-GREEN-24M-21-07-30-A', 'E-1R-SUPER-GREEN-24M-21-07-30-B', "Region must match 'A'"),
  ('G-1R-SUPER-GREEN-24M-21-07-30-A', 'G-1R-SUPER-GREEN-24M-21-07-30-B', "Region must match 'A'"),
  ('E-1R-SUPER-GREEN-24M-21-07-30-A', 'E-1R-NOT-A-PRODUCT-A', "Failed to find owning product 'NOT-A-PRODUCT'"),
  ('G-1R-SUPER-GREEN-24M-21-07-30-A', 'G-1R-NOT-A-PRODUCT-A', "Failed to find owning product 'NOT-A-PRODUCT'"),
  ('E-1R-SUPER-GREEN-24M-21-07-30-A', 'E-0R-AGILE-FLEX-22-11-25-A', "Failed to find tariff 'E-0R-AGILE-FLEX-22-11-25-A'"),
  ('G-1R-SUPER-GREEN-24M-21-07-30-A', 'G-0R-VAR-21-09-29-A', "Failed to find tariff 'G-0R-VAR-21-09-29-A'"),
  ('E-1R-SUPER-GREEN-24M-21-07-30-A', 'E-1R-GO-18-06-12-A', None),
  ('E-1R-SUPER-GREEN-24M-21-07-30-A', 'E-2R-SUPER-GREEN-24M-21-07-30-A', None),
  ('E-1R-SUPER-GREEN-24M-21-07-30-A', 'E-1R-VAR-BB-23-04-01-A', None),
  ('G-1R-SUPER-GREEN-24M-21-07-30-A', 'G-1R-VAR-21-09-29-A', None),
])
async def test_when_data_provided_then_expected_error_is_returned(original_tariff_code, tariff_code, expected_error_message):
  # Arrange
  context = get_test_context()
  client = OctopusEnergyApiClient(context.api_key)
  
  # Act
  result = await check_tariff_override_valid(client, original_tariff_code, tariff_code)

  # Assert
  assert result == expected_error_message