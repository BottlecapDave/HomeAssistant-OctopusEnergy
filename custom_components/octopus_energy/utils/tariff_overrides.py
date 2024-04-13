import logging

from homeassistant.helpers import storage

from ..const import STORAGE_ELECTRICITY_TARIFF_OVERRIDE_NAME

_LOGGER = logging.getLogger(__name__)

async def async_get_tariff_override(hass, mpan_mprn: str, serial_number: str):
  storage_key = STORAGE_ELECTRICITY_TARIFF_OVERRIDE_NAME.format(mpan_mprn, serial_number)
  store = storage.Store(hass, "1", storage_key)

  try:
    data = await store.async_load()
    if data is not None and "tariff" in data:
      tariff = data["tariff"]
      _LOGGER.info(f"Overriding tariff for {mpan_mprn}/{serial_number} with {tariff}")
      return tariff

  except:
    return None
  
  return None