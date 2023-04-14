from datetime import timedelta
import logging

from homeassistant.util.dt import (utcnow, now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  DOMAIN
)

from ..api_client import (OctopusEnergyApiClient)

_LOGGER = logging.getLogger(__name__)

def __get_interval_end(item):
    return item["interval_end"]

def __sort_consumption(consumption_data):
  sorted = consumption_data.copy()
  sorted.sort(key=__get_interval_end)
  return sorted

async def async_get_consumption_data(
  client: OctopusEnergyApiClient,
  previous_data,
  current_utc_timestamp,
  period_from,
  period_to,
  sensor_identifier,
  sensor_serial_number,
  is_electricity: bool
):
  if (previous_data == None or 
      ((len(previous_data) < 1 or previous_data[-1]["interval_end"] < period_to) and 
       current_utc_timestamp.minute % 30 == 0)
      ):
    if (is_electricity == True):
      data = await client.async_get_electricity_consumption(sensor_identifier, sensor_serial_number, period_from, period_to)
    else:
      data = await client.async_get_gas_consumption(sensor_identifier, sensor_serial_number, period_from, period_to)
    
    if data != None and len(data) > 0:
      data = __sort_consumption(data)
      return data
    
  if previous_data != None:
    return previous_data
  else:
    return []

async def async_create_previous_consumption_coordinator(hass, client: OctopusEnergyApiClient, is_electricity: bool, identifier: str, serial_number: str):
  """Create reading coordinator"""

  async def async_update_data():
    """Fetch data from API endpoint."""

    previous_consumption_key = f'{identifier}_{serial_number}_previous_consumption'
    previous_data = None
    if previous_consumption_key in hass.data[DOMAIN]:
      previous_data = hass.data[DOMAIN][previous_consumption_key]

    period_from = as_utc((now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = as_utc(now().replace(hour=0, minute=0, second=0, microsecond=0))

    data = await async_get_consumption_data(
      client,
      previous_data,
      utcnow(),
      period_from,
      period_to,
      identifier,
      serial_number,
      is_electricity
    )

    if data != None and len(data) > 0:
      hass.data[DOMAIN][previous_consumption_key] = data
      return data

    return []

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"rates_{identifier}_{serial_number}",
    update_method=async_update_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

  hass.data[DOMAIN][f'{identifier}_{serial_number}_previous_consumption_coordinator'] = coordinator

  await coordinator.async_config_entry_first_refresh()

  return coordinator