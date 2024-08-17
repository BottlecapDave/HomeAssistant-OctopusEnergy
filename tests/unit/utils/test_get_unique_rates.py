from datetime import datetime
import pytest

from tests.unit import create_rate_data

from custom_components.octopus_energy.utils.rate_information import get_unique_rates

@pytest.mark.asyncio
async def test_when_called_then_unique_rates_for_current_day_returned_in_order():
  period_from = datetime.strptime("2024-04-16T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2024-04-18T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2024-04-17T00:00:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  rate_data = create_rate_data(period_from, period_to, [0.4, 0.2, 0.2, 0.3, 0.1])

  rate_data.append({
    "start": datetime.strptime("2024-04-16T22:30:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    "end": datetime.strptime("2024-04-17T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    "value_inc_vat": 0.5,
    "tariff_code": "E-1R-Test-L",
    "is_capped": False
  })
  
  # Act
  result = get_unique_rates(current, rate_data)

  # Assert
  assert result is not None
  assert len(result) == 4

  assert result[0] == 0.1
  assert result[1] == 0.2
  assert result[2] == 0.3
  assert result[3] == 0.4