from typing import Optional
import pytest

from custom_components.octopus_energy.heat_pump import calculate_battery_percentage

@pytest.mark.parametrize(
  "voltage, expected_percentage",
  [
    (None, None),
    (2.0, 0),
    (2.1, 10),
    (2.2, 20),
    (2.3, 30),
    (2.4, 40),
    (2.5, 50),
    (2.6, 60),
    (2.7, 70),
    (2.8, 80),
    (2.9, 90),
    (3.0, 100),
    (1.5, 0),  # Below minimum voltage
    (3.5, 100) # Above maximum voltage
   ]
)
def test_when_voltage_then_expected_percentage_provided(voltage: Optional[float], expected_percentage: Optional[float]):
  assert calculate_battery_percentage(voltage) == expected_percentage