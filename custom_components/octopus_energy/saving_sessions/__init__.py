def current_saving_sessions_event(current_date, events):
  current_event = None

  if events is not None:
    for event in events:
      if (event["start"] <= current_date and event["end"] >= current_date):
        current_event = {
            "start": event["start"],
            "end": event["end"],
            "duration_in_minutes": (event["end"] - event["start"]).total_seconds() / 60
          }
        break
  
  return current_event

def get_next_saving_sessions_event(current_date, events):
  next_event = None

  if events is not None:
    for event in events:
      if event["start"] > current_date and (next_event == None or event["start"] < next_event["start"]):
          next_event = {
            "start": event["start"],
            "end": event["end"],
            "duration_in_minutes": (event["end"] - event["start"]).total_seconds() / 60
          }

  return next_event