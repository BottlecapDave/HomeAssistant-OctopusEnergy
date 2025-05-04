from datetime import datetime, timedelta

def triangle_number(n):
  sum = 0
  for i in range(1, n + 1):
      sum += i * (i + 1) / 2
  return sum

def calculate_next_refresh(current: datetime, request_attempts: int, refresh_rate_in_minutes: float):
  # Ignore seconds and microseconds to account request taking a long time and pushing the next refresh into
  # the next request (causing an additional 1 minute wait)
  next_rate = current.replace(second=0, microsecond=0) + timedelta(minutes=refresh_rate_in_minutes)
  if (request_attempts > 1):
    i = request_attempts - 1

    # Cap at 30 minute intervals
    number_of_additional_thirty_minutes = 0
    if i > 30:
       number_of_additional_thirty_minutes = i - 30
       i = 30

    target_minutes = i * (i + 1) / 2
    next_rate = next_rate + timedelta(minutes=target_minutes)
    
    if number_of_additional_thirty_minutes > 0:
       next_rate = next_rate + timedelta(minutes=30*number_of_additional_thirty_minutes)

  return next_rate