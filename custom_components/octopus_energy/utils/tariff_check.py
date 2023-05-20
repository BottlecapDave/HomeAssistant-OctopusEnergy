from . import get_tariff_parts
from ..api_client import (OctopusEnergyApiClient)

async def check_tariff_override_valid(client: OctopusEnergyApiClient, original_tariff_code: str, tariff_code: str):
  tariff_parts = get_tariff_parts(tariff_code)
  original_tariff_parts = get_tariff_parts(original_tariff_code)
  if tariff_parts.energy != original_tariff_parts.energy:
    return f"Energy must match '{original_tariff_parts.energy}'"
  
  if tariff_parts.region != original_tariff_parts.region:
    return f"Region must match '{original_tariff_parts.region}'"
  
  product = await client.async_get_product(tariff_parts.product_code)
  if product is None:
    return f"Failed to find owning product '{tariff_parts.product_code}'"
  
  if tariff_parts.energy == 'E':
    is_present = ('single_register_electricity_tariffs' in product and
                  f'_{tariff_parts.region}' in product['single_register_electricity_tariffs'] and
                  'direct_debit_monthly' in product['single_register_electricity_tariffs'][f'_{tariff_parts.region}'] and
                  'code' in product['single_register_electricity_tariffs'][f'_{tariff_parts.region}']['direct_debit_monthly'] and
                  product['single_register_electricity_tariffs'][f'_{tariff_parts.region}']['direct_debit_monthly']['code'] == tariff_code)
    if is_present == False:
      is_present = ('dual_register_electricity_tariffs' in product and
                  f'_{tariff_parts.region}' in product['dual_register_electricity_tariffs'] and
                  'direct_debit_monthly' in product['dual_register_electricity_tariffs'][f'_{tariff_parts.region}'] and
                  'code' in product['dual_register_electricity_tariffs'][f'_{tariff_parts.region}']['direct_debit_monthly'] and
                  product['dual_register_electricity_tariffs'][f'_{tariff_parts.region}']['direct_debit_monthly']['code'] == tariff_code)
      if is_present == False:
        return f"Failed to find tariff '{tariff_code}'"
  elif tariff_parts.energy == 'G':
    is_present = ('single_register_gas_tariffs' in product and
                  f'_{tariff_parts.region}' in product['single_register_gas_tariffs'] and
                  'direct_debit_monthly' in product['single_register_gas_tariffs'][f'_{tariff_parts.region}'] and
                  'code' in product['single_register_gas_tariffs'][f'_{tariff_parts.region}']['direct_debit_monthly'] and
                  product['single_register_gas_tariffs'][f'_{tariff_parts.region}']['direct_debit_monthly']['code'] == tariff_code)
    if is_present == False:
      return f"Failed to find tariff '{tariff_code}'"
  else:
    return f"Unexpected energy '{tariff_parts.energy}'"
  
  return None
