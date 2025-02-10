import logging

from ..utils.conversions import value_inc_vat_to_pounds

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
    round_cost = True,
    target_rate = None
  ):
  if (consumption_data is not None and len(consumption_data) >= minimum_consumption_records and rate_data is not None and len(rate_data) > 0 and standing_charge is not None):

    sorted_consumption_data = __sort_consumption(consumption_data)

    # Only calculate our consumption if our data has changed
    if (last_reset is None or last_reset < sorted_consumption_data[0]["start"]):

      charges = []
      total_cost_in_pence = 0
      total_consumption = 0

      for consumption in sorted_consumption_data:
        consumption_value = consumption["consumption"]
        consumption_from = consumption["start"]
        consumption_to = consumption["end"]

        try:
          rate = next(r for r in rate_data if r["start"] == consumption_from and r["end"] == consumption_to)
        except StopIteration:
          raise Exception(f"Failed to find rate for consumption between {consumption_from} and {consumption_to}")

        value = rate["value_inc_vat"]

        if target_rate is not None and value != target_rate:
          continue

        total_consumption = total_consumption + consumption_value
        cost = (value * consumption_value)
        total_cost_in_pence = total_cost_in_pence + cost

        current_charge = {
          "start": rate["start"],
          "end": rate["end"],
          "rate": value_inc_vat_to_pounds(value),
          "consumption": consumption_value,
          "cost": round(cost / 100, 2) if round_cost else cost / 100
        }

        charges.append(current_charge)
      
      total_cost = round(total_cost_in_pence / 100, 2) if round_cost else total_cost_in_pence / 100
      total_cost_plus_standing_charge = round((total_cost_in_pence + standing_charge) / 100, 2) if round_cost else (total_cost_in_pence + standing_charge) / 100

      last_reset = sorted_consumption_data[0]["start"] if len(sorted_consumption_data) > 0 else None
      last_calculated_timestamp = sorted_consumption_data[-1]["end"] if len(sorted_consumption_data) > 0 else None

      result = {
        "standing_charge": round(standing_charge / 100, 2) if round_cost else standing_charge / 100,
        "total_cost_without_standing_charge": total_cost,
        "total_cost": total_cost_plus_standing_charge,
        "total_consumption": total_consumption,
        "last_reset": last_reset,
        "last_evaluated": last_calculated_timestamp,
        "charges": charges,
      }

      return result
    else:
      _LOGGER.debug(f'Skipping electricity consumption and cost calculation as last reset has not changed - last_reset: {last_reset}; consumption start: {sorted_consumption_data[0]["start"]}')
  else:
    _LOGGER.debug(f'Skipping electricity consumption and cost calculation due to lack of data; consumption: {len(consumption_data) if consumption_data is not None else 0}; rates: {len(rate_data) if rate_data is not None else 0}; standing_charge: {standing_charge}')

def get_electricity_tariff_override_key(serial_number: str, mpan: str) -> str:
  return f'electricity_previous_consumption_tariff_{serial_number}_{mpan}'