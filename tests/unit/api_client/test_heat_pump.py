from custom_components.octopus_energy.api_client.heat_pump import HeatPumpResponse

def test_when_valid_dictionary_returned_then_it_can_be_parsed_into_heat_pump_object():
  # Arrange
  data = {
    "octoHeatPumpControllerStatus": {
      "sensors": [
        {
          "code": "ADC1",
          "connectivity": {
            "online": True,
            "retrievedAt": "2024-12-01T10:04:54.952000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": 57.4,
            "humidityPercentage": None,
            "retrievedAt": "2024-12-01T10:04:51.588000+00:00"
          }
        },
        {
          "code": "ADC2",
          "connectivity": {
            "online": True,
            "retrievedAt": "2024-12-01T10:04:54.952000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": -273.1,
            "humidityPercentage": None,
            "retrievedAt": "2024-12-01T10:04:51.588000+00:00"
          }
        },
        {
          "code": "ADC3",
          "connectivity": {
            "online": True,
            "retrievedAt": "2024-12-01T10:04:54.953000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": -273.1,
            "humidityPercentage": None,
            "retrievedAt": "2024-12-01T10:04:51.588000+00:00"
          }
        },
        {
          "code": "ADC4",
          "connectivity": {
            "online": True,
            "retrievedAt": "2024-12-01T10:04:54.953000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": -273.1,
            "humidityPercentage": None,
            "retrievedAt": "2024-12-01T10:04:51.588000+00:00"
          }
        },
        {
          "code": "SENSOR01",
          "connectivity": {
            "online": True,
            "retrievedAt": "2024-12-01T10:04:54.953000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": 19.4,
            "humidityPercentage": 57,
            "retrievedAt": "2024-12-01T10:03:15.615000+00:00"
          }
        },
        {
          "code": "SENSOR02",
          "connectivity": {
            "online": True,
            "retrievedAt": "2024-12-01T10:04:54.955000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": 22.4,
            "humidityPercentage": 54,
            "retrievedAt": "2024-12-01T10:03:54.876000+00:00"
          }
        },
        {
          "code": "SENSOR03",
          "connectivity": {
            "online": True,
            "retrievedAt": "2024-12-01T10:04:54.956000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": 22.3,
            "humidityPercentage": 60,
            "retrievedAt": "2024-12-01T10:04:27.571000+00:00"
          }
        },
        {
          "code": "SENSOR04",
          "connectivity": {
            "online": True,
            "retrievedAt": "2024-12-01T10:04:54.957000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": 22.7,
            "humidityPercentage": 46,
            "retrievedAt": "2024-12-01T10:03:12.376000+00:00"
          }
        }
      ],
      "zones": [
        {
          "zone": "WATER",
          "telemetry": {
            "setpointInCelsius": -300,
            "mode": "AUTO",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": "2024-12-01T10:04:59.116000+00:00"
          }
        },
        {
          "zone": "ZONE_1",
          "telemetry": {
            "setpointInCelsius": 22,
            "mode": "AUTO",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": "2024-12-01T10:04:59.117000+00:00"
          }
        },
        {
          "zone": "ZONE_2",
          "telemetry": {
            "setpointInCelsius": 7,
            "mode": "OFF",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": "2024-12-01T10:04:59.118000+00:00"
          }
        },
        {
          "zone": "AUXILIARY",
          "telemetry": {
            "setpointInCelsius": 7,
            "mode": "OFF",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": "2024-12-01T10:04:59.118000+00:00"
          }
        }
      ]
    },
    "octoHeatPumpControllerConfiguration": {
      "controller": {
        "state": [
          "NORMAL_MODE"
        ],
        "heatPumpTimezone": "GMT0BST,M3.5.0/1,M10.5.0",
        "connected": True
      },
      "heatPump": {
        "serialNumber": None,
        "model": "Cosy 6",
        "hardwareVersion": "v5.1.0",
        "faultCodes": [],
        "maxWaterSetpoint": 60,
        "minWaterSetpoint": 40,
        "heatingFlowTemperature": {
          "currentTemperature": {
            "value": "70",
            "unit": "DEGREES_CELSIUS"
          },
          "allowableRange": {
            "minimum": {
              "value": "30",
              "unit": "DEGREES_CELSIUS"
            },
            "maximum": {
              "value": "70",
              "unit": "DEGREES_CELSIUS"
            }
          }
        },
        "weatherCompensation": {
          "enabled": True,
          "allowableRange": {
            "minimum": {
              "value": "30",
              "unit": "DEGREES_CELSIUS"
            },
            "maximum": {
              "value": "70",
              "unit": "DEGREES_CELSIUS"
            }
          },
          "currentRange": {
            "minimum": {
              "value": "45",
              "unit": "DEGREES_CELSIUS"
            },
            "maximum": {
              "value": "55",
              "unit": "DEGREES_CELSIUS"
            }
          }
        }
      },
      "zones": [
        {
          "configuration": {
            "code": "WATER",
            "zoneType": "WATER",
            "enabled": True,
            "displayName": "WATER",
            "primarySensor": "ADC1",
            "currentOperation": {
              "mode": "AUTO",
              "setpointInCelsius": None,
              "action": "OFF",
              "end": "1970-01-01T00:00:00+00:00"
            },
            "callForHeat": False,
            "heatDemand": False,
            "emergency": False,
            "sensors": [
              {
                "code": "ADC1",
                "displayName": "ADC1",
                "type": "NTC",
                "enabled": True
              },
              {
                "code": "ADC2",
                "displayName": "ADC2",
                "type": "NTC",
                "enabled": True
              },
              {
                "code": "ADC3",
                "displayName": "ADC3",
                "type": "NTC",
                "enabled": True
              },
              {
                "code": "ADC4",
                "displayName": "ADC4",
                "type": "NTC",
                "enabled": True
              }
            ]
          }
        },
        {
          "configuration": {
            "code": "ZONE_1",
            "zoneType": "HEAT",
            "enabled": True,
            "displayName": "ZONE1",
            "primarySensor": "SENSOR03",
            "currentOperation": {
              "mode": "AUTO",
              "setpointInCelsius": 22,
              "action": None,
              "end": "1970-01-01T00:00:00+00:00"
            },
            "callForHeat": False,
            "heatDemand": False,
            "emergency": False,
            "sensors": [
              {
                "code": "SENSOR01",
                "displayName": "Hallway",
                "type": "ZIGBEE",
                "id": None,
                "firmwareVersion": "0D",
                "boostEnabled": True
              },
              {
                "code": "SENSOR02",
                "displayName": "bedoom",
                "type": "ZIGBEE",
                "id": None,
                "firmwareVersion": "0D",
                "boostEnabled": True
              },
              {
                "code": "SENSOR03",
                "displayName": "Mom and Dad",
                "type": "ZIGBEE",
                "id": None,
                "firmwareVersion": "0D",
                "boostEnabled": True
              },
              {
                "code": "SENSOR04",
                "displayName": "Lounge ",
                "type": "ZIGBEE",
                "id": None,
                "firmwareVersion": "0D",
                "boostEnabled": True
              }
            ]
          }
        },
        {
          "configuration": {
            "code": "ZONE_2",
            "zoneType": "HEAT",
            "enabled": False,
            "displayName": "ZONE2",
            "primarySensor": None,
            "currentOperation": {
              "mode": "OFF",
              "setpointInCelsius": 7,
              "action": None,
              "end": "1970-01-01T00:00:00+00:00"
            },
            "callForHeat": False,
            "heatDemand": False,
            "emergency": True,
            "sensors": []
          }
        },
        {
          "configuration": {
            "code": "AUXILIARY",
            "zoneType": "AUX",
            "enabled": False,
            "displayName": "AUX",
            "primarySensor": None,
            "currentOperation": {
              "mode": "OFF",
              "setpointInCelsius": 7,
              "action": None,
              "end": "1970-01-01T00:00:00+00:00"
            },
            "callForHeat": False,
            "heatDemand": False,
            "emergency": False,
            "sensors": []
          }
        }
      ]
    }
  }

  # Act
  result = HeatPumpResponse.parse_obj(data)

  # Assert
  assert result is not None