from custom_components.octopus_energy.fan_club import mock_fan_club_forecast

def test_when_mock_fan_club_forecast_is_called_then_data_returned():

  # Act
  result = mock_fan_club_forecast()

  # Assert
  assert result is not None