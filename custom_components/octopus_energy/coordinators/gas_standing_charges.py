import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  DOMAIN,
  DATA_CLIENT,
  DATA_GAS_STANDING_CHARGES,
  DATA_ACCOUNT,
)

from ..api_client import OctopusEnergyApiClient

from . import get_current_gas_agreement_tariff_codes

_LOGGER = logging.getLogger(__name__)

async def async_refresh_gas_standing_charges_data(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_info,
    existing_standing_charges: list
  ):
  if (account_info is not None):
    tariff_codes = get_current_gas_agreement_tariff_codes(current, account_info)

    period_from = as_utc(current.replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = period_from + timedelta(days=1)

    standing_charges = {}
    for ((meter_point, is_smart_meter), tariff_code) in tariff_codes.items():
      key = meter_point

      new_standing_charges = None
      if ((current.minute % 30) == 0 or 
          existing_standing_charges is None or
          key not in existing_standing_charges or
          (existing_standing_charges[key]["valid_from"] is not None and existing_standing_charges[key]["valid_from"] < period_from)):
        try:
          new_standing_charges = await client.async_get_gas_standing_charge(tariff_code, period_from, period_to)
          _LOGGER.debug(f'Gas standing charges retrieved for {tariff_code}')
        except:
          _LOGGER.debug(f'Failed to retrieve gas standing charges for {tariff_code}')
      else:
          new_standing_charges = existing_standing_charges[key]
        
      if new_standing_charges is not None:
        standing_charges[key] = new_standing_charges
      elif (existing_standing_charges is not None and key in existing_standing_charges):
        _LOGGER.debug(f"Failed to retrieve new gas standing charges for {tariff_code}, so using cached standing charges")
        standing_charges[key] = existing_standing_charges[key]

    return standing_charges
  
  return existing_standing_charges

async def async_setup_gas_standing_charges_coordinator(hass, account_id: str):
  # Reset data rates as we might have new information
  hass.data[DOMAIN][DATA_GAS_STANDING_CHARGES] = []
  
  async def async_update_gas_standing_charges_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    account_info = hass.data[DOMAIN][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN] else None
    standing_charges = hass.data[DOMAIN][DATA_GAS_STANDING_CHARGES] if DATA_GAS_STANDING_CHARGES in hass.data[DOMAIN] else {}

    hass.data[DOMAIN][DATA_GAS_STANDING_CHARGES] = await async_refresh_gas_standing_charges_data(
      current,
      client,
      account_info,
      standing_charges,
    )

    return hass.data[DOMAIN][DATA_GAS_STANDING_CHARGES]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="gas_standing_charges",
    update_method=async_update_gas_standing_charges_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )

  await coordinator.async_config_entry_first_refresh()

  return coordinator