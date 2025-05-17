from datetime import datetime, timedelta
import random
from pydantic import BaseModel

from homeassistant.util.dt import (utcnow)
from ..api_client.fan_club import DiscountPeriod, FanClubResponse, FanClubStatusItem

class Discount(BaseModel):
    start: datetime
    end: datetime
    discount: float

class DiscountSource(BaseModel):
    source: str
    discounts: list[Discount]

def discount_period_to_discount(period: DiscountPeriod) -> Discount:
  return Discount(start=period.startAt, end=period.startAt + timedelta(minutes=30), discount=float(period.discount) * 100)

def combine_discounts(status: FanClubStatusItem) -> list[Discount]:
  discounts: list[Discount] = []

  discounts.extend(list(map(lambda x: discount_period_to_discount(x), status.historic)))
  discounts.append(discount_period_to_discount(status.current))
  for forecast in status.forecast.data:
    discounts.append(Discount(start=forecast.validTime, end=forecast.validTime + timedelta(minutes=30), discount=float(forecast.projectedDiscount) * 100))
    discounts.append(Discount(start=forecast.validTime + timedelta(minutes=30), end=forecast.validTime + timedelta(minutes=60), discount=float(forecast.projectedDiscount) * 100))

  return discounts

def get_fan_club_number(discountSource: str):
  return discountSource.split(":")[0].strip()

def mock_fan_club_forecast() -> FanClubResponse:
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
      "validTime": current.isoformat(),
      "projectedDiscount": f"{random.choice([0,0.200,0.500])}"
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

def get_current_fan_club_discount_information(discounts: list[Discount], now: datetime):
  min_target = now.replace(hour=0, minute=0, second=0, microsecond=0)
  max_target = min_target + timedelta(days=1)

  min_discount_value = None
  max_discount_value = None
  total_discount_value = 0
  total_discounts = 0
  current_discount = None

  applicable_discounts = []
  is_adding_applicable_rates = True

  if discounts is not None:
    for discount in discounts:
      if current_discount is None and len(applicable_discounts) > 0 and applicable_discounts[0].discount != discount.discount:
        applicable_discounts.clear()

      if is_adding_applicable_rates and (len(applicable_discounts) < 1 or current_discount is None or applicable_discounts[0].discount == discount.discount):
        applicable_discounts.append(discount)
      elif current_discount is not None and len(applicable_discounts) > 0 and applicable_discounts[0].discount != discount.discount:
        is_adding_applicable_rates = False
      
      if now >= discount.start and now <= discount.end:
        current_discount = discount

      if discount.start >= min_target and discount.end <= max_target:
        if min_discount_value is None or discount.discount < min_discount_value:
          min_discount_value = discount.discount

        if max_discount_value is None or discount.discount > max_discount_value:
          max_discount_value = discount.discount

        total_discount_value = total_discount_value + discount.discount
        total_discounts = total_discounts + 1

  if len(applicable_discounts) > 0 and current_discount is not None:
    return {
      "start": applicable_discounts[0].start,
      "end": applicable_discounts[-1].end,
      "discount": applicable_discounts[0].discount,
      "min_discount_today": min_discount_value,
      "max_discount_today": max_discount_value,
      "average_discount_today": total_discount_value / total_discounts
    }

  return None

def get_start(discount: Discount):
  return (discount.start.timestamp(), discount.start.fold)

def get_previous_fan_club_discount_information(discounts: list[Discount], now: datetime):
  current_discount = None
  applicable_discounts = []

  if discounts is not None:
    for period in reversed(discounts):
      if now >= period.start and now <= period.end:
        current_discount = period
        continue

      if current_discount is not None and current_discount.discount != period.discount:
        if len(applicable_discounts) == 0 or period.discount == applicable_discounts[0].discount:
          applicable_discounts.append(period)
        else:
          break
      elif len(applicable_discounts) > 0:
        break

  applicable_discounts.sort(key=get_start)

  if len(applicable_discounts) > 0 and current_discount is not None:
    return {
      "start": applicable_discounts[0].start,
      "end": applicable_discounts[-1].end,
      "discount": applicable_discounts[0].discount,
    }

  return None

def get_next_fan_club_discount_information(discounts: list[Discount], now: datetime):
  current_discount = None
  applicable_discounts = []

  if discounts is not None:
    for period in discounts:
      if now >= period.start and now <= period.end:
        current_discount = period
        continue

      if current_discount is not None and current_discount.discount != period.discount:
        if len(applicable_discounts) == 0 or period.discount == applicable_discounts[0].discount:
          applicable_discounts.append(period)
        else:
          break
      elif len(applicable_discounts) > 0:
        break

  if len(applicable_discounts) > 0 and current_discount is not None:
    return {
      "start": applicable_discounts[0].start,
      "end": applicable_discounts[-1].end,
      "discount": applicable_discounts[0].discount,
    }

  return None