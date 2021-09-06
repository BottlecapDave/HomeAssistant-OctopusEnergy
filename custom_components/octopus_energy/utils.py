from homeassistant.util.dt import (utcnow, as_utc, parse_datetime)

def get_active_agreement(agreements):
  now = utcnow()

  for agreement in agreements:
    valid_from = as_utc(parse_datetime(agreement["valid_from"]))
    valid_to = as_utc(parse_datetime(agreement["valid_to"]))

    if valid_from <= now and valid_to >= now:
      return agreement
  
  return None
