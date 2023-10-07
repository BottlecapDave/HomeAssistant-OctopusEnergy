from datetime import timedelta
import logging
from typing import Callable, Any
import asyncio

from homeassistant.util.dt import (utcnow, now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,
  DATA_INTELLIGENT_DISPATCHES,
  EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES,
  EVENT_GAS_PREVIOUS_CONSUMPTION_RATES,
  MINIMUM_CONSUMPTION_DATA_LENGTH
)

from ..api_client import (OctopusEnergyApiClient)

from ..intelligent import adjust_intelligent_rates

_LOGGER = logging.getLogger(__name__)

def __get_interval_end(item):
    return item["interval_end"]

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_interval_end)
  return sorted

async def async_fetch_consumption_and_rates(
  previous_data,
  utc_now,
  client: OctopusEnergyApiClient,
  period_from,
  period_to,
  identifier: str,
  serial_number: str,
  is_electricity: bool,
  tariff_code: str,
  is_smart_meter: bool,
  fire_event: Callable[[str, "dict[str, Any]"], None],
  intelligent_dispatches = None

):
  """Fetch the previous consumption and rates"""

  if (previous_data == None or 
      ((len(previous_data["consumption"]) < 1 or 
      previous_data["consumption"][-1]["interval_end"] < period_to) and 
      utc_now.minute % 30 == 0)):
    
    _LOGGER.debug(f"Retrieving previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}...")
    
    try:
      if (is_electricity == True):

        [consumption_data, rate_data, standing_charge] = await asyncio.gather(
          client.async_get_electricity_consumption(identifier, serial_number, period_from, period_to),
          client.async_get_electricity_rates(tariff_code, is_smart_meter, period_from, period_to),
          client.async_get_electricity_standing_charge(tariff_code, period_from, period_to)
        )

        if intelligent_dispatches is not None:
          rate_data = adjust_intelligent_rates(rate_data,
                                                intelligent_dispatches["planned"] if "planned" in intelligent_dispatches else [],
                                                intelligent_dispatches["completed"] if "completed" in intelligent_dispatches else [])
          
          _LOGGER.debug(f"Tariff: {tariff_code}; dispatches: {intelligent_dispatches}")
      else:
        [consumption_data, rate_data, standing_charge] = await asyncio.gather(
          client.async_get_gas_consumption(identifier, serial_number, period_from, period_to),
          client.async_get_gas_rates(tariff_code, period_from, period_to),
          client.async_get_gas_standing_charge(tariff_code, period_from, period_to)
        )
      
      if consumption_data is not None and len(consumption_data) >= MINIMUM_CONSUMPTION_DATA_LENGTH and rate_data is not None and len(rate_data) > 0 and standing_charge is not None:
        _LOGGER.debug(f"Discovered previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}")
        consumption_data = __sort_consumption(consumption_data)

        if (is_electricity == True):
          fire_event(EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES, { "mpan": identifier, "serial_number": serial_number, "tariff_code": tariff_code, "rates": rate_data })
        else:
          fire_event(EVENT_GAS_PREVIOUS_CONSUMPTION_RATES, { "mprn": identifier, "serial_number": serial_number, "tariff_code": tariff_code, "rates": rate_data })

        _LOGGER.debug(f"Fired event for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}")

        return {
          "consumption": consumption_data,
          "rates": rate_data,
          "standing_charge": standing_charge["value_inc_vat"]
        }
      else:
        _LOGGER.debug(f"Failed to retrieve previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}; consumptions: {len(consumption_data)}; rates: {len(rate_data)}; standing_charge: {standing_charge is not None};")
    except:
      _LOGGER.debug(f"Failed to retrieve previous consumption data for {'electricity' if is_electricity else 'gas'} {identifier}/{serial_number}")

  return previous_data 

async def async_create_previous_consumption_and_rates_coordinator(
    hass,
    client: OctopusEnergyApiClient,
    identifier: str,
    serial_number: str,
    is_electricity: bool,
    tariff_code: str,
    is_smart_meter: bool,
    days_offset: int):
  """Create reading coordinator"""

  async def async_update_data():
    """Fetch data from API endpoint."""

    previous_consumption_key = f'{identifier}_{serial_number}_previous_consumption_and_rates'
    period_from = as_utc((now() - timedelta(days=days_offset)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = period_from + timedelta(days=1)
    result = await async_fetch_consumption_and_rates(
      hass.data[DOMAIN][previous_consumption_key] 
      if previous_consumption_key in hass.data[DOMAIN] and 
      "rates" in hass.data[DOMAIN][previous_consumption_key] and 
      "consumption" in hass.data[DOMAIN][previous_consumption_key] and 
      "standing_charge" in hass.data[DOMAIN][previous_consumption_key] 
      else None,
      utcnow(),
      client,
      period_from,
      period_to,
      identifier,
      serial_number,
      is_electricity,
      tariff_code,
      is_smart_meter,
      hass.bus.async_fire,
      hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES] if DATA_INTELLIGENT_DISPATCHES in hass.data[DOMAIN] else None
    )

    if (result is not None):
      hass.data[DOMAIN][previous_consumption_key] = result

    if previous_consumption_key in hass.data[DOMAIN] and "rates" in hass.data[DOMAIN][previous_consumption_key] and "consumption" in hass.data[DOMAIN][previous_consumption_key] and "standing_charge" in hass.data[DOMAIN][previous_consumption_key]:
      return hass.data[DOMAIN][previous_consumption_key] 
    else:
      return None

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"rates_{identifier}_{serial_number}",
    update_method=async_update_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  hass.data[DOMAIN][f'{identifier}_{serial_number}_previous_consumption_and_cost_coordinator'] = coordinator

  await coordinator.async_config_entry_first_refresh()

  return coordinator