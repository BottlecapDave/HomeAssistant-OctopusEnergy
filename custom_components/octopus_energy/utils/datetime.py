import datetime


def round_down_to_nearest_half_hour(dt: datetime) -> datetime:
  """Round down a datetime to the nearest half hour."""
  if dt.minute < 30:
    return dt.replace(minute=0, second=0, microsecond=0)
  else:
    return dt.replace(minute=30, second=0, microsecond=0)
  
def round_up_to_nearest_half_hour(dt: datetime) -> datetime:
  """Round up a datetime to the nearest half hour."""
  if dt.minute == 0 and dt.second == 0 and dt.microsecond == 0:
    return dt
  if dt.minute < 30 or (dt.minute == 30 and dt.second == 0 and dt.microsecond == 0):
    return dt.replace(minute=30, second=0, microsecond=0)
  else:
    return (dt + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)