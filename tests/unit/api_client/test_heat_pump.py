from custom_components.octopus_energy.api_client.heat_pump import HeatPumpResponse

def test_when_valid_dictionary_returned_then_it_can_be_parsed_into_heat_pump_object():
  # Arrange
  data = {
    "heatPumpControllerStatus": {
      "sensors": [
        {
          "code": "ADC1",
          "connectivity": {
            "online": "true",
            "retrievedAt": "2025-05-09T17:28:51.553000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": 52.5,
            "voltage": 2.1,
            "humidityPercentage": None,
            "retrievedAt": "2025-05-09T17:28:44.152000+00:00"
          }
        },
        {
          "code": "ADC2",
          "connectivity": {
            "online": "true",
            "retrievedAt": "2025-05-09T17:28:51.554000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": -90.3,
            "humidityPercentage": None,
            "voltage": 2.0,
            "retrievedAt": "2025-05-09T17:28:44.152000+00:00"
          }
        },
        {
          "code": "ADC3",
          "connectivity": {
            "online": "true",
            "retrievedAt": "2025-05-09T17:28:51.555000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": None,
            "humidityPercentage": None,
            "voltage": None,
            "retrievedAt": None
          }
        },
        {
          "code": "ADC4",
          "connectivity": {
            "online": "true",
            "retrievedAt": "2025-05-09T17:28:51.556000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": -90.3,
            "humidityPercentage": None,
            "voltage": 2.0,
            "retrievedAt": "2025-05-09T17:28:44.152000+00:00"
          }
        },
        {
          "code": "SENSOR01",
          "connectivity": {
            "online": "true",
            "retrievedAt": "2025-05-09T17:28:51.556000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": 21.0,
            "humidityPercentage": 36.0,
            "voltage": 2.0,
            "retrievedAt": "2025-05-09T17:27:51.160000+00:00"
          }
        },
        {
          "code": "SENSOR02",
          "connectivity": {
            "online": "true",
            "retrievedAt": "2025-05-09T17:28:51.557000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": 20.8,
            "humidityPercentage": 37.0,
            "voltage": 2.0,
            "retrievedAt": "2025-05-09T17:28:39.347000+00:00"
          }
        },
        {
          "code": "SENSOR03",
          "connectivity": {
            "online": "true",
            "retrievedAt": "2025-05-09T17:28:51.570000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": 20.9,
            "humidityPercentage": 38.0,
            "voltage": 2.0,
            "retrievedAt": "2025-05-09T17:28:46.611000+00:00"
          }
        }
      ],
      "zones": [
        {
          "zone": "WATER",
          "telemetry": {
            "setpointInCelsius": -300.0,
            "mode": "AUTO",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": "2025-05-09T17:28:56.609000+00:00"
          }
        },
        {
          "zone": "ZONE_1",
          "telemetry": {
            "setpointInCelsius": 18.0,
            "mode": "AUTO",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": "2025-05-09T17:28:56.610000+00:00"
          }
        },
        {
          "zone": "ZONE_2",
          "telemetry": {
            "setpointInCelsius": 7.0,
            "mode": "OFF",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": "2025-05-09T17:28:56.611000+00:00"
          }
        },
        {
          "zone": "AUXILIARY",
          "telemetry": {
            "setpointInCelsius": 7.0,
            "mode": "OFF",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": "2025-05-09T17:28:56.612000+00:00"
          }
        }
      ]
    },
    "heatPumpControllerConfiguration": {
      "controller": {
        "state": [
          "NORMAL_MODE"
        ],
        "heatPumpTimezone": "GMT0BST,M3.5.0/1,M10.5.0",
        "connected": "true"
      },
      "heatPump": {
        "serialNumber": "00000000000002510198",
        "model": "Cosy 9",
        "hardwareVersion": "v5.1.0",
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
          "enabled": "true",
          "currentRange": {
            "minimum": {
              "value": "37",
              "unit": "DEGREES_CELSIUS"
            },
            "maximum": {
              "value": "57",
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
            "enabled": "true",
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
                "enabled": "true",
                "firmwareVersion": None,
                "boostEnabled": None
              },
              {
                "code": "ADC2",
                "displayName": "ADC2",
                "type": "NTC",
                "enabled": "true",
                "firmwareVersion": None,
                "boostEnabled": None
              },
              {
                "code": "ADC3",
                "displayName": "ADC3",
                "type": "NTC",
                "enabled": "true",
                "firmwareVersion": None,
                "boostEnabled": None
              },
              {
                "code": "ADC4",
                "displayName": "ADC4",
                "type": "NTC",
                "enabled": "true",
                "firmwareVersion": None,
                "boostEnabled": None
              }
            ]
          }
        },
        {
          "configuration": {
            "code": "ZONE_1",
            "zoneType": "HEAT",
            "enabled": "true",
            "displayName": "ZONE1",
            "primarySensor": "SENSOR01",
            "currentOperation": {
              "mode": "AUTO",
              "setpointInCelsius": 18.0,
              "action": None,
              "end": "1970-01-01T00:00:00+00:00"
            },
            "callForHeat": False,
            "heatDemand": False,
            "emergency": False,
            "sensors": [
              {
                "code": "SENSOR01",
                "displayName": "Primary",
                "type": "ZIGBEE",
                "enabled": None,
                "firmwareVersion": "0D",
                "boostEnabled": "true"
              },
              {
                "code": "SENSOR02",
                "displayName": "Upstairs",
                "type": "ZIGBEE",
                "enabled": None,
                "firmwareVersion": "0D",
                "boostEnabled": "true"
              },
              {
                "code": "SENSOR03",
                "displayName": "Nursery",
                "type": "ZIGBEE",
                "enabled": None,
                "firmwareVersion": "0D",
                "boostEnabled": "true"
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
              "setpointInCelsius": 7.0,
              "action": None,
              "end": "1970-01-01T00:00:00+00:00"
            },
            "callForHeat": False,
            "heatDemand": False,
            "emergency": "true",
            "sensors": []
          }
        },
        {
          "configuration": {
            "code": "AUXILIARY",
            "zoneType": "HEAT",
            "enabled": False,
            "displayName": "AUX",
            "primarySensor": None,
            "currentOperation": {
              "mode": "OFF",
              "setpointInCelsius": 7.0,
              "action": None,
              "end": "1970-01-01T00:00:00+00:00"
            },
            "callForHeat": False,
            "heatDemand": False,
            "emergency": "true",
            "sensors": []
          }
        }
      ]
    },
    "heatPumpLifetimePerformance": {
      "seasonalCoefficientOfPerformance": "2.985",
      "heatOutput": {
        "value": "765.599",
        "unit": "KILOWATT_HOUR"
      },
      "energyInput": {
        "value": "256.439",
        "unit": "KILOWATT_HOUR"
      },
      "readAt": "2025-05-09T18:28:51.628000+01:00"
    },
    "heatPumpTimeSeriesPerformance": [
      {
        "startAt": "2025-05-09T17:25:51+01:00",
        "endAt": "2025-05-09T17:30:51+01:00",
        "energyInput": {
          "value": "10.0",
          "unit": "KILOWATT_HOUR"
        },
        "energyOutput": {
          "value": "30.0",
          "unit": "KILOWATT_HOUR"
        },
        "outdoorTemperature": {
          "value": "15.0",
          "unit": "DEGREES_CELSIUS"
        }
      },
      {
        "startAt": "2025-05-09T17:30:51+01:00",
        "endAt": "2025-05-09T17:35:51+01:00",
        "energyInput": {
          "value": "12.0",
          "unit": "KILOWATT_HOUR"
        },
        "energyOutput": {
          "value": "35.0",
          "unit": "KILOWATT_HOUR"
        },
        "outdoorTemperature": {
          "value": "16.0",
          "unit": "DEGREES_CELSIUS"
        }
      }
    ]
  }

  # Act
  result = HeatPumpResponse.model_validate(data)

  # Assert
  assert result is not None

  assert float(result.heatPumpLifetimePerformance.seasonalCoefficientOfPerformance) == 2.985
  assert float(result.heatPumpLifetimePerformance.heatOutput.value) == 765.599
  assert float(result.heatPumpLifetimePerformance.energyInput.value) == 256.439

  assert len(result.heatPumpTimeSeriesPerformance) == 2
  assert float(result.heatPumpTimeSeriesPerformance[0].energyInput.value) == 10.0
  assert result.heatPumpTimeSeriesPerformance[0].energyInput.unit == "KILOWATT_HOUR"
  assert float(result.heatPumpTimeSeriesPerformance[0].energyOutput.value) == 30.0
  assert result.heatPumpTimeSeriesPerformance[0].energyOutput.unit == "KILOWATT_HOUR"
  assert float(result.heatPumpTimeSeriesPerformance[0].outdoorTemperature.value) == 15.0
  assert result.heatPumpTimeSeriesPerformance[0].outdoorTemperature.unit == "DEGREES_CELSIUS"
  assert result.heatPumpTimeSeriesPerformance[0].startAt == "2025-05-09T17:25:51+01:00"
  assert result.heatPumpTimeSeriesPerformance[0].endAt == "2025-05-09T17:30:51+01:00"

  assert float(result.heatPumpTimeSeriesPerformance[1].energyInput.value) == 12.0
  assert result.heatPumpTimeSeriesPerformance[1].energyInput.unit == "KILOWATT_HOUR"
  assert float(result.heatPumpTimeSeriesPerformance[1].energyOutput.value) == 35.0
  assert result.heatPumpTimeSeriesPerformance[1].energyOutput.unit == "KILOWATT_HOUR"
  assert float(result.heatPumpTimeSeriesPerformance[1].outdoorTemperature.value) == 16.0
  assert result.heatPumpTimeSeriesPerformance[1].outdoorTemperature.unit == "DEGREES_CELSIUS"
  assert result.heatPumpTimeSeriesPerformance[1].startAt == "2025-05-09T17:30:51+01:00"
  assert result.heatPumpTimeSeriesPerformance[1].endAt == "2025-05-09T17:35:51+01:00"


  
