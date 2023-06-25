import logging

from homeassistant.helpers import issue_registry as ir

from homeassistant.util.dt import (now)

from ..const import (
  DOMAIN,
  DATA_ACCOUNT,
)

from ..api_client import OctopusEnergyApiClient

from ..utils import (
  get_active_tariff_code,
  get_tariff_parts
)

from ..const import (
  DOMAIN,
  DATA_KNOWN_TARIFF,
)

_LOGGER = logging.getLogger(__name__)

async def async_check_valid_tariff(hass, client: OctopusEnergyApiClient, tariff_code: str, is_electricity: bool):
  tariff_key = f'{DATA_KNOWN_TARIFF}_{tariff_code}'
  if (tariff_key not in hass.data[DOMAIN]):
    tariff_parts = get_tariff_parts(tariff_code)
    if tariff_parts is None:
      ir.async_create_issue(
        hass,
        DOMAIN,
        f"unknown_tariff_format_{tariff_code}",
        is_fixable=False,
        severity=ir.IssueSeverity.ERROR,
        learn_more_url="https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/blob/develop/_docs/repairs/unknown_tariff_format.md",
        translation_key="unknown_tariff_format",
        translation_placeholders={ "type": "Electricity" if is_electricity else "Gas", "tariff_code": tariff_code },
      )
    else:
      try:
        _LOGGER.debug(f"Retrieving product information for '{tariff_parts.product_code}'")
        product = await client.async_get_product(tariff_parts.product_code)
        if product is None:
          ir.async_create_issue(
            hass,
            DOMAIN,
            f"unknown_tariff_{tariff_code}",
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            learn_more_url="https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/blob/develop/_docs/repairs/unknown_tariff.md",
            translation_key="unknown_tariff",
            translation_placeholders={ "type": "Electricity" if is_electricity else "Gas", "tariff_code": tariff_code },
          )
        else:
          hass.data[DOMAIN][tariff_key] = True
      except:
        _LOGGER.debug(f"Failed to retrieve product info for '{tariff_parts.product_code}'")

async def async_get_current_electricity_agreement_tariff_codes(hass, client: OctopusEnergyApiClient, account_id: str):
  account_info = hass.data[DOMAIN][DATA_ACCOUNT]

  tariff_codes = {}
  current = now()
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff_code = get_active_tariff_code(current, point["agreements"])
      # The type of meter (ie smart vs dumb) can change the tariff behaviour, so we
      # have to enumerate the different meters being used for each tariff as well.
      for meter in point["meters"]:
        is_smart_meter = meter["is_smart_meter"]
        if active_tariff_code != None:
          key = (point["mpan"], is_smart_meter)
          if key not in tariff_codes:
            tariff_codes[(point["mpan"], is_smart_meter)] = active_tariff_code
            await async_check_valid_tariff(hass, client, active_tariff_code, True)
  
  return tariff_codes