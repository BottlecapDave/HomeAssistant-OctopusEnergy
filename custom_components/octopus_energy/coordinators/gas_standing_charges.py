import logging
from datetime import datetime, timedelta
from custom_components.octopus_energy.coordinators import get_gas_meter_tariff_code

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_GAS_STANDING_CHARGE_KEY,
  DOMAIN,
  DATA_CLIENT,
  DATA_ACCOUNT,
)

from ..api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

class GasStandingChargeCoordinatorResult:
  last_retrieved: datetime
  standing_charge: {}

  def __init__(self, last_retrieved: datetime, standing_charge: {}):
    self.last_retrieved = last_retrieved
    self.standing_charge = standing_charge

async def async_refresh_gas_standing_charges_data(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_info,
    target_mprn: str,
    target_serial_number: str,
    existing_standing_charges_result: GasStandingChargeCoordinatorResult
  ):
  period_from = as_utc(current.replace(hour=0, minute=0, second=0, microsecond=0))
  period_to = period_from + timedelta(days=1)

  if (account_info is not None):
    tariff_code = get_gas_meter_tariff_code(current, account_info, target_mprn, target_serial_number)
    if tariff_code is None:
      return None
    
    new_standing_charge = None
    if ((current.minute % 30) == 0 or 
        existing_standing_charges_result is None or
        existing_standing_charges_result.standing_charge is None or
        (existing_standing_charges_result.standing_charge["start"] is not None and existing_standing_charges_result.standing_charge["start"] < period_from)):
      try:
        new_standing_charge = await client.async_get_gas_standing_charge(tariff_code, period_from, period_to)
        _LOGGER.debug(f'Gas standing charges retrieved for {target_mprn}/{target_serial_number} ({tariff_code})')
      except:
        _LOGGER.debug(f'Failed to retrieve gas standing charges for {target_mprn}/{target_serial_number} ({tariff_code})')
      
    if new_standing_charge is not None:
      return GasStandingChargeCoordinatorResult(current, new_standing_charge)
    elif (existing_standing_charges_result is not None):
      _LOGGER.debug(f"Failed to retrieve new gas standing charges for {target_mprn}/{target_serial_number} ({tariff_code}), so using cached standing charges")
  
  return existing_standing_charges_result

async def async_setup_gas_standing_charges_coordinator(hass, target_mprn: str, target_serial_number: str):
  key = DATA_GAS_STANDING_CHARGE_KEY.format(target_mprn, target_serial_number)
  
  # Reset data rates as we might have new information
  hass.data[DOMAIN][key] = None
  
  async def async_update_gas_standing_charges_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    account_info = hass.data[DOMAIN][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN] else None
    standing_charges: GasStandingChargeCoordinatorResult = hass.data[DOMAIN][key] if key in hass.data[DOMAIN] else None

    hass.data[DOMAIN][key] = await async_refresh_gas_standing_charges_data(
      current,
      client,
      account_info,
      target_mprn,
      target_serial_number,
      standing_charges,
    )

    return hass.data[DOMAIN][key]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=key,
    update_method=async_update_gas_standing_charges_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  await coordinator.async_config_entry_first_refresh()

  return coordinator