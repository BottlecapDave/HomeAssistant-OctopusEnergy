from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


class Connectivity(BaseModel):
    online: bool
    retrievedAt: str


class Telemetry(BaseModel):
    temperatureInCelsius: float
    humidityPercentage: Optional[float]
    retrievedAt: str


class Sensor(BaseModel):
    code: str
    connectivity: Connectivity
    telemetry: Telemetry


class ZoneTelemetry(BaseModel):
    setpointInCelsius: float
    mode: str
    relaySwitchedOn: bool
    heatDemand: bool
    retrievedAt: str


class Zone(BaseModel):
    zone: str
    telemetry: ZoneTelemetry


class OctoHeatPumpControllerStatus(BaseModel):
    sensors: List[Sensor]
    zones: List[Zone]


class Controller(BaseModel):
    state: List[str]
    heatPumpTimezone: str
    connected: bool


class ValueAndUnit(BaseModel):
    value: str
    unit: str


class AllowableRange(BaseModel):
    minimum: ValueAndUnit
    maximum: ValueAndUnit


class HeatingFlowTemperature(BaseModel):
    currentTemperature: ValueAndUnit
    allowableRange: AllowableRange


class AllowableRange(BaseModel):
    minimum: ValueAndUnit
    maximum: ValueAndUnit


class WeatherCompensation(BaseModel):
    enabled: bool
    allowableRange: AllowableRange
    currentRange: AllowableRange


class HeatPump(BaseModel):
    serialNumber: Any
    model: str
    hardwareVersion: str
    faultCodes: List
    maxWaterSetpoint: int
    minWaterSetpoint: int
    heatingFlowTemperature: HeatingFlowTemperature
    weatherCompensation: WeatherCompensation


class CurrentOperation(BaseModel):
    mode: str
    setpointInCelsius: Optional[float]
    action: Optional[str]
    end: str


class SensorConfiguration(BaseModel):
    code: str
    displayName: str
    type: str
    enabled: Optional[bool] = None
    firmwareVersion: Optional[str] = None
    boostEnabled: Optional[bool] = None


class Configuration(BaseModel):
    code: str
    zoneType: str
    enabled: bool
    displayName: str
    primarySensor: Optional[str]
    currentOperation: CurrentOperation
    callForHeat: bool
    heatDemand: bool
    emergency: bool
    sensors: List[SensorConfiguration]


class ConfigurationZone(BaseModel):
    configuration: Configuration


class OctoHeatPumpControllerConfiguration(BaseModel):
    controller: Controller
    heatPump: HeatPump
    zones: List[ConfigurationZone]


class OctoHeatPumpLivePerformance(BaseModel):
    coefficientOfPerformance: str 
    heatOutput: ValueAndUnit
    powerInput: ValueAndUnit
    outdoorTemperature: ValueAndUnit
    readAt: str


class OctoHeatPumpLifetimePerformance(BaseModel):
    seasonalCoefficientOfPerformance: str
    heatOutput: ValueAndUnit
    energyInput: ValueAndUnit
    readAt: str


class HeatPumpResponse(BaseModel):
    octoHeatPumpControllerStatus: OctoHeatPumpControllerStatus
    octoHeatPumpControllerConfiguration: OctoHeatPumpControllerConfiguration
    octoHeatPumpLivePerformance: OctoHeatPumpLivePerformance
    octoHeatPumpLifetimePerformance: OctoHeatPumpLifetimePerformance
