from datetime import timedelta
import logging

from homeassistant.util.dt import (utcnow, as_utc, parse_datetime)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  DOMAIN,
  
  DATA_GAS_RATES
)

from ..api_client import (OctopusEnergyApiClient)

from . import async_check_valid_tariff

_LOGGER = logging.getLogger(__name__)

async def async_create_gas_rate_coordinator(hass, client: OctopusEnergyApiClient, tariff_code: str):
  """Create gas rate coordinator"""

  async def async_update_data():
    """Fetch data from API endpoint."""
    current = utcnow()
    
    rate_key = f'{DATA_GAS_RATES}_{tariff_code}'
    period_from = as_utc(parse_datetime(current.strftime("%Y-%m-%dT00:00:00Z")))
    
    if (rate_key not in hass.data[DOMAIN] or 
        (current.minute % 30) == 0 or 
        hass.data[DOMAIN][rate_key] is None or 
        len(hass.data[DOMAIN][rate_key]) == 0 or
        hass.data[DOMAIN][rate_key][-1]["valid_from"] < period_from):
      period_to = as_utc(parse_datetime((current + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")))

      try:
        hass.data[DOMAIN][rate_key] = await client.async_get_gas_rates(tariff_code, period_from, period_to)
        await async_check_valid_tariff(hass, client, tariff_code, False)
      except:
        _LOGGER.debug('Failed to retrieve gas rates')

    return hass.data[DOMAIN][rate_key]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"gas_rates_{tariff_code}",
    update_method=async_update_data,
    update_interval=timedelta(minutes=1),
  )
  
  await coordinator.async_config_entry_first_refresh()

  return coordinator