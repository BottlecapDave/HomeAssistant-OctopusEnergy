import logging
from homeassistant.helpers import storage

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_account(hass, account_id: str):
  store = storage.Store(hass, "1", f"octopus_energy.{account_id}_account")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached account data for {account_id}")
    return data
  except:
    return None
  
async def async_save_cached_account(hass, account_id: str, account_data):
  if account_data is not None:
    store = storage.Store(hass, "1", f"octopus_energy.{account_id}_account")
    await store.async_save(account_data)
    _LOGGER.debug(f"Saved account data for ({account_id})")