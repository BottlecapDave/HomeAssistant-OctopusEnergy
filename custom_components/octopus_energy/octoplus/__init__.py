import datetime
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