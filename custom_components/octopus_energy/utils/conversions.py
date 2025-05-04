def value_inc_vat_to_pounds(value: float):
  # We want our rates in a consistent pounds/pence but what the accuracy
  return round(value / 100, 6)

def round_pounds(value: int):
  return round(value, 2) 

def pence_to_pounds_pence(value: int):
  return round_pounds(value / 100)