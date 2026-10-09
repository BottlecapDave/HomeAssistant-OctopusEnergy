from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, field_validator


class ChargePointOnboarding(BaseModel):
  accountNumber: Any
  propertyId: Any
  onboardedAt: Optional[str] = None
  externalDeviceId: Optional[str] = None


class ChargePointConfiguration(BaseModel):
  isRandomDelayEnabled: Optional[bool] = None
  isConnected: Optional[bool] = None
  LEDBrightnessPercentage: Optional[int] = None
  isChargeCableAutoLockAvailable: Optional[bool] = None
  isChargeCableAutoLockEnabled: Optional[bool] = None
  isEcoModeEnabled: Optional[bool] = None
  isAwayMode: Optional[bool] = None


class OnboardedChargePoint(BaseModel):
  deviceUUID: str
  model: Optional[str] = None
  serialNumber: Any = None
  bluetoothLowEnergyPin: Optional[str] = None
  simcardIdentifier: Optional[str] = None
  firmwareVersion: Optional[str] = None
  controlMode: Optional[str] = None
  chargingMethod: Optional[str] = None
  operationalState: Optional[str] = None
  boostEndTime: Optional[str] = None
  onboarding: Optional[ChargePointOnboarding] = None
  configuration: Optional[ChargePointConfiguration] = None


class ChargePointScheduleSetting(BaseModel):
  start: Optional[str] = None
  end: Optional[str] = None
  action: Optional[str] = None


class ChargePointDaySchedule(BaseModel):
  day: Optional[str] = None
  chargePointScheduleSettings: list[ChargePointScheduleSetting] = []

  @field_validator("chargePointScheduleSettings", mode="before")
  @classmethod
  def _default_empty_when_null(cls, value):
    # The API may represent a day with no periods as an explicit null
    # rather than omitting the field - treat both the same way the old
    # dict-based code did (`.get(..., []) or []`).
    return [] if value is None else value


class ChargePointPowerReading(BaseModel):
  value: float
  unit: Optional[str] = None


class ChargePointIdentity(BaseModel):
  deviceUUID: str
  propertyId: str
