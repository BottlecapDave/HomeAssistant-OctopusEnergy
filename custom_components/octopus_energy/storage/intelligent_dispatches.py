import logging
from homeassistant.helpers import storage

from ..api_client.intelligent_dispatches import IntelligentDispatches

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_intelligent_dispatches(hass, account_id: str) -> IntelligentDispatches | None:
  store = storage.Store(hass, "1", f"octopus_energy.{account_id}_intelligent_dispatches")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached intelligent dispatches data for {account_id}")
      return IntelligentDispatches.from_dict(data)
  except:
    return None
  
async def async_save_cached_intelligent_dispatches(hass, account_id: str, intelligent_dispatches: IntelligentDispatches):
  if intelligent_dispatches is not None:
    store = storage.Store(hass, "1", f"octopus_energy.{account_id}_intelligent_dispatches")
    await store.async_save(intelligent_dispatches.to_dict())
    _LOGGER.debug(f"Saved intelligent dispatches data for ({account_id})")