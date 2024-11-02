import logging
from homeassistant.helpers import storage

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_intelligent_device(hass, account_id: str):
  store = storage.Store(hass, "1", f"octopus_energy.{account_id}_intelligent_device")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached intelligent device data for {account_id}")
    return data
  except:
    return None
  
async def async_save_cached_intelligent_device(hass, account_id: str, intelligent_device):
  store = storage.Store(hass, "1", f"octopus_energy.{account_id}_intelligent_device")
  await store.async_save(intelligent_device)
  _LOGGER.debug(f"Saved intelligent device data for ({account_id})")