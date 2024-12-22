from datetime import datetime

from pydantic import BaseModel

class RateWeighting(BaseModel):
  start: datetime
  end: datetime
  weighting: float

class ValidateRateWeightingsResult:

  def __init__(self, success: bool, weightings: list[RateWeighting] = [], error_message: str | None = None):
    self.success = success
    self.weightings = weightings
    self.error_message = error_message

def validate_rate_weightings(weightings: list[dict]):
  if weightings is None or len(weightings) < 1:
    return []
  
  processed_weightings = []
  for index in range(len(weightings)):
    weighting = weightings[index]
    error = None

    start = None
    try:
      start = datetime.fromisoformat(weighting["start"])
    except:
      error = f"start was not a valid ISO datetime in string format at index {index}"
      break

    end = None
    try:
      end = datetime.fromisoformat(weighting["end"])
    except:
      error = f"end was not a valid ISO datetime in string format at index {index}"
      break

    if start >= end:
      error = f"start must be before end at index {index}"

    if (end - start).seconds != 1800: # 30 minutes
      error = f"time period must be equal to 30 minutes at index {index}"
      break

    error = _validate_time(start, "start", index)
    if error is not None:
      break

    error = _validate_time(end, "end", index)
    if error is not None:
      break

    processed_weightings.append(RateWeighting(start=start, end=end, weighting=weighting["weighting"]))

  if error is not None:
    return ValidateRateWeightingsResult(False, [], error)

  return ValidateRateWeightingsResult(True, processed_weightings)

def _validate_time(value: datetime, key: str, index: int):
  if value.minute != 0 and value.minute != 30:
    return f"{key} minute must equal 0 or 30 at index {index}"
  
  if value.second != 0 or value.microsecond != 0:
    return f"{key} second and microsecond must equal 0"
  
  return None

def merge_weightings(current_date: datetime, new_weighting: list[RateWeighting], current_weighting: list[RateWeighting]):
  merged_weightings = []
  merged_weightings.extend(new_weighting)

  for weighting in current_weighting:
    if weighting.end >= current_date:
      merged_weightings.append(weighting)

  merged_weightings.sort(key=lambda x: x.start)

  return merged_weightings

def apply_weighting(applicable_rates: list | None, rate_weightings: list[RateWeighting] | None):
  if applicable_rates is None:
    return None
  
  if rate_weightings is None:
    return applicable_rates
  
  for rate in applicable_rates:
    for session in rate_weightings:
      if rate["start"] >= session.start and rate["end"] <= session.end:
        rate["weighting"] = session.weighting

  return applicable_rates