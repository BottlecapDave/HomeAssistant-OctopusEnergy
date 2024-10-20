from datetime import datetime


class BaseOctoplusSession:
  code: str
  start: datetime
  end: datetime
  duration_in_minutes: int

  def __init__(
    self,
    code: str,
    start: datetime,
    end: datetime
  ):
    self.code = code
    self.start = start
    self.end = end
    self.duration_in_minutes = (end - start).total_seconds() / 60