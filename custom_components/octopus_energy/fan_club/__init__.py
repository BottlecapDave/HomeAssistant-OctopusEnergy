from datetime import datetime, timedelta
import random

from homeassistant.util.dt import (utcnow)
from ..api_client.fan_club import FanClubResponse

def get_fan_club_number(discountSource: str):
  return discountSource.split(":")[0].strip()

def mock_fan_club_forecast():
  now: datetime = utcnow()
  now = now.replace(minute=30 if now.minute >= 30 else 0, second=0, microsecond=0)
  historic = []
  current = now
  for i in range(0, 48):
    current = current - timedelta(minutes=30)
    historic.append({
      "startAt": current.isoformat(),
      "discount": f"{random.choice([0,0.200,0.500])}"
    })

  forecast = []
  current = now
  for i in range(0, 48):
    current = current + timedelta(minutes=60)
    forecast.append({
      "startAt": current.isoformat(),
      "discount": f"{random.choice([0,0.200,0.500])}"
    })

  data = {
    "fanClubStatus": [
      {
        "discountSource": "#1 Fan: Market Weighton - Carr Farm",
        "current": {
            "startAt": now,
            "discount": "0.500"
        },
        "historic": historic,
        "forecast": {
          "baseTime": current.isoformat(),
          "data": forecast
        }
      }
    ]
  }

  return FanClubResponse.parse_obj(data)