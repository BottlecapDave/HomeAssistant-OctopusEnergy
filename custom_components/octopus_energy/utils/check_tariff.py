from homeassistant.helpers import issue_registry as ir

from ..const import (
  DOMAIN,
  DATA_KNOWN_TARIFF,
)

from ..api_client import (OctopusEnergyApiClient)

from ..utils import get_tariff_parts

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
      product = await client.async_get_product(tariff_parts["product_code"])
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