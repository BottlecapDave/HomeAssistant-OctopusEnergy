from datetime import timedelta
import re
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.const import (
  ENERGY_KILO_WATT_HOUR
)

from homeassistant.util.dt import (now, parse_datetime)

from ..api_client import OctopusEnergyApiClient
from ..const import REGEX_DATE
from .consumption import async_import_external_statistics_from_consumption, get_electricity_consumption_statistic_name, get_electricity_consumption_statistic_unique_id
from .cost import async_import_external_statistics_from_cost, get_electricity_cost_statistic_name, get_electricity_cost_statistic_unique_id
from ..electricity import calculate_electricity_consumption_and_cost

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
      tariff_code,
      # During BST, two records are returned before the rest of the data is available
      3
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