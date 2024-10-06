from datetime import datetime

class JoinSavingSessionResponse:
  is_successful: bool
  errors: list[str]

  def __init__(
    self,
    is_successful: bool,
    errors: list[str]
  ):
    self.is_successful = is_successful
    self.errors = errors

class SavingSession:
  id: str
  code: str
  start: datetime
  end: datetime
  octopoints: int
  duration_in_minutes: int

  def __init__(
    self,
    id: str,
    code: str,
    start: datetime,
    end: datetime,
    octopoints: int
  ):
    self.id = id
    self.code = code
    self.start = start
    self.end = end
    self.octopoints = octopoints
    self.duration_in_minutes = (end - start).total_seconds() / 60

class SavingSessionsResponse:
  available_events: list[SavingSession]
  joined_events: list[SavingSession]

  def __init__(
    self,
    available_events: list[SavingSession],
    joined_events: list[SavingSession]
  ):
    self.available_events = available_events
    self.joined_events = joined_events
