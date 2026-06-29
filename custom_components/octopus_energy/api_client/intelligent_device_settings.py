from typing import List, Optional
from datetime import time

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

class IntelligentDeviceSettingStatus(BaseModel):
  isSuspended: bool

class IntelligentDeviceSettings(BaseModel):
  id: str
  status: IntelligentDeviceSettingStatus
  preferences: IntelligentDeviceSettingPreference