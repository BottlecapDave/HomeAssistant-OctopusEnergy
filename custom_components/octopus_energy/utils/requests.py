from datetime import datetime, timedelta

def triangle_number(n):
  sum = 0
  for i in range(1, n + 1):
      sum += i * (i + 1) / 2
  return sum

def calculate_next_refresh(current: datetime, request_attempts: int, refresh_rate_in_minutes: int):
  next_rate = current + timedelta(minutes=refresh_rate_in_minutes)
  if (request_attempts > 1):
    i = request_attempts - 1
    target_minutes = i * (i + 1) / 2
    next_rate = next_rate + timedelta(minutes=target_minutes)
  return next_rate