import logging

from homeassistant.helpers import storage

from ..const import STORAGE_TARIFF_CACHE_NAME

_LOGGER = logging.getLogger(__name__)

async def async_get_cached_tariff_total_unique_rates(hass, tariff_code: str):
  storage_key = STORAGE_TARIFF_CACHE_NAME.format(tariff_code)
  
  _LOGGER.info(f"Loading '{storage_key}'")
  store = storage.Store(hass, "2", storage_key)

  try:
    data = await store.async_load()
    if data is not None and "total_unique_rates" in data:
      total_unique_rates = data["total_unique_rates"]
      return total_unique_rates

  except:
    return None
  finally:
    _LOGGER.info(f"Loaded '{storage_key}'")
  
  return None

async def async_save_cached_tariff_total_unique_rates(hass, tariff_code: str, total_unique_rates: int):
  storage_key = STORAGE_TARIFF_CACHE_NAME.format(tariff_code)
  
  _LOGGER.info(f"Saving '{storage_key}'")
  store = storage.Store(hass, "2", storage_key)
  
  await store.async_save({
    "total_unique_rates": total_unique_rates
  })
  
  _LOGGER.info(f"Saved '{storage_key}'")