import logging
from homeassistant.helpers import storage

from pydantic import BaseModel

from ..utils.weightings import RateWeighting

_LOGGER = logging.getLogger(__name__)

class RateWeightings(BaseModel):
  weightings: list[RateWeighting]

async def async_load_cached_rate_weightings(hass, mpan: str, serial_number: str) -> list[RateWeighting]:
  store = storage.Store(hass, "1", f"octopus_energy.{mpan}_{serial_number}_rate_weightings")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached rate weightings for {mpan}/{serial_number}")
      return RateWeightings.parse_obj(data).weightings
  except:
    return None
  
async def async_save_cached_rate_weightings(hass, mpan: str, serial_number: str, weightings: list[RateWeighting]):
  if weightings is not None:
    store = storage.Store(hass, "1", f"octopus_energy.{mpan}_{serial_number}_rate_weightings")
    await store.async_save(RateWeightings(weightings=weightings).dict())
    _LOGGER.debug(f"Saved rate weightings data for {mpan}/{serial_number}")