import pytest

from custom_components.octopus_energy.utils.consumption import get_total_consumption

@pytest.mark.asyncio
async def test_when_consumption_data_available_then_total_returned():
  # Arrange
  consumption = [
    {
      "consumption": 10.1
    },
    {
      "consumption": 20.5
    },
    {
      "consumption": 5.3
    }
  ]

  # Act
  total_consumption = get_total_consumption(consumption)

  # Assert
  assert total_consumption == 35.9