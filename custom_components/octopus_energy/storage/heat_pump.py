import logging
from homeassistant.helpers import storage

from ..api_client.heat_pump import HeatPumpResponse

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_heat_pump(hass, account_id: str, euid: str) -> HeatPumpResponse:
  store = storage.Store(hass, "2", f"octopus_energy.{account_id}_{euid}_heat_pump")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached heat pump data for {account_id}/{euid}")
      return HeatPumpResponse.parse_obj(data)
  except:
    return None
  
async def async_save_cached_heat_pump(hass, account_id: str, euid: str, heat_pump: HeatPumpResponse):
  if heat_pump is not None:
    store = storage.Store(hass, "2", f"octopus_energy.{account_id}_{euid}_heat_pump")
    await store.async_save(heat_pump.dict())
    _LOGGER.debug(f"Saved heat pump data for {account_id}/{euid}")
