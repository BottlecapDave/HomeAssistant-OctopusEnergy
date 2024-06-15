import logging

from homeassistant.helpers import storage

from ..const import STORAGE_ELECTRICITY_TARIFF_OVERRIDE_NAME
from ..utils import Tariff

_LOGGER = logging.getLogger(__name__)

async def async_get_tariff_override(hass, mpan_mprn: str, serial_number: str):
  storage_key = STORAGE_ELECTRICITY_TARIFF_OVERRIDE_NAME.format(mpan_mprn, serial_number)
  store = storage.Store(hass, "1", storage_key)

  try:
    data = await store.async_load()
    if data is not None and "tariff_code" in data and "product_code" in data:
      tariff = Tariff(data["product_code"], data["tariff_code"])
      _LOGGER.info(f"Overriding tariff for {mpan_mprn}/{serial_number} with {tariff.code}")
      return tariff

  except:
    return None
  
  return None