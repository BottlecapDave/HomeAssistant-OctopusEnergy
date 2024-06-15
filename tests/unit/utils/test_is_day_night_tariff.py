import pytest

from custom_components.octopus_energy.utils import is_day_night_tariff

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff_code,expected_result",[
  ("E-1R-AGILE-FLEX-22-11-25-B", False),
  ("BUS-PANELP-12M-FIXED-SEPTEMBER2029", False),
  ("E-2R-VAR-22-11-01-A", True),
  ("E-FLAT2R-SILVER-23-12-06-A", True),
])
async def test_when_tariff_code_provided_then_expected_result_returned(tariff_code: str, expected_result: bool):
  # Act
  assert is_day_night_tariff(tariff_code) == expected_result