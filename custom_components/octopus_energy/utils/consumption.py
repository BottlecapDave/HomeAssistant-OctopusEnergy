from datetime import (datetime)
import logging

from ..coordinators.current_consumption import CurrentConsumptionCoordinatorResult

_LOGGER = logging.getLogger(__name__)

def get_total_consumption(consumption: list | None):
  total_consumption = 0
  if consumption is not None:
    for item in consumption:
      total_consumption += item["consumption"]

  return total_consumption

def get_current_consumption_delta(current_datetime: datetime, current_total_consumption: float, previous_updated: datetime, previous_total_consumption: float):
  if (previous_total_consumption is None or previous_updated is None):
    return None
  
  if (current_datetime.date() == previous_updated.date()):
    return (current_total_consumption - previous_total_consumption)
  
  return current_total_consumption

class CurrentConsumption:
  def __init__(self, state: float, total_consumption: float, last_evaluated: datetime, data_last_retrieved: datetime):
    self.state = state
    self.total_consumption = total_consumption
    self.last_evaluated = last_evaluated
    self.data_last_retrieved = data_last_retrieved

def calculate_current_consumption(
  current_date: datetime,
  consumption_result: CurrentConsumptionCoordinatorResult,
  current_state: float,
  last_update: datetime,
  last_total_consumption: datetime
):
  last_evaluated = last_update
  new_state = current_state
  data_last_retrieved = consumption_result.last_retrieved if consumption_result is not None else None
  consumption_data = consumption_result.data if consumption_result is not None else None
  total_consumption = last_total_consumption

  if (consumption_data is not None):

    # We should only calculate the delta if our underlying data has updated since we last updated 
    if last_update is None or consumption_result.last_retrieved > last_update:
      total_consumption = get_total_consumption(consumption_data)
      new_state = get_current_consumption_delta(current_date,
                                                total_consumption,
                                                last_update,
                                                last_total_consumption)
      if (new_state is not None):
        last_evaluated = current_date
        data_last_retrieved = consumption_result.last_retrieved

      # Store the total consumption ready for the next run
      last_total_consumption = total_consumption

    # Reset to zero if we don't have up-to-date information 
    elif consumption_result.last_retrieved.date() != current_date.date():
      new_state = 0
      last_evaluated = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
      total_consumption = 0
    
    _LOGGER.debug(f'state: {new_state}; total_consumption: {total_consumption}; previous_total_consumption: {last_total_consumption}; consumption_data: {consumption_data}')
    
  return CurrentConsumption(new_state, total_consumption, last_evaluated, data_last_retrieved)