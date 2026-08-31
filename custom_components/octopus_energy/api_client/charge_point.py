from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


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
