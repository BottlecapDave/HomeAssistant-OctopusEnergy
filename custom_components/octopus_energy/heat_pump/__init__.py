from datetime import timedelta
import random

from homeassistant.util.dt import (utcnow)

from ..api_client.heat_pump import HeatPumpResponse

def get_mock_heat_pump_id():
  return "ABC"

def mock_heat_pump_status_and_configuration():
  now = utcnow()
  data = {
    "octoHeatPumpControllerStatus": {
      "sensors": [
        {
          "code": "ADC1",
          "connectivity": {
            "online": True,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          },
          "telemetry": {
            "temperatureInCelsius": 57 + (random.randrange(1, 20) * 0.1),
            "humidityPercentage": None,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          }
        },
        {
          "code": "ADC2",
          "connectivity": {
            "online": True,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          },
          "telemetry": {
            "temperatureInCelsius": -273 + (random.randrange(1, 20) * 0.1),
            "humidityPercentage": None,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          }
        },
        {
          "code": "ADC3",
          "connectivity": {
            "online": True,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          },
          "telemetry": {
            "temperatureInCelsius": -273 + (random.randrange(1, 20) * 0.1),
            "humidityPercentage": None,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          }
        },
        {
          "code": "ADC4",
          "connectivity": {
            "online": True,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          },
          "telemetry": {
            "temperatureInCelsius": -273 + (random.randrange(1, 20) * 0.1),
            "humidityPercentage": None,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          }
        },
        {
          "code": "SENSOR01",
          "connectivity": {
            "online": True,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          },
          "telemetry": {
            "temperatureInCelsius": 18 + (random.randrange(1, 20) * 0.1),
            "humidityPercentage": 57 + (random.randrange(1, 20) * 0.1),
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          }
        },
        {
          "code": "SENSOR02",
          "connectivity": {
            "online": True,
            "retrievedAt": "2024-12-01T10:04:54.955000+00:00"
          },
          "telemetry": {
            "temperatureInCelsius": 22 + (random.randrange(1, 20) * 0.1),
            "humidityPercentage": 54 + (random.randrange(1, 20) * 0.1),
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          }
        },
        {
          "code": "SENSOR03",
          "connectivity": {
            "online": True,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          },
          "telemetry": {
            "temperatureInCelsius": 22 + (random.randrange(1, 20) * 0.1),
            "humidityPercentage": 60 + (random.randrange(1, 20) * 0.1),
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          }
        },
        {
          "code": "SENSOR04",
          "connectivity": {
            "online": True,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          },
          "telemetry": {
            "temperatureInCelsius": 22 + (random.randrange(1, 20) * 0.1),
            "humidityPercentage": 46 + (random.randrange(1, 20) * 0.1),
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
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
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          }
        },
        {
          "zone": "ZONE_1",
          "telemetry": {
            "setpointInCelsius": 22,
            "mode": "AUTO",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          }
        },
        {
          "zone": "ZONE_2",
          "telemetry": {
            "setpointInCelsius": 7,
            "mode": "OFF",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
          }
        },
        {
          "zone": "AUXILIARY",
          "telemetry": {
            "setpointInCelsius": 7,
            "mode": "OFF",
            "relaySwitchedOn": False,
            "heatDemand": False,
            "retrievedAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
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
        "serialNumber": "ABC",
        "model": "Cosy 6",
        "hardwareVersion": "v5.1.0",
        "faultCodes": [],
        "maxWaterSetpoint": 60,
        "minWaterSetpoint": 40,
        "heatingFlowTemperature": {
          "currentTemperature": {
            "value": "56",
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
    },
    "octoHeatPumpLifetimePerformance": {
      "seasonalCoefficientOfPerformance": str(3 + (random.randrange(1, 9) * 0.1)),
      "heatOutput": {
        "unit": "KILOWATT_HOUR",
        "value": str(100 + (random.randrange(1, 20) * 0.1))
      },
      "energyInput": {
        "unit": "KILOWATT_HOUR",
        "value": str(20 + (random.randrange(1, 20) * 0.1))
      },
      "readAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    },
    "octoHeatPumpLivePerformance": {
      "coefficientOfPerformance": str(3 + (random.randrange(1, 20) * 0.1)),
      "outdoorTemperature": {
        "unit": "DEGREES_CELSIUS",
        "value": str(10 + (random.randrange(1, 20) * 0.1))
      },
      "heatOutput": {
        "value": str(4 + (random.randrange(1, 9) * 0.1)),
        "unit": "KILOWATT"
      },
      "powerInput": {
        "unit": "KILOWATT",
        "value": str(1 + (random.randrange(1, 9) * 0.1))
      },
      "readAt": (now - timedelta(seconds=random.randrange(1, 120))).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    }
  }

  return HeatPumpResponse.parse_obj(data)