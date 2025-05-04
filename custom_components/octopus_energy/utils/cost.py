def consumption_cost_in_pence(consumption: float, rate: float):
  # This is defined in https://developer.octopus.energy/rest/guides/endpoints, where consumption is rounded to 2 decimal places
  # before being multiplied by the price, which is rounded to 2 decimal places according to billing
  return round(consumption, 2) * round(rate, 2)