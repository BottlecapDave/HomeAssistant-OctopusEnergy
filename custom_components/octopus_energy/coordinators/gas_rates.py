import logging
from datetime import datetime, timedelta
from typing import Callable, Any

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)
from homeassistant.helpers import issue_registry as ir

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DATA_ACCOUNT_COORDINATOR,
  DOMAIN,
  DATA_GAS_RATES_KEY,
  DATA_ACCOUNT,
  EVENT_GAS_CURRENT_DAY_RATES,
  EVENT_GAS_NEXT_DAY_RATES,
  EVENT_GAS_PREVIOUS_DAY_RATES,
  REFRESH_RATE_IN_MINUTES_RATES,
  REPAIR_NO_ACTIVE_TARIFF,
)

from ..api_client import ApiException, OctopusEnergyApiClient
from ..utils import private_rates_to_public_rates
from . import BaseCoordinatorResult, combine_rates, get_gas_meter_tariff, raise_rate_events

_LOGGER = logging.getLogger(__name__)

class GasRatesCoordinatorResult(BaseCoordinatorResult):
  rates: list

  def __init__(self, last_evaluated: datetime, request_attempts: int, rates: list, last_retrieved: datetime | None = None, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_RATES, last_retrieved, last_error)
    self.rates = rates

async def async_refresh_gas_rates_data(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_info,
    target_mprn: str,
    target_serial_number: str,
    existing_rates_result: GasRatesCoordinatorResult,
    fire_event: Callable[[str, "dict[str, Any]"], None],
    raise_no_active_rate: Callable[[], None] = None,
    remove_no_active_rate: Callable[[], None] = None
  ) -> GasRatesCoordinatorResult: 
  if (account_info is not None):
    period_from = as_utc((current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = as_utc((current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0))

    tariff = get_gas_meter_tariff(current, account_info, target_mprn, target_serial_number)
    if tariff is None:
      if raise_no_active_rate is not None:
        await raise_no_active_rate()
      return None
    elif remove_no_active_rate is not None:
      await remove_no_active_rate()

    new_rates = None
    raised_exception = None
    if (existing_rates_result is None or current >= existing_rates_result.next_refresh):
      adjusted_period_from = period_from
      is_new_tariff = True
      if existing_rates_result is not None and existing_rates_result.rates is not None and len(existing_rates_result.rates) > 0:
        is_new_tariff = existing_rates_result.rates[-1]["tariff_code"] != tariff.code
        if is_new_tariff == False:
          adjusted_period_from = existing_rates_result.rates[-1]["end"]

      last_retrieved = None
      if adjusted_period_from < period_to:
        try:
          new_rates = await client.async_get_gas_rates(tariff.product, tariff.code, adjusted_period_from, period_to)
        except Exception as e:
          if isinstance(e, ApiException) == False:
            raise
          
          raised_exception = e
          _LOGGER.debug(f'Failed to retrieve gas rates for {target_mprn}/{target_serial_number} ({tariff.code})')
        
        new_rates = combine_rates(existing_rates_result.rates if existing_rates_result is not None and is_new_tariff == False else [], new_rates, period_from, period_to)
      else:
        _LOGGER.info('All required rates present, so using cached rates')
        new_rates = existing_rates_result.rates
        last_retrieved = existing_rates_result.last_retrieved

      # Make sure our rate information doesn't contain any negative values https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/506
      if new_rates is not None:
        for rate in new_rates:
          if rate["value_inc_vat"] < 0:
            new_rates = None
            break
        
      if new_rates is not None:
        _LOGGER.debug(f'Gas rates retrieved for {target_mprn}/{target_serial_number} ({tariff.code});')

        raise_rate_events(current,
                          private_rates_to_public_rates(new_rates),
                          { "mprn": target_mprn, "serial_number": target_serial_number, "tariff_code": tariff.code },
                          fire_event,
                          EVENT_GAS_PREVIOUS_DAY_RATES,
                          EVENT_GAS_CURRENT_DAY_RATES,
                          EVENT_GAS_NEXT_DAY_RATES)
        
        return GasRatesCoordinatorResult(current, 1, new_rates, last_retrieved)

      result = None
      if (existing_rates_result is not None):
        result = GasRatesCoordinatorResult(existing_rates_result.last_evaluated, existing_rates_result.request_attempts + 1, existing_rates_result.rates, last_retrieved, last_error=raised_exception)
        
        if (result.request_attempts == 2):
          _LOGGER.warning(f"Failed to retrieve new gas rates for {target_mprn}/{target_serial_number} - using cached rates. See diagnostics sensor for more information.")
      else:
        # We want to force into our fallback mode
        result = GasRatesCoordinatorResult(current - timedelta(minutes=REFRESH_RATE_IN_MINUTES_RATES), 2, None, last_retrieved, last_error=raised_exception)
        _LOGGER.warning(f"Failed to retrieve new gas rates for {target_mprn}/{target_serial_number}. See diagnostics sensor for more information.")

      return result
  
  return existing_rates_result

async def async_raise_no_active_tariff(hass, account_id: str, mprn: str, serial_number: str):
  ir.async_create_issue(
    hass,
    DOMAIN,
    REPAIR_NO_ACTIVE_TARIFF.format(mprn, serial_number),
    is_fixable=False,
    severity=ir.IssueSeverity.ERROR,
    learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/no_active_tariff",
    translation_key="no_active_tariff",
    translation_placeholders={ "account_id": account_id, "mpan_mprn": mprn, "serial_number": serial_number, "meter_type": "Gas" }
  )

async def async_remove_no_active_tariff(hass, mprn: str, serial_number: str):
  ir.async_delete_issue(
    hass,
    DOMAIN,
    REPAIR_NO_ACTIVE_TARIFF.format(mprn, serial_number)
  )

async def async_setup_gas_rates_coordinator(hass, account_id: str, client: OctopusEnergyApiClient, target_mprn: str, target_serial_number: str):
  key = DATA_GAS_RATES_KEY.format(target_mprn, target_serial_number)

  # Reset data rates as we might have new information
  hass.data[DOMAIN][account_id][key] = None
  
  async def async_update_gas_rates_data():
    """Fetch data from API endpoint."""
    account_coordinator = hass.data[DOMAIN][account_id][DATA_ACCOUNT_COORDINATOR]
    if account_coordinator is not None:
      await account_coordinator.async_request_refresh()

    current = now()
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT] if DATA_ACCOUNT in hass.data[DOMAIN][account_id] else None
    account_info = account_result.account if account_result is not None else None
    rates = hass.data[DOMAIN][account_id][key] if key in hass.data[DOMAIN][account_id] else None

    hass.data[DOMAIN][account_id][key] = await async_refresh_gas_rates_data(
      current,
      client,
      account_info,
      target_mprn,
      target_serial_number,
      rates,
      hass.bus.async_fire,
      lambda: async_raise_no_active_tariff(hass, account_id, target_mprn, target_serial_number),
      lambda: async_remove_no_active_tariff(hass, target_mprn, target_serial_number)
    )

    return hass.data[DOMAIN][account_id][key]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=key,
    update_method=async_update_gas_rates_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )

  return coordinator