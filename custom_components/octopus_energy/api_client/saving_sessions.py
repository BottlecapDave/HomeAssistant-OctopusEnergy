from datetime import datetime

from .octoplus_session import BaseOctoplusSession

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

class SavingSession(BaseOctoplusSession):
  id: str
  octopoints: int

  def __init__(
    self,
    id: str,
    code: str,
    start: datetime,
    end: datetime,
    octopoints: int
  ):
    BaseOctoplusSession.__init__(self, code, start, end)
    self.id = id
    self.octopoints = octopoints

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
