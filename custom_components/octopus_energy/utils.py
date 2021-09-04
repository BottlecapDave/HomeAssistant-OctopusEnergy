from datetime import datetime
from homeassistant.util.dt import (utcnow, as_utc)

def get_active_agreement(agreements):
  active_agreement = None
  now = utcnow()

  for agreement in agreements:
    valid_from = as_utc(datetime.fromisoformat(agreement["valid_from"]))
    valid_to = as_utc(datetime.fromisoformat(agreement["valid_to"]))

    if valid_from <= now and valid_to >= now:
      active_agreement = agreement
      break
  
  return active_agreement