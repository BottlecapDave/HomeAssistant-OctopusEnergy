from datetime import datetime, timedelta

from ..const import DEFAULT_REFRESH_RATE_IN_MINUTES

def calculate_next_rate(current: datetime, request_attempts: int):
  next_rate = current + timedelta(minutes=DEFAULT_REFRESH_RATE_IN_MINUTES)
  return next_rate