import logging
from homeassistant.helpers import storage

from ..api_client.charge_point import ChargePointIdentity

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_charge_point_ids(hass, account_id: str) -> list[ChargePointIdentity]:
  store = storage.Store(hass, "1", f"octopus_energy.{account_id}_charge_point_ids")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached charge point ids for {account_id}")
      return [ChargePointIdentity.model_validate(item) for item in data.get("charge_point_ids", [])]
  except:
    return []

async def async_save_cached_charge_point_ids(hass, account_id: str, charge_point_ids: list[ChargePointIdentity]):
  if charge_point_ids is not None:
    store = storage.Store(hass, "1", f"octopus_energy.{account_id}_charge_point_ids")
    await store.async_save({"charge_point_ids": [item.model_dump() for item in charge_point_ids]})
    _LOGGER.debug(f"Saved charge point ids for {account_id}")
