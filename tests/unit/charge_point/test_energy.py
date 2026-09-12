import pytest

from custom_components.octopus_energy.charge_point.energy import integrate_energy_kwh

@pytest.mark.asyncio
async def test_when_charging_at_constant_power_then_energy_accumulates():
  # Arrange - 7kW for a realistic 5 second gap between live readings
  current_total = 10.0
  power_kw = 7.0
  elapsed_hours = 5 / 3600

  # Act
  result = integrate_energy_kwh(current_total, power_kw, elapsed_hours)

  # Assert
  assert result == round(10.0 + (7.0 * elapsed_hours), 4)

@pytest.mark.asyncio
async def test_when_charging_across_several_short_steps_then_energy_accumulates_correctly():
  # Arrange - 7kW for 30 minutes, split into 5 second steps (matches how
  # live readings actually arrive), should add 3.5kWh in total
  current_total = 10.0
  power_kw = 7.0
  elapsed_hours = 5 / 3600
  steps = int(0.5 / elapsed_hours)  # 30 minutes worth of 5 second steps

  # Act
  result = current_total
  for _ in range(steps):
    result = integrate_energy_kwh(result, power_kw, elapsed_hours)

  # Assert
  assert result == pytest.approx(13.5, abs=0.01)

@pytest.mark.asyncio
async def test_when_elapsed_hours_is_zero_then_total_unchanged():
  # Arrange
  current_total = 10.0

  # Act
  result = integrate_energy_kwh(current_total, 7.0, 0)

  # Assert
  assert result == current_total

@pytest.mark.asyncio
async def test_when_elapsed_hours_is_negative_then_total_unchanged():
  # Arrange - clock went backwards somehow
  current_total = 10.0

  # Act
  result = integrate_energy_kwh(current_total, 7.0, -0.1)

  # Assert
  assert result == current_total

@pytest.mark.asyncio
async def test_when_elapsed_hours_exceeds_max_step_then_total_unchanged():
  # Arrange - a long gap (e.g. HA restarted mid-charge) shouldn't fabricate
  # a spike of energy that was never actually measured
  current_total = 10.0

  # Act
  result = integrate_energy_kwh(current_total, 7.0, elapsed_hours=1, max_step_hours=0.1)

  # Assert
  assert result == current_total

@pytest.mark.asyncio
async def test_when_elapsed_hours_is_just_under_max_step_then_total_updated():
  # Arrange
  current_total = 10.0

  # Act
  result = integrate_energy_kwh(current_total, 7.0, elapsed_hours=0.099, max_step_hours=0.1)

  # Assert
  assert result == round(10.0 + (7.0 * 0.099), 4)

@pytest.mark.asyncio
async def test_when_power_is_zero_then_total_unchanged():
  # Arrange - not charging, no energy should accumulate
  current_total = 10.0

  # Act
  result = integrate_energy_kwh(current_total, 0, 0.5)

  # Assert
  assert result == current_total
