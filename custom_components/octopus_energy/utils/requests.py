from datetime import datetime, timedelta

def calculate_next_rate(current: datetime, request_attempts: int, refresh_rate_in_minutes: int):
  next_rate = current + timedelta(minutes=refresh_rate_in_minutes)
  return next_rate