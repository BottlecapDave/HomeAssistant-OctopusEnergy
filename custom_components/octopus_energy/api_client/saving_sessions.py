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
  targetRegions: list[str] | None
  availability: str | None

  def __init__(
    self,
    id: str,
    code: str,
    start: datetime,
    end: datetime,
    octopoints: int,
    targetRegions: list[str] | None = None,
    availability: str | None = None
  ):
    BaseOctoplusSession.__init__(self, code, start, end)
    self.id = id
    self.octopoints = octopoints
    self.targetRegions = targetRegions
    self.availability = availability

class SavingSessionsResponse:
  available_power_down_events: list[SavingSession]
  joined_power_down_events: list[SavingSession]
  available_power_up_events: list[SavingSession]
  joined_power_up_events: list[SavingSession]
  region_id: str | None
  weekend_happy_hours: int | None

  def __init__(
    self,
    available_power_down_events: list[SavingSession],
    joined_power_down_events: list[SavingSession],
    available_power_up_events: list[SavingSession],
    joined_power_up_events: list[SavingSession],
    region: str | None,
    weekend_happy_hours: int | None = None
  ):
    self.available_power_down_events = available_power_down_events
    self.joined_power_down_events = joined_power_down_events
    self.available_power_up_events = available_power_up_events
    self.joined_power_up_events = joined_power_up_events
    self.region_id = region
    self.weekend_happy_hours = weekend_happy_hours
