from datetime import datetime
from typing import Optional

from homeassistant.util.dt import (parse_datetime)
from pydantic import BaseModel

class IntelligentDispatchItem:
  start: datetime
  end: datetime
  charge_in_kwh: float | None
  source: str | None
  location: str | None

  def __init__(
    self,
    start: datetime,
    end: datetime,
    charge_in_kwh: float | None,
    source: str | None,
    location: str | None
  ):
    self.start = start
    self.end = end
    self.charge_in_kwh = charge_in_kwh
    self.source = source
    self.location = location

  def to_dict(self, ignore_none: bool = True):
    data = {
      "start": self.start,
      "end": self.end,
    }

    if self.charge_in_kwh is not None or not ignore_none:
      data["charge_in_kwh"] = self.charge_in_kwh

    if self.source is not None or not ignore_none:
      data["source"] = self.source

    if self.location is not None or not ignore_none:
      data["location"] = self.location

    return data
  
  def from_dict(data):
    return IntelligentDispatchItem(
      parse_datetime(data["start"]),
      parse_datetime(data["end"]),
      float(data["charge_in_kwh"]) if "charge_in_kwh" in data and data["charge_in_kwh"] is not None else None,
      data["source"] if "source" in data else None,
      data["location"] if "location" in data else None
    )
  
class SimpleIntelligentDispatchItem:
  start: datetime
  end: datetime

  def __init__(
    self,
    start: datetime,
    end: datetime
  ):
    self.start = start
    self.end = end

  def to_dict(self):
    return {
      "start": self.start,
      "end": self.end,
    }
  
  def from_dict(data):
    return SimpleIntelligentDispatchItem(
      parse_datetime(data["start"]),
      parse_datetime(data["end"]),
    )

class DecimalReading(BaseModel):
  value: Optional[float] = None
  timestamp: Optional[datetime] = None


class IntelligentDispatches:
  current_state: str | None
  planned: list[IntelligentDispatchItem]
  completed: list[IntelligentDispatchItem]

  # Bit of a smell this being on the API client object as it's never returned from the API
  started: list[SimpleIntelligentDispatchItem]
  state_of_charge: DecimalReading | None

  def __init__(
    self,
    current_state: str | None,
    planned: list[IntelligentDispatchItem],
    completed: list[IntelligentDispatchItem],
    started: list[SimpleIntelligentDispatchItem] = [],
    state_of_charge: DecimalReading | None = None
  ):
    self.current_state = current_state
    self.planned = planned
    self.completed = completed
    self.started = started
    self.state_of_charge = state_of_charge

  def to_dict(self):
    return {
      "current_state": self.current_state,
      "planned": list(map(lambda x: x.to_dict(True), self.planned)) if self.planned is not None else [],
      "completed": list(map(lambda x: x.to_dict(False), self.completed)) if self.completed is not None else [],
      "started": list(map(lambda x: x.to_dict(), self.started)) if self.started is not None else [],
      "state_of_charge": self.state_of_charge.model_dump() if self.state_of_charge is not None else None,
    }

  def from_dict(data):
    state_of_charge = None
    if "state_of_charge" in data and data["state_of_charge"] is not None:
      state_of_charge = DecimalReading.model_validate(data["state_of_charge"])

    return IntelligentDispatches(
      data["current_state"],
      list(map(lambda x: IntelligentDispatchItem.from_dict(x), data["planned"])),
      list(map(lambda x: IntelligentDispatchItem.from_dict(x), data["completed"])),
      list(map(lambda x: SimpleIntelligentDispatchItem.from_dict(x), data["started"] if "started" in data else [])),
      state_of_charge=state_of_charge,
    )