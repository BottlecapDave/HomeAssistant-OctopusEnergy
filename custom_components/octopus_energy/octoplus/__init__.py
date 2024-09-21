from datetime import datetime, timedelta
from ..api_client.saving_sessions import SavingSession

def current_saving_sessions_event(current_date: datetime, events: list[SavingSession]) -> SavingSession | None:
  if events is not None:
    for event in events:
      if (event.start <= current_date and event.end >= current_date):
        return event
  
  return None

def get_next_saving_sessions_event(current_date: datetime, events: list[SavingSession]) -> SavingSession | None:
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

def is_new_saving_session_date_valid(saving_session_start: datetime, previous_saving_sessions: list[SavingSession]):
  start_of_day = saving_session_start.replace(hour=0, minute=0, second=0, microsecond=0)
  end_of_day = start_of_day + timedelta(days=1)
  for saving_session in previous_saving_sessions:
    if saving_session.start >= start_of_day and saving_session.start <= end_of_day:
      return False
  
  return True

def get_filtered_consumptions(consumptions: list, target_consumption_dates: list[SavingSessionConsumptionDate]):

  filtered_consumptions = []
  if target_consumption_dates is not None and consumptions is not None:
    for target_consumption_date in target_consumption_dates:
      for consumption in consumptions:
        if consumption["start"] >= target_consumption_date.start and consumption["start"] <= target_consumption_date.end and consumption["end"] >= target_consumption_date.start and consumption["end"] <= target_consumption_date.end:
          filtered_consumptions.append(consumption)
  
  return filtered_consumptions

def get_target_consumption_days(saving_session: datetime):
  saving_session_day = saving_session.weekday()
  if (saving_session_day >= 5):
    return 4
  
  return 10

def get_saving_session_weekend_dates(start: datetime, target_consumption_dates: int, hours: timedelta, previous_saving_sessions: list[SavingSession]):
  dates: list[SavingSessionConsumptionDate] = []

  new_start = start
  while len(dates) < target_consumption_dates:
    new_start = new_start - timedelta(days=1)
    if (is_new_saving_session_date_valid(new_start, previous_saving_sessions) and new_start.weekday() >= 5):
      dates.append(SavingSessionConsumptionDate(new_start, new_start + hours))
  
  return dates

def get_saving_session_weekday_dates(start: datetime, target_consumption_dates: int, hours: timedelta, previous_saving_sessions: list[SavingSession]):
  dates: list[SavingSessionConsumptionDate] = []

  new_start = start
  while len(dates) < target_consumption_dates:
    new_start = new_start - timedelta(days=1)
    if (is_new_saving_session_date_valid(new_start, previous_saving_sessions) and new_start.weekday() < 5):
      dates.append(SavingSessionConsumptionDate(new_start, new_start + hours))

  return dates

def get_saving_session_consumption_dates(saving_session: SavingSession, previous_saving_sessions: list[SavingSession]) -> list[SavingSessionConsumptionDate]:
  hours = saving_session.end - saving_session.start
  target_consumption_dates = get_target_consumption_days(saving_session.start)
  saving_session_day = saving_session.start.weekday()
  if (saving_session_day >= 5):
    return get_saving_session_weekend_dates(saving_session.start, target_consumption_dates, hours, previous_saving_sessions)
  else:
    return get_saving_session_weekday_dates(saving_session.start, target_consumption_dates, hours, previous_saving_sessions)

class SavingSessionBaseline:
  start: datetime
  end: datetime
  baseline: float
  consumption_items: list
  is_incomplete_calculation: bool

  def __init__(self, start: datetime, end: datetime, baseline: float, consumption_items: list, is_incomplete_calculation: bool):
    self.start = start
    self.end = end
    self.baseline = baseline
    self.consumption_items = consumption_items
    self.is_incomplete_calculation = is_incomplete_calculation

class SavingSessionBaselinesResult:
  current_target: SavingSessionBaseline
  total_baseline: float
  baselines: list[SavingSessionBaseline]

  def __init__(self, current_target: SavingSessionBaseline, total_baseline: float, baselines: list[SavingSessionBaseline]):
    self.current_target = current_target
    self.total_baseline = total_baseline
    self.baselines = baselines

def get_saving_session_thirty_minute_periods(saving_session: SavingSession):
  periods = []
  current = saving_session.start
  while (current < saving_session.end):
    periods.append({ "start": current, "end": current + timedelta(minutes=30)})
    current += timedelta(minutes=30)

  return periods

def get_saving_session_target(current: datetime, saving_session: SavingSession | None, consumption_data: list) -> SavingSessionBaselinesResult:
  if saving_session is None:
    return None
  
  if current > saving_session.end:
    return None

  # Split our saving session into thirty minute periods and work out which period we're within
  saving_session_periods = get_saving_session_thirty_minute_periods(saving_session)
  current_saving_session_period_index = 0
  if current > saving_session.start:
    for index in range(len(saving_session_periods)):
      if current >= saving_session_periods[index]["start"] and current <= saving_session_periods[index]["end"]:
        current_saving_session_period_index = index
        break

  target_consumption_days = get_target_consumption_days(saving_session.start)

  # Work out which consumption data is applicable for each saving session period and what our overall target is
  targets: list[SavingSessionBaseline] = []
  for saving_session_period in saving_session_periods:
    target_consumption_data = []
    for item in consumption_data:
      if item["start"].hour == saving_session_period["start"].hour and item["start"].minute == saving_session_period["start"].minute:
        target_consumption_data.append(item)

    targets.append(SavingSessionBaseline(saving_session_period["start"],
                                       saving_session_period["end"],
                                       sum(map(lambda item: item["consumption"], target_consumption_data)) / len(target_consumption_data) if len(target_consumption_data) != 0 else 0,
                                       target_consumption_data,
                                       len(target_consumption_data) != target_consumption_days))

  current_target = targets[current_saving_session_period_index]

  return SavingSessionBaselinesResult(current_target, sum(map(lambda target: target.baseline, targets)), targets)