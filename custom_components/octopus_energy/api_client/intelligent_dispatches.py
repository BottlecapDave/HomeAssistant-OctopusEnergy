from datetime import datetime
from homeassistant.util.dt import (parse_datetime)

class IntelligentDispatchItem:
  start: datetime
  end: datetime
  charge_in_kwh: float
  source: str
  location: str

  def __init__(
    self,
    start: datetime,
    end: datetime,
    charge_in_kwh: float,
    source: str,
    location: str
  ):
    self.start = start
    self.end = end
    self.charge_in_kwh = charge_in_kwh
    self.source = source
    self.location = location

  def to_dict(self):
    return {
      "start": self.start,
      "end": self.end,
      "charge_in_kwh": self.charge_in_kwh,
      "source": self.source,
      "location": self.location,
    }
  
  def from_dict(data):
    return IntelligentDispatchItem(
      parse_datetime(data["start"]),
      parse_datetime(data["end"]),
      float(data["charge_in_kwh"]),
      data["source"],
      data["location"],
    )

class IntelligentDispatches:
  current_state: str | None
  planned: list[IntelligentDispatchItem]
  completed: list[IntelligentDispatchItem]

  def __init__(
    self,
    current_state: str | None,
    planned: list[IntelligentDispatchItem],
    completed: list[IntelligentDispatchItem]
  ):
    self.current_state = current_state
    self.planned = planned
    self.completed = completed

  def to_dict(self):
    return {
      "current_state": self.current_state,
      "planned": list(map(lambda x: x.to_dict(), self.planned)),
      "completed": list(map(lambda x: x.to_dict(), self.completed)),
    }
  
  def from_dict(data):
    return IntelligentDispatches(
      data["current_state"],
      list(map(lambda x: IntelligentDispatchItem.from_dict(x), data["planned"])),
      list(map(lambda x: IntelligentDispatchItem.from_dict(x), data["completed"])),
    )