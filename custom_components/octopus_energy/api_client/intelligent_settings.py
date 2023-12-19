from datetime import time

class IntelligentSettings:
  smart_charge: bool
  charge_limit_weekday: int
  charge_limit_weekend: int
  ready_time_weekday: time
  ready_time_weekend: time

  def __init__(
    self,
    smart_charge: bool,
    charge_limit_weekday: int,
    charge_limit_weekend: int,
    ready_time_weekday: str,
    ready_time_weekend: str
  ):
    self.smart_charge = smart_charge
    self.charge_limit_weekday = charge_limit_weekday
    self.charge_limit_weekend = charge_limit_weekend
    self.ready_time_weekday = ready_time_weekday
    self.ready_time_weekend = ready_time_weekend