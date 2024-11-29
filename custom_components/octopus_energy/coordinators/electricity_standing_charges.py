import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_ELECTRICITY_STANDING_CHARGE_KEY,
  DOMAIN,
  DATA_CLIENT,
  DATA_ACCOUNT,
  REFRESH_RATE_IN_MINUTES_STANDING_CHARGE,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from . import BaseCoordinatorResult, get_electricity_meter_tariff

_LOGGER = logging.getLogger(__name__)

class ElectricityStandingChargeCoordinatorResult(BaseCoordinatorResult):
  standing_charge: {}

  def __init__(self, last_evaluated: datetime, request_attempts: int, standing_charge: dict, last_retrieved: datetime | None = None, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_STANDING_CHARGE, last_retrieved, last_error)
    self.standing_charge = standing_charge

async def async_refresh_electricity_standing_charges_data(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_info,
    target_mpan: str,
    target_serial_number: str,
    existing_standing_charges_result: ElectricityStandingChargeCoordinatorResult | None
  ):
  period_from = as_utc(current.replace(hour=0, minute=0, second=0, microsecond=0))
  period_to = period_from + timedelta(days=1)

  if (account_info is not None):
    tariff = get_electricity_meter_tariff(current, account_info, target_mpan, target_serial_number)
    if tariff is None:
      return None
    
    new_standing_charge = None
    raised_exception = None
    if (existing_standing_charges_result is None or current >= existing_standing_charges_result.next_refresh):

      _LOGGER.info(existing_standing_charges_result.standing_charge if existing_standing_charges_result is not None else None)

      last_retrieved = None
      if (existing_standing_charges_result is not None and
          existing_standing_charges_result.standing_charge is not None and
          existing_standing_charges_result.standing_charge["tariff_code"] == tariff.code and
          (existing_standing_charges_result.standing_charge["start"] is None or existing_standing_charges_result.standing_charge["start"] <= period_from) and
          (existing_standing_charges_result.standing_charge["end"] is None or existing_standing_charges_result.standing_charge["end"] >= period_to)):
        _LOGGER.info('Current standing charges cover the requested period, so using previously retrieved standing charges')
        new_standing_charge = existing_standing_charges_result.standing_charge
        last_retrieved = existing_standing_charges_result.last_retrieved
      else:
        try:
          new_standing_charge = await client.async_get_electricity_standing_charge(tariff.product, tariff.code, period_from, period_to)
          _LOGGER.debug(f'Electricity standing charges retrieved for {target_mpan}/{target_serial_number} ({tariff.code})')
        except Exception as e:
          if isinstance(e, ApiException) == False:
            raise
          
          raised_exception = e
          _LOGGER.debug(f'Failed to retrieve electricity standing charges for {target_mpan}/{target_serial_number} ({tariff.code})')
      
      if new_standing_charge is not None:
        return ElectricityStandingChargeCoordinatorResult(current, 1, new_standing_charge, last_retrieved)
      
      result = None
      if (existing_standing_charges_result is not None):
        result = ElectricityStandingChargeCoordinatorResult(existing_standing_charges_result.last_evaluated, existing_standing_charges_result.request_attempts + 1, existing_standing_charges_result.standing_charge, existing_standing_charges_result.last_retrieved, last_error=raised_exception)

        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve new electricity standing charges for {target_mpan}/{target_serial_number} ({tariff.code}) - using cached standing charges. See diagnostics sensor for more information.")
      else:
        # We want to force into our fallback mode
        result = ElectricityStandingChargeCoordinatorResult(current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_STANDING_CHARGE), 2, None, last_error=raised_exception)
        _LOGGER.warning(f"Failed to retrieve new electricity standing charges for {target_mpan}/{target_serial_number} ({tariff.code}). See diagnostics sensor for more information.")

      return result
  
  return existing_standing_charges_result

async def async_setup_electricity_standing_charges_coordinator(hass, account_id: str, target_mpan: str, target_serial_number: str):
  key = DATA_ELECTRICITY_STANDING_CHARGE_KEY.format(target_mpan, target_serial_number)
  
  # Reset data rates as we might have new information
  hass.data[DOMAIN][account_id][key] = None
  
  async def async_update_electricity_standing_charges_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN][account_id] else None
    account_info = account_result.account if account_result is not None else None
    standing_charges: ElectricityStandingChargeCoordinatorResult = hass.data[DOMAIN][account_id][key] if key in hass.data[DOMAIN][account_id] else None

    hass.data[DOMAIN][account_id][key] = await async_refresh_electricity_standing_charges_data(
      current,
      client,
      account_info,
      target_mpan,
      target_serial_number,
      standing_charges,
    )

    return hass.data[DOMAIN][account_id][key]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=key,
    update_method=async_update_electricity_standing_charges_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  return coordinator