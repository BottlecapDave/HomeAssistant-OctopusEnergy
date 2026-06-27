from typing import List, Optional
from datetime import time, datetime

from pydantic import BaseModel

class IntelligentDeviceSettingPreferenceSchedule(BaseModel):
  dayOfWeek: str
  time: time
  min: Optional[float]
  max: Optional[float]
  upperLimit: Optional[float]

class IntelligentDeviceSettingPreference(BaseModel):
  targetType: str
  unit: str
  mode: str
  schedules: List[IntelligentDeviceSettingPreferenceSchedule]

class DecimalReading(BaseModel):
  value: Optional[float] = None
  timestamp: Optional[datetime] = None

class IntelligentDeviceSettingStatus(BaseModel):
  isSuspended: bool
  stateOfCharge: Optional[DecimalReading] = None

class IntelligentDeviceSettings(BaseModel):
  id: str
  status: IntelligentDeviceSettingStatus
  preferences: IntelligentDeviceSettingPreference