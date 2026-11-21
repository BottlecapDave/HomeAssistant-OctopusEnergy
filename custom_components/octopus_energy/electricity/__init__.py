import logging

from ..utils.conversions import pence_to_pounds_pence, pence_to_pounds_pence_accurate, consumption_cost_in_pence

_LOGGER = logging.getLogger(__name__)

def __get_to(item):
    return (item["end"].timestamp(), item["end"].fold)

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_to)
  return sorted

def calculate_electricity_consumption_and_cost(
    consumption_data,
    rate_data,
    standing_charge,
    last_reset,
    minimum_consumption_records = 0,
    target_rate = None
  ):
  if (consumption_data is not None and len(consumption_data) >= minimum_consumption_records and rate_data is not None and len(rate_data) > 0 and standing_charge is not None):

    sorted_consumption_data = __sort_consumption(consumption_data)

    # Only calculate our consumption if our data has changed
    if (last_reset is None or last_reset < sorted_consumption_data[0]["start"]):

      charges = []
      total_cost_in_pence = 0
      total_consumption = 0
      missing_rates = []

      for consumption in sorted_consumption_data:
        consumption_value = consumption["consumption"]
        consumption_from = consumption["start"]
        consumption_to = consumption["end"]

        rate = next((r for r in rate_data if r["start"] == consumption_from and r["end"] == consumption_to), None)
        if rate is None:
          missing_rates.append({ "start": consumption_from, "end": consumption_to })

          # Without a rate we can't tell which peak the consumption belongs to, so only the total consumption is known
          if target_rate is None:
            total_consumption = total_consumption + consumption_value
            charges.append({
              "start": consumption_from,
              "end": consumption_to,
              "rate": None,
              "consumption": consumption_value,
              "cost": None,
              "raw_cost": None,
            })
          continue

        value = rate["value_inc_vat"]

        if target_rate is not None and value != target_rate:
          continue

        total_consumption = total_consumption + consumption_value
        cost = pence_to_pounds_pence(consumption_cost_in_pence(consumption_value, value))
        raw_cost = consumption_value * value
        total_cost_in_pence = total_cost_in_pence + raw_cost

        current_charge = {
          "start": rate["start"],
          "end": rate["end"],
          "rate": pence_to_pounds_pence_accurate(value),
          "consumption": consumption_value,
          "cost": cost,
          "raw_cost": pence_to_pounds_pence_accurate(raw_cost),
        }

        charges.append(current_charge)
      
      total_cost_in_pence_plus_standing_charge = total_cost_in_pence + standing_charge

      last_reset = sorted_consumption_data[0]["start"] if len(sorted_consumption_data) > 0 else None
      last_calculated_timestamp = sorted_consumption_data[-1]["end"] if len(sorted_consumption_data) > 0 else None

      error = None
      if len(missing_rates) > 0:
        error = f"Failed to find rates for {len(missing_rates)} consumption period(s), starting with {missing_rates[0]['start']} - {missing_rates[0]['end']}"
        _LOGGER.debug(f'{error}; costs will not be calculated')

      result = {
        "standing_charge": pence_to_pounds_pence(standing_charge),
        "total_cost_without_standing_charge": pence_to_pounds_pence(total_cost_in_pence) if error is None else None,
        "total_cost": pence_to_pounds_pence(total_cost_in_pence_plus_standing_charge) if error is None else None,
        "total_consumption": total_consumption if error is None or target_rate is None else None,
        "last_reset": last_reset,
        "last_evaluated": last_calculated_timestamp,
        "charges": charges,
        "missing_rates": missing_rates,
        "error": error,
      }

      return result
    else:
      _LOGGER.debug(f'Skipping electricity consumption and cost calculation as last reset has not changed - last_reset: {last_reset}; consumption start: {sorted_consumption_data[0]["start"]}')
  else:
    _LOGGER.debug(f'Skipping electricity consumption and cost calculation due to lack of data; consumption: {len(consumption_data) if consumption_data is not None else 0}; rates: {len(rate_data) if rate_data is not None else 0}; standing_charge: {standing_charge}')

def raise_if_rates_missing(consumption_and_cost):
  """For callers that need complete cost data, fail if any consumption period couldn't be matched to a rate"""
  if consumption_and_cost is not None and consumption_and_cost["error"] is not None:
    raise Exception(consumption_and_cost["error"])

def get_electricity_tariff_override_key(serial_number: str, mpan: str) -> str:
  return f'electricity_previous_consumption_tariff_{serial_number}_{mpan}'