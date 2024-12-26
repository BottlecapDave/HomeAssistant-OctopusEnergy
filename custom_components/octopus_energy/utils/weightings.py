from datetime import datetime, timedelta

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
    return ValidateRateWeightingsResult(True, [])
  
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

    if start.tzinfo is None:
      error = f"start must include timezone at index {index}"
      break

    end = None
    try:
      end = datetime.fromisoformat(weighting["end"])
    except:
      error = f"end was not a valid ISO datetime in string format at index {index}"
      break

    if end.tzinfo is None:
      error = f"end must include timezone at index {index}"
      break


    if start >= end:
      error = f"start must be before end at index {index}"
      break

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
    return f"{key} second and microsecond must equal 0 at index {index}"
  
  return None

def merge_weightings(current_date: datetime, new_weightings: list[RateWeighting], current_weightings: list[RateWeighting]):
  merged_weightings: list[RateWeighting] = []

  if new_weightings is not None:
    merged_weightings.extend(new_weightings)

  minimum_date = current_date - timedelta(hours=24)

  if current_weightings is not None:
    for weighting in current_weightings:
      if weighting.end >= minimum_date:
        is_present = False
        for existing_weighting in merged_weightings:
          if existing_weighting.start == weighting.start and existing_weighting.end == weighting.end:
            is_present = True
            break

        if is_present == False:
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