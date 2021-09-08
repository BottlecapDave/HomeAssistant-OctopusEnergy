from homeassistant.util.dt import (utcnow, as_utc, parse_datetime)

def get_active_agreement(agreements):
  now = utcnow()

  for agreement in agreements:
    
    valid_from = as_utc(parse_datetime(agreement["valid_from"]))
    
    valid_to = None
    if "valid_to" in agreement:
      valid_to = as_utc(parse_datetime(agreement["valid_to"]))
    
    # Some agreements have no end date, which means they are still active with no end in sight
    if valid_from <= now and (valid_to == None or valid_to >= now):
      return agreement
  
  return None