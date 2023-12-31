from datetime import datetime, timedelta
from ..api_client.saving_sessions import SavingSession

def current_saving_sessions_event(current_date: datetime, events: list[SavingSession]) -> SavingSession or None:
  if events is not None:
    for event in events:
      if (event.start <= current_date and event.end >= current_date):
        return event
  
  return None

def get_next_saving_sessions_event(current_date: datetime, events: list[SavingSession]) -> SavingSession or None:
  next_event = None

  if events is not None:
    for event in events:
      if event.start > current_date and (next_event == None or event.start < next_event.start):
          next_event = event

  return next_event

class SavingSessionConsumptionDate:
  start: datetime
  end: datetime

  def __init__(self, start: datetime, end: datetime):
    self.start = start
    self.end = end

def is_new_saving_session_date_valid(saving_session_start: datetime, previous_saving_sessions: list):
  start_of_day = saving_session_start.replace(hour=0, minute=0, second=0, microsecond=0)
  end_of_day = start_of_day + timedelta(days=1)
  for saving_session in previous_saving_sessions:
    if saving_session["start"] >= start_of_day and saving_session["start"] <= end_of_day:
      return False
  
  return True

def get_saving_session_consumption_dates(saving_session_start: datetime, saving_session_end: datetime, previous_saving_sessions: list) -> list[SavingSessionConsumptionDate]:
  dates: list[SavingSessionConsumptionDate] = []

  hours = saving_session_end - saving_session_start
  saving_session_day = saving_session_start.weekday()
  if (saving_session_day >= 5):
    # Weekend
    new_start = saving_session_start
    while len(dates) < 4:
      new_start = new_start - timedelta(days=1)
      if (is_new_saving_session_date_valid(new_start, previous_saving_sessions) and new_start.weekday() >= 5):
        dates.append(SavingSessionConsumptionDate(new_start, new_start + hours))
  else:
    # Weekday
    new_start = saving_session_start
    while len(dates) < 10:
      new_start = new_start - timedelta(days=1)
      if (is_new_saving_session_date_valid(new_start, previous_saving_sessions) and new_start.weekday() < 5):
        dates.append(SavingSessionConsumptionDate(new_start, new_start + hours))

  return dates