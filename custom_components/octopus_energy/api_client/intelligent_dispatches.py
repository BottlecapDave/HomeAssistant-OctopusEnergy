from datetime import datetime

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

class IntelligentDispatches:
  planned: list[IntelligentDispatchItem]
  completed: list[IntelligentDispatchItem]

  def __init__(
    self,
    planned: list[IntelligentDispatchItem],
    completed: list[IntelligentDispatchItem]
  ):
    self.planned = planned
    self.completed = completed