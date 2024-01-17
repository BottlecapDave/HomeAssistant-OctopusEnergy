import logging
from datetime import datetime, timedelta

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
  REFRESH_RATE_IN_MINUTES_STANDING_CHARGE,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from . import BaseCoordinatorResult, get_gas_meter_tariff_code

_LOGGER = logging.getLogger(__name__)

class GasStandingChargeCoordinatorResult(BaseCoordinatorResult):
  standing_charge: {}

  def __init__(self, last_retrieved: datetime, request_attempts: int, standing_charge: {}):
    super().__init__(last_retrieved, request_attempts, REFRESH_RATE_IN_MINUTES_STANDING_CHARGE)
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
    if (existing_standing_charges_result is None or current >= existing_standing_charges_result.next_refresh):
      try:
        new_standing_charge = await client.async_get_gas_standing_charge(tariff_code, period_from, period_to)
        _LOGGER.debug(f'Gas standing charges retrieved for {target_mprn}/{target_serial_number} ({tariff_code})')
      except Exception as e:
        if isinstance(e, ApiException) == False:
          raise
        
        _LOGGER.debug(f'Failed to retrieve gas standing charges for {target_mprn}/{target_serial_number} ({tariff_code})')
      
      if new_standing_charge is not None:
        return GasStandingChargeCoordinatorResult(current, 1, new_standing_charge)
      
      result = None
      if (existing_standing_charges_result is not None):
        result = GasStandingChargeCoordinatorResult(existing_standing_charges_result.last_retrieved, existing_standing_charges_result.request_attempts + 1, existing_standing_charges_result.standing_charge)
        _LOGGER.warning(f"Failed to retrieve new gas standing charges for {target_mprn}/{target_serial_number} ({tariff_code}) - using cached standing charges. Next attempt at {result.next_refresh}")
      else:
        # We want to force into our fallback mode
        result = GasStandingChargeCoordinatorResult(current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_STANDING_CHARGE), 2, None)
        _LOGGER.warning(f"Failed to retrieve new gas standing charges for {target_mprn}/{target_serial_number} ({tariff_code}). Next attempt at {result.next_refresh}")

      return result
  
  return existing_standing_charges_result

async def async_setup_gas_standing_charges_coordinator(hass, account_id: str, target_mprn: str, target_serial_number: str):
  key = DATA_GAS_STANDING_CHARGE_KEY.format(target_mprn, target_serial_number)
  
  # Reset data rates as we might have new information
  hass.data[DOMAIN][account_id][key] = None
  
  async def async_update_gas_standing_charges_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN][account_id] else None
    account_info = account_result.account if account_result is not None else None
    standing_charges: GasStandingChargeCoordinatorResult = hass.data[DOMAIN][account_id][key] if key in hass.data[DOMAIN][account_id] else None

    hass.data[DOMAIN][account_id][key] = await async_refresh_gas_standing_charges_data(
      current,
      client,
      account_info,
      target_mprn,
      target_serial_number,
      standing_charges,
    )

    return hass.data[DOMAIN][account_id][key]

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

  return coordinator