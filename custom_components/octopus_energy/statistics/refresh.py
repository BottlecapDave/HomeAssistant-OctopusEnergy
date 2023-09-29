from datetime import timedelta
import re
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.components import persistent_notification
from homeassistant.const import (
  ENERGY_KILO_WATT_HOUR,
  VOLUME_CUBIC_METERS
)

from homeassistant.util.dt import (now, parse_datetime)

from ..api_client import OctopusEnergyApiClient
from ..const import REGEX_DATE
from .consumption import async_import_external_statistics_from_consumption, get_electricity_consumption_statistic_name, get_electricity_consumption_statistic_unique_id, get_gas_consumption_statistic_name, get_gas_consumption_statistic_unique_id
from .cost import async_import_external_statistics_from_cost, get_electricity_cost_statistic_name, get_electricity_cost_statistic_unique_id, get_gas_cost_statistic_name, get_gas_cost_statistic_unique_id
from ..electricity import calculate_electricity_consumption_and_cost
from ..gas import calculate_gas_consumption_and_cost

async def async_refresh_previous_electricity_consumption_data(
  hass: HomeAssistant,
  client: OctopusEnergyApiClient,
  start_date: str,
  mpan: str,
  serial_number: str,
  tariff_code: str,
  is_smart_meter: bool,
  is_export: bool
):
  # Inputs from automations can include quotes, so remove these
  trimmed_date = start_date.strip('\"')
  matches = re.search(REGEX_DATE, trimmed_date)
  if matches is None:
    raise vol.Invalid(f"Date '{trimmed_date}' must match format of YYYY-MM-DD.")
  
  persistent_notification.async_create(
    hass,
    title="Consumption data refreshing started",
    message=f"Consumption data from {start_date} for electricity meter {serial_number}/{mpan} has started"
  )

  period_from = parse_datetime(f'{trimmed_date}T00:00:00Z')
  while period_from < now():
    period_to = period_from + timedelta(days=2)

    consumption_data = await client.async_get_electricity_consumption(mpan, serial_number, period_from, period_to)
    rates = await client.async_get_electricity_rates(tariff_code, is_smart_meter, period_from, period_to)

    consumption_and_cost = calculate_electricity_consumption_and_cost(
      consumption_data,
      rates,
      0,
      None,
      tariff_code
    )
  
    if consumption_and_cost is not None:
      await async_import_external_statistics_from_consumption(
        hass,
        get_electricity_consumption_statistic_unique_id(serial_number, mpan, is_export),
        get_electricity_consumption_statistic_name(serial_number, mpan, is_export),
        consumption_and_cost["charges"],
        rates,
        ENERGY_KILO_WATT_HOUR,
        "consumption"
      )

      await async_import_external_statistics_from_cost(
        hass,
        get_electricity_cost_statistic_unique_id(serial_number, mpan, is_export),
        get_electricity_cost_statistic_name(serial_number, mpan, is_export),
        consumption_and_cost["charges"],
        rates,
        "GBP",
        "consumption"
      )

    period_from = period_to

  persistent_notification.async_create(
    hass,
    title="Consumption data refreshed",
    message=f"Consumption data from {start_date} for electricity meter {serial_number}/{mpan} has finished"
  )

async def async_refresh_previous_gas_consumption_data(
  hass: HomeAssistant,
  client: OctopusEnergyApiClient,
  start_date: str,
  mprn: str,
  serial_number: str,
  tariff_code: str,
  consumption_units: str,
  calorific_value: float
):
  # Inputs from automations can include quotes, so remove these
  trimmed_date = start_date.strip('\"')
  matches = re.search(REGEX_DATE, trimmed_date)
  if matches is None:
    raise vol.Invalid(f"Date '{trimmed_date}' must match format of YYYY-MM-DD.")
  
  persistent_notification.async_create(
    hass,
    title="Consumption data refreshing started",
    message=f"Consumption data from {start_date} for gas meter {serial_number}/{mprn} has started"
  )
  
  period_from = parse_datetime(f'{trimmed_date}T00:00:00Z')
  while period_from < now():
    period_to = period_from + timedelta(days=2)

    consumption_data = await client.async_get_gas_consumption(mprn, serial_number, period_from, period_to)
    rates = await client.async_get_gas_rates(tariff_code, period_from, period_to)

    consumption_and_cost = calculate_gas_consumption_and_cost(
      consumption_data,
      rates,
      0,
      None,
      tariff_code,
      consumption_units,
      calorific_value
    )
  
    if consumption_and_cost is not None:
      await async_import_external_statistics_from_consumption(
        hass,
        get_gas_consumption_statistic_unique_id(serial_number, mprn),
        get_gas_consumption_statistic_name(serial_number, mprn),
        consumption_and_cost["charges"],
        rates,
        VOLUME_CUBIC_METERS,
        "consumption_m3",
        False
      )

      await async_import_external_statistics_from_cost(
        hass,
        get_gas_cost_statistic_unique_id(serial_number, mprn),
        get_gas_cost_statistic_name(serial_number, mprn),
        consumption_and_cost["charges"],
        rates,
        "GBP",
        "consumption_kwh",
        False
      )

    period_from = period_to

  persistent_notification.async_create(
    hass,
    title="Consumption data refreshed",
    message=f"Consumption data from {start_date} for gas meter {serial_number}/{mprn} has finished"
  )