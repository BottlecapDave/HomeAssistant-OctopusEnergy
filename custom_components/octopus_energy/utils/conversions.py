from decimal import ROUND_HALF_EVEN, Decimal


def pence_to_pounds_pence_accurate(value: float):
  # We want our rates in a consistent pounds/pence but with the accuracy
  return round(value / 100, 6)

def round_pounds(value: int):
  return round(value, 2) 

def pence_to_pounds_pence(value: int):
  return round_pounds(value / 100)

def consumption_cost_in_pence(consumption: float, rate: float):
  # This is defined in https://developer.octopus.energy/rest/guides/endpoints, where consumption is rounded to 2 decimal places
  # before being multiplied by the price, which is rounded to 2 decimal places according to billing
  rounded_consumption = float(Decimal(str(consumption)).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN))
  return rounded_consumption * round(rate, 2)