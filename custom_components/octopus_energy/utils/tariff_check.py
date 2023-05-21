from . import get_tariff_parts
from ..api_client import (OctopusEnergyApiClient)

def is_tariff_present(root_key: str, region: str, tariff_code: str, product) -> bool:
  target_region = f'_{region}'
  if root_key in product and target_region in product[root_key]:
    first_key = next(iter(product[root_key][target_region]))
    return (first_key in product[root_key][target_region] and
            'code' in product[root_key][target_region][first_key] and
            product[root_key][target_region][first_key]['code'] == tariff_code)
  return False

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
    is_present = is_tariff_present('single_register_electricity_tariffs', tariff_parts.region, tariff_code, product)
    if is_present == False:
      is_present = is_tariff_present('dual_register_electricity_tariffs', tariff_parts.region, tariff_code, product)
      if is_present == False:
        return f"Failed to find tariff '{tariff_code}'"
  elif tariff_parts.energy == 'G':
    is_present = is_tariff_present('single_register_gas_tariffs', tariff_parts.region, tariff_code, product)
    if is_present == False:
      return f"Failed to find tariff '{tariff_code}'"
  else:
    return f"Unexpected energy '{tariff_parts.energy}'"
  
  return None
