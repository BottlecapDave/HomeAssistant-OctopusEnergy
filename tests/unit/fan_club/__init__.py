from datetime import datetime, timedelta

from custom_components.octopus_energy.fan_club import Discount

def create_discount_data(period_from: datetime, period_to: datetime, expected_discounts: list[float]) -> list[Discount]:
  discounts = []
  current_start = period_from
  current_end = None

  discount_index = 0
  while current_end is None or current_end < period_to:
    current_end = current_start + timedelta(minutes=30)

    discounts.append(Discount(start=current_start, end=current_end, discount=expected_discounts[discount_index]))

    current_start = current_end
    discount_index = discount_index + 1

    if (discount_index > (len(expected_discounts) - 1)):
      discount_index = 0

  return discounts