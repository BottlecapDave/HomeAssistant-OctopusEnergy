import logging

from homeassistant.helpers import storage

from ..const import STORAGE_TARIFF_CACHE_NAME

_LOGGER = logging.getLogger(__name__)

async def async_get_cached_tariff_total_unique_rates(hass, tariff_code: str):
  storage_key = STORAGE_TARIFF_CACHE_NAME.format(tariff_code)
  store = storage.Store(hass, "1", storage_key)

  try:
    data = await store.async_load()
    if data is not None and "total_unique_rates" in data:
      total_unique_rates = data["total_unique_rates"]
      return total_unique_rates

  except:
    return None
  
  return None

async def async_save_cached_tariff_total_unique_rates(hass, tariff_code: str, total_unique_rates: int):
  storage_key = STORAGE_TARIFF_CACHE_NAME.format(tariff_code)
  store = storage.Store(hass, "1", storage_key)

  await store.async_save({
    "total_unique_rates": total_unique_rates
  })