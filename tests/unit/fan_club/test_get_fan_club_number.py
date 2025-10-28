from custom_components.octopus_energy.fan_club import get_fan_club_number

def test_when_get_fan_club_number_called_then_correct_value_returned():
  # Act
  result = get_fan_club_number("#1 Fan: Market Weighton - Carr Farm")

  # Assert
  assert result == "#1 Fan"