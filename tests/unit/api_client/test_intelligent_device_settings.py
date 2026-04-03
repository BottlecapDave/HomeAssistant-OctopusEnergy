from datetime import time

from custom_components.octopus_energy.api_client.intelligent_device_settings import IntelligentDeviceSettings

def test_when_valid_dictionary_returned_then_it_can_be_parsed_into_intelligent_device_settings_object():
  # Arrange
  data = {
    "id": "00000000-0000-0000-0000-000000000001",
    "status": {
      "isSuspended": False
    },
    "preferences": {
      "targetType": "RELATIVE_STATE_OF_CHARGE",
      "unit": "PERCENTAGE",
      "mode": "CHARGE",
      "schedules": [
        {
          "dayOfWeek": "MONDAY",
          "time": "07:30:00",
          "min": None,
          "max": 43,
          "upperLimit": 100
        },
        {
          "dayOfWeek": "TUESDAY",
          "time": "07:30:00",
          "min": None,
          "max": 43,
          "upperLimit": 100
        },
        {
          "dayOfWeek": "WEDNESDAY",
          "time": "07:30:00",
          "min": None,
          "max": 43,
          "upperLimit": 100
        },
        {
          "dayOfWeek": "THURSDAY",
          "time": "07:30:00",
          "min": None,
          "max": 43,
          "upperLimit": 100
        },
        {
          "dayOfWeek": "FRIDAY",
          "time": "07:30:00",
          "min": None,
          "max": 43,
          "upperLimit": 100
        },
        {
          "dayOfWeek": "SATURDAY",
          "time": "07:30:00",
          "min": None,
          "max": 43,
          "upperLimit": 100
        },
        {
          "dayOfWeek": "SUNDAY",
          "time": "07:30:00",
          "min": None,
          "max": 43,
          "upperLimit": 100
        }
      ]
    }
  }

  # Act
  result = IntelligentDeviceSettings.model_validate(data)

  # Assert
  assert result is not None

  assert result.id == "00000000-0000-0000-0000-000000000001"
  assert result.status is not None
  assert result.status.isSuspended == False
  assert result.preferences is not None
  assert result.preferences.targetType == "RELATIVE_STATE_OF_CHARGE"
  assert result.preferences.unit == "PERCENTAGE"
  assert result.preferences.mode == "CHARGE"
  assert result.preferences.schedules is not None
  assert len(result.preferences.schedules) == 7
  for index in range(len(result.preferences.schedules)):
    schedule = result.preferences.schedules[index]
    if (index == 0):
      assert schedule.dayOfWeek == "MONDAY"
    elif (index == 1):
      assert schedule.dayOfWeek == "TUESDAY"
    elif (index == 2):
      assert schedule.dayOfWeek == "WEDNESDAY"
    elif (index == 3):
      assert schedule.dayOfWeek == "THURSDAY"
    elif (index == 4):
      assert schedule.dayOfWeek == "FRIDAY"
    elif (index == 5):
      assert schedule.dayOfWeek == "SATURDAY"
    elif (index == 6):
      assert schedule.dayOfWeek == "SUNDAY"

    assert schedule.time == time(7, 30, 0)
    assert schedule.min is None
    assert schedule.max == 43
    assert schedule.upperLimit == 100
  