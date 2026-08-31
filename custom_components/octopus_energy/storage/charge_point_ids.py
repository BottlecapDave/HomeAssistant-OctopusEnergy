import logging
from homeassistant.helpers import storage

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_charge_point_ids(hass, account_id: str) -> list[str]:
  store = storage.Store(hass, "2", f"octopus_energy.{account_id}_charge_point_ids")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached charge point ids for {account_id}")
      return data.get("charge_point_ids", [])
  except:
    return []

async def async_save_cached_charge_point_ids(hass, account_id: str, charge_point_ids: list[str]):
  if charge_point_ids is not None:
    store = storage.Store(hass, "2", f"octopus_energy.{account_id}_charge_point_ids")
    await store.async_save({"charge_point_ids": charge_point_ids})
    _LOGGER.debug(f"Saved charge point ids for {account_id}")
