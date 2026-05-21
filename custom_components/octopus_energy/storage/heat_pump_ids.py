import logging
from homeassistant.helpers import storage

from ..api_client.heat_pump import HeatPumpResponse

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_heat_pump_ids(hass, account_id: str) -> list[str]:
  store = storage.Store(hass, "2", f"octopus_energy.{account_id}_heat_pump_ids")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached heat pump ids for {account_id}")
      return data.get("heat_pump_ids", [])
  except:
    return []

async def async_save_cached_heat_pump_ids(hass, account_id: str, heat_pump_ids: list[str]):
  if heat_pump_ids is not None:
    store = storage.Store(hass, "2", f"octopus_energy.{account_id}_heat_pump_ids")
    await store.async_save({"heat_pump_ids": heat_pump_ids})
    _LOGGER.debug(f"Saved heat pump ids for {account_id}")
